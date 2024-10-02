package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

type Config struct {
	APIKey          string `json:"apiKey"`
	SensitiveAPIKey string `json:"sensitiveAPIKey"`
}

var config Config
var storagePath = "file_storage" // Relative path to file storage directory

// loadConfig reads the configuration from 'config.json' and unmarshals it into the global 'config' variable.
// Returns an error if reading or unmarshaling fails.
func loadConfig() error {
	file, err := ioutil.ReadFile("config.json")
	if err != nil {
		return err
	}

	err = json.Unmarshal(file, &config)
	if err != nil {
		return err
	}

	return nil
}

// checkMethod verifies if the HTTP request method matches the allowed method.
// Returns false and sends an error response if the method does not match.
func checkMethod(method string, allowedMethod string, w http.ResponseWriter) bool {
	if method != allowedMethod {
		http.Error(w, "[-] Method not allowed", http.StatusMethodNotAllowed)
		return false
	}
	return true
}

// checkAPIKey validates the API key provided in the request headers.
// If 'useSensitive' is true, checks for the sensitive API key; otherwise, checks for the standard API key.
// Returns false and sends an error response if the API key is invalid.
func checkAPIKey(w http.ResponseWriter, r *http.Request, useSensitive bool) bool {
	var apiKeyToCheck string
	if useSensitive {
		apiKeyToCheck = r.Header.Get("X-Sensitive-API-Key")
	} else {
		apiKeyToCheck = r.Header.Get("X-API-Key")
	}

	if apiKeyToCheck != config.APIKey && apiKeyToCheck != config.SensitiveAPIKey {
		http.Error(w, "[-] Unauthorized", http.StatusUnauthorized)
		return false
	}
	return true
}

// isValidFilename checks if the provided filename is valid, ensuring it is not empty and does not contain forbidden characters.
// Returns false and sends an error response if the filename is invalid.
func isValidFilename(filename string, w http.ResponseWriter) bool {
	if filename == "" || strings.ContainsAny(filename, "/\\") {
		http.Error(w, "[-] Invalid filename", http.StatusBadRequest)
		return false
	}
	return true
}

// fileExists checks if a file exists at the given filename path.
// Returns true if the file exists, false otherwise.
func fileExists(filename string) bool {
	_, err := os.Stat(filename)
	return !os.IsNotExist(err)
}

// handleError sends an error response with the given message and status code.
func handleError(w http.ResponseWriter, message string, statusCode int) {
	http.Error(w, message, statusCode)
}

// handleFileUpload processes a file upload request, saving the uploaded file to the server.
// The file is stored in the 'file_storage' directory with the filename provided in the request.
func handleFileUpload(w http.ResponseWriter, r *http.Request) {
	if !checkMethod(r.Method, http.MethodPost, w) {
		return
	}

	if !checkAPIKey(w, r, false) {
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB limit
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	file, handler, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "[-] Error Retrieving the File", http.StatusBadRequest)
		return
	}
	defer file.Close()

	fileContent, err := ioutil.ReadAll(file)
	if err != nil {
		http.Error(w, "[-] Error Reading the File", http.StatusInternalServerError)
		return
	}

	filename := handler.Filename

	if !isValidFilename(filename, w) {
		return
	}

	relativeFilePath := filepath.Join(storagePath, filename)

	err = ioutil.WriteFile(relativeFilePath, fileContent, 0666)
	if err != nil {
		http.Error(w, "[-] Error Writing the File", http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "[+] File Uploaded Successfully: %s\n", filename)
}

// handleFileExistence handles requests to check if a file exists on the server.
// Returns a response indicating whether the file exists or not.
func handleFileExistence(w http.ResponseWriter, r *http.Request) {
	if !checkMethod(r.Method, http.MethodGet, w) {
		return
	}

	if !checkAPIKey(w, r, false) {
		return
	}

	filename := r.URL.Query().Get("file")
	if !isValidFilename(filename, w) {
		return
	}

	relativeFilePath := filepath.Join(storagePath, filename)

	if fileExists(relativeFilePath) {
		fmt.Fprintf(w, "[+] File %s exists on the server\n", filename)
	} else {
		http.Error(w, fmt.Sprintf("[-] File %s does not exist on the server", filename), http.StatusNotFound)
	}
}

// handleFileDownload processes file download requests, sending the requested file to the client.
// Sets the appropriate headers to facilitate file download.
func handleFileDownload(w http.ResponseWriter, r *http.Request) {
	if !checkMethod(r.Method, http.MethodGet, w) {
		return
	}

	if !checkAPIKey(w, r, false) {
		return
	}

	filename := r.URL.Query().Get("file")
	if !isValidFilename(filename, w) {
		return
	}

	relativeFilePath := filepath.Join(storagePath, filename)

	if fileExists(relativeFilePath) {
		file, err := os.Open(relativeFilePath)
		if err != nil {
			http.Error(w, fmt.Sprintf("[-] Error opening file %s", filename), http.StatusInternalServerError)
			return
		}
		defer file.Close()

		w.Header().Set("Content-Type", "application/octet-stream")
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filename))

		_, err = io.Copy(w, file)
		if err != nil {
			http.Error(w, "[-] Error sending file contents", http.StatusInternalServerError)
			return
		}

		fmt.Fprintf(w, "[+] File %s downloaded successfully\n", filename)
	} else {
		http.Error(w, fmt.Sprintf("[-] File %s does not exist", filename), http.StatusNotFound)
	}
}

