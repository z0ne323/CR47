<?php
// Include configuration file for credentials
require_once '/var/www/confidential_files/dadd0662bff0311e0be398570bc2001d.php'; // config_with_creds.php

// Start session with secure options
session_start([
    'cookie_secure' => true,
    'cookie_httponly' => true,
]);

// Check if the Authorization header is set
if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW'])) {
    // Send authentication headers
    header('WWW-Authenticate: Basic realm="Restricted Area"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'Authorization Required';
    exit;
}

// Validate username and hash input password
if ($_SERVER['PHP_AUTH_USER'] == $credentials['4p11d34s']['username'] && password_verify($_SERVER['PHP_AUTH_PW'], $credentials['4p11d34s']['password_hash'])) {
    // Successful authentication
    header('HTTP/1.0 200 OK');
    
    // Read the content of endpoints_list.txt 
    $file_path = '/var/www/confidential_files/e38e09bc83639e724f02dda2d92feb3a.txt';
    if (file_exists($file_path)) {
        $file_content = file_get_contents($file_path);
        
        // Check if the request comes from a browser or cURL
        if (strpos($_SERVER['HTTP_USER_AGENT'], 'curl') !== false) {
            // Output each word on a new line for cURL
            echo str_replace("<br>", "\n", $file_content);
        } else {
            // Output words directly without list formatting for web browsers
            $words = explode("\n", str_replace("<br>", "\n", $file_content));
            foreach ($words as $word) {
                echo "$word<br>";
            }
        }
        
        exit;
    } else {
        header('HTTP/1.0 404 Not Found');
        echo 'File not found';
        exit;
    }
} else {
    // Invalid credentials
    header('HTTP/1.0 401 Unauthorized');
    echo 'Invalid credentials';
    exit;
}
?>



