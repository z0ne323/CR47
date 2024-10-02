<?php

// Start session with secure options
session_start([
    'cookie_secure' => true,
    'cookie_httponly' => true,
]);

// Check if the user is logged in
if (!isset($_SESSION['username'])) {
    // Redirect to the login page
    header("Location: administracion.php");
    exit();
}

// Tickets list
$tickets = array(
    array("001", "[*] Players progressing through cr47...", "Waiting for completion :)", "N/A", "Pending"),
    array("002", "New File Management System", "Made last update, please review new file and instruct on next steps.", "dec7d0ab8aae309ab949cca7974a34d2.txt", "In Progress"),
    array("003", "Broken access control vulnerability.", "Got it fixed just now, please see the attached file for more details.", "a3229c43fddcefaed7db9b3410bb90e2.txt", "Closed")
);
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="Escudo_DIS.png">
    <title>DIS - UdO</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-image: url('DIS_UdO_panel.jpg'); /* Background image URL */
            background-size: cover;
            background-position: center;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: rgba(255, 255, 255, 0.8); /* Adjust background color opacity if needed */
            border-radius: 8px;
            padding: 20px;
        }

        h1 {
            text-align: center;
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            vertical-align: middle; /* Align content vertically in the middle */
        }

        .status {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 20px;
            color: #fff;
            font-size: 12px;
            white-space: nowrap; /* Ensure the status button stays on one line */
            overflow: hidden; /* Hide overflow text */
            text-overflow: ellipsis; /* Add ellipsis if text overflows */
        }

        .status-closed {
            background-color: #2ecc71; /* green */
        }

        .status-in-progress {
            background-color: #f39c12; /* orange */
        }

        .status-pending {
            background-color: #e74c3c; /* red */
        }

        a {
            color: #3498db;
            text-decoration: none;
        }

        .attachment {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 20px;
            background-color: #3498db;
            color: #fff;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to the Dashboard</h1>
        <table>
            <tr>
                <th>Ticket Number</th>
                <th>Description</th>
                <th>Technician Response</th>
                <th>Attachments</th>
                <th>Status</th>
            </tr>
            <?php foreach ($tickets as $ticket): ?>
            <tr>
                <td><?php echo $ticket[0]; ?></td>
                <td><?php echo $ticket[1]; ?></td>
                <td><?php echo $ticket[2]; ?></td>
                <td>
                    <?php if ($ticket[3] !== "N/A"): ?>
                        <a href="download.php?filename=<?php echo urlencode($ticket[3]); ?>" download class="attachment">Download</a>
                    <?php else: ?>
                        N/A
                    <?php endif; ?>
                </td>
                <td>
                    <span class="status status-<?php echo strtolower(str_replace(' ', '-', $ticket[4])); ?>">
                        <?php echo $ticket[4]; ?>
                    </span>
                </td>
            </tr>
            <?php endforeach; ?>
        </table>
        <a href="cerrar_sesion.php">Cerrar sesión</a>
    </div>
</body>
</html>