// handleFileExecution processes requests to execute a file on the server.
// Sets the file to be executable and runs it as a command.
func handleFileExecution(w http.ResponseWriter, r *http.Request) {
	if !checkMethod(r.Method, http.MethodPost, w) {
		return
	}

	if !checkAPIKey(w, r, true) {
		return
	}

	err := r.ParseForm()
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	filename := r.Form.Get("file")
	if !isValidFilename(filename, w) {
		return
	}

	relativeFilePath := filepath.Join(storagePath, filename)

	if fileExists(relativeFilePath) {
		err = os.Chmod(relativeFilePath, 0755)
		if err != nil {
			http.Error(w, fmt.Sprintf("[-] Error making file %s executable", filename), http.StatusInternalServerError)
			return
		}

		cmd := exec.Command("./" + relativeFilePath)
		err = cmd.Run()
		if err != nil {
			http.Error(w, fmt.Sprintf("[-] Error executing file %s: %s", filename, err.Error()), http.StatusInternalServerError)
			return
		}

		fmt.Fprintf(w, "[+] File %s executed successfully\n", filename)
	} else {
		http.Error(w, fmt.Sprintf("[-] File %s does not exist on the server", filename), http.StatusNotFound)
	}
}

// handleFileDeletion processes requests to delete a file from the server.
// Removes the file and sends a response indicating the result.
func handleFileDeletion(w http.ResponseWriter, r *http.Request) {
	if !checkMethod(r.Method, http.MethodDelete, w) {
		return
	}

	if !checkAPIKey(w, r, false) {
		return
	}

	filename := r.URL.Query().Get("file")
	if !isValidFilename(filename, w) {
		return
	}

	relativeFilePath := filepath.Join(storagePath, filename)

	if !fileExists(relativeFilePath) {
		http.Error(w, fmt.Sprintf("[-] File %s does not exist on the server", filename), http.StatusNotFound)
		return
	}

	err := os.Remove(relativeFilePath)
	if err != nil {
		http.Error(w, fmt.Sprintf("[-] Error deleting file %s", filename), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "[+] File %s deleted successfully\n", filename)
}

// MethodDetails contains details about a specific method.
type MethodDetails struct {
	Method       string `json:"method"`
	APIKeyHeader string `json:"apiKeyHeader,omitempty"`
	Argument     string `json:"argument,omitempty"`
}

// MethodInfo contains information about allowed methods and their required arguments.
type MethodInfo struct {
	API      MethodDetails `json:"4p1"`
	Upload   MethodDetails `json:"upl04d"`
	Check    MethodDetails `json:"ch3ck"`
	Download MethodDetails `json:"d0wnl04d"`
	Execute  MethodDetails `json:"3x3cut3"`
	Delete   MethodDetails `json:"d3l3t3"`
}

// getMethodInfo returns a MethodInfo struct containing details about allowed HTTP methods and their required arguments.
func getMethodInfo() MethodInfo {
	return MethodInfo{
		API: MethodDetails{
			Method: http.MethodGet,
		},
		Upload: MethodDetails{
			Method:       http.MethodPost,
			APIKeyHeader: "X-API-Key",
			Argument:     "file",
		},
		Check: MethodDetails{
			Method:       http.MethodGet,
			APIKeyHeader: "X-API-Key",
			Argument:     "file",
		},
		Download: MethodDetails{
			Method:       http.MethodGet,
			APIKeyHeader: "X-API-Key",
			Argument:     "file",
		},
		Execute: MethodDetails{
			Method:       http.MethodPost,
			APIKeyHeader: "X-Sensitive-API-Key",
			Argument:     "file",
		},
		Delete: MethodDetails{
			Method:       http.MethodDelete,
			APIKeyHeader: "X-API-Key",
			Argument:     "file",
		},
	}
}

// handleAPIRequest handles requests to /api and serves method information.
func handleAPIRequest(w http.ResponseWriter, r *http.Request) {
	methodInfo := getMethodInfo()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(methodInfo)
}

func main() {
	err := loadConfig()
	if err != nil {
		fmt.Println("[-] Error loading configuration:", err)
		return
	}

	// Handle default route to set proper Server header
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Server", "[*] nmap says 'ssl/pharos?'... really? What a shame I can't tell you what I am :)")
		w.WriteHeader(http.StatusTeapot)
		w.Write([]byte("[-] You're definitely NOT welcome here friend!"))
	})

	http.HandleFunc("/4p1", handleAPIRequest)
	http.HandleFunc("/upl04d", handleFileUpload)
	http.HandleFunc("/ch3ck", handleFileExistence)
	http.HandleFunc("/d0wnl04d", handleFileDownload)
	http.HandleFunc("/3x3cut3", handleFileExecution)
	http.HandleFunc("/d3l3t3", handleFileDeletion)

	fmt.Println("[*] Server is listening on port 4443...")
	err = http.ListenAndServeTLS(":4443", "cr_cert.pem", "cr_key.pem", nil)
	if err != nil {
		fmt.Println("[-] Error starting server:", err)
	}
}
