<?php

// Start session with secure options
session_start([
    'cookie_secure' => true,
    'cookie_httponly' => true,
]);

// Unset all session variables
$_SESSION = array();

// Destroy the session
session_destroy();

// Redirect to the login page
header("Location: administracion.php");
exit();
?>