<?php

// Start session with secure options
session_start([
    'cookie_secure' => true,
    'cookie_httponly' => true,
]);

// Check if the user is logged in
if (!isset($_SESSION['username'])) {
    // Redirect to the login page or display an error message
    header("Location: /acceso/");
    exit();
}

// Directory where confidential files are stored
$confidentialDir = '/var/www/confidential_files/';

// Check if the filename parameter is set and matches the expected pattern
if (isset($_GET['filename']) && preg_match('/^[a-zA-Z0-9_-]+\.txt$/', $_GET['filename'])) {
    // Construct the full path to the file
    $file = $confidentialDir . $_GET['filename'];

    // Check if the file exists within the confidential directory
    if (file_exists($file) && strpos(realpath($file), realpath($confidentialDir)) === 0) {
        // Set headers to force download
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($file) . '"');
        header('Content-Length: ' . filesize($file));
        ob_clean();
        flush();
        readfile($file);
        exit;
    } else {
        // Invalid request or file not found
        header("HTTP/1.0 418 I'm a teapot");
        echo 'File not found, TEAPOOOOOOOOOOOOOOOOT.';
    }
} else {
    // Invalid filename format or missing parameter
    header("HTTP/1.0 418 I'm a teapot");
    echo 'Invalid filename, who are you ? I like tea.';
}
?>