<?php
// Include configuration file for credentials
require_once '/var/www/confidential_files/dadd0662bff0311e0be398570bc2001d.php'; // config_with_creds.php

// Start session with secure options
session_start([
    'cookie_secure' => true,
    'cookie_httponly' => true,
]);

// Check if form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Retrieve values from form
    $input_username = filter_input(INPUT_POST, 'username', FILTER_SANITIZE_STRING);
    $input_password = $_POST["password"];

    // Validate username and hash input password
    if ($input_username === $credentials['administracion']['username'] && password_verify($input_password, $credentials['administracion']['password_hash'])) {
        // Authentication successful
        $_SESSION["username"] = $input_username;
        session_regenerate_id(); // Regenerate session ID

        // Redirect user to dashboard
        header("Location: panel.php", true, 302);
        exit();
    } else {
        // Authentication failed
        $error_message = "Nombre de usuario y/o contraseña no válidos.";
    }
}
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DIS - UdO</title>
    <link rel="icon" type="image/x-icon" href="Escudo_DIS.png">
    <link rel="stylesheet" href="style.css">
</head>
<body>

<div class="container">
    <div class="login-box">
        <!--"Deberíamos ocultar el encabezado de abajo - Santiago Carrillo"-->
        <h2>DIS - Sistema de Unidad de Operaciones</h2>
        <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
            <div class="textbox">
                <input type="text" name="username" id="username" required>
                <label for="username">Nombre de usuario</label>
            </div>
            <div class="textbox">
                <input type="password" name="password" id="password" required>
                <label for="password">Contraseña</label>
            </div>
            <button type="submit" class="btn">Acceso</button>
        </form>
        <?php
        // Display error message if authentication failed
        if (isset($error_message)) {
            echo "<p style='color: red;'>$error_message</p>";
        }
        ?>
    </div>
</div>

</body>
</html>
