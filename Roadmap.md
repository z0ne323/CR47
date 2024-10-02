# INTRODUCING ROADMAP !!

## What is **ROADMAP** ??

**ROADMAP** is a new `.md` file idea I had in mind that basically consists of giving my few tips / tricks I used during the development of `cr47`. You could see this not as instructions to install the box, but rather side notes about how certain things were built, especially on the web side of the box!

### Web on `443`

#### `original_first_note.txt`

```
Hello Alberto,

I'm thinking of changing the way our product is fetching the keys we're using on this server.

Please watch out ! I found that your api key was hardcoded on there... "7h1515d3f1n1731y4n4p1k3y" should never be written on a file, right ? :)

Let me know what I should do to make this more secure, it seems like a giant flaw in our new system :/

Alejandro
```

Then we execute this command on the `.txt`: `zip -q -r -P da45rk7night first_note.zip original_first_note.txt && base64 -w 0 first_note.zip > $(echo -n "first_note" | md5sum | awk '{print $1}').txt && rm original_first_note.txt first_note.zip`.

This command basically zips the text file with a password, encodes the zip file in Base64, saves that encoded content to a text file named after the MD5 hash of "first_note", and then removes the original text and zip files. 
      
  
#### `original_second_note.txt`

```
Hello Alberto,

The "lista" of ideas we had for naming our endpoints was visible to the public (under 4p11d34s/), that's not good, never do that !!

Thankfully I got it fixed, I put a portal up there to prevent access by unauthenticated users.

Got it tested with my own account and it works perfectly ! 

Alejandro Cerdas
```

We're able to run this command on the `.txt` file: `rar a -hpnoche second_note.rar original_second_note.txt && cat second_note.rar | base64 > $(echo -n "second_note" | md5sum | awk '{print $1}').txt && rm original_second_note.txt second_note.rar`

This command basically creates a password-protected RAR archive of the text file, encodes that archive in Base64, saves it to a new text file named after the MD5 hash of "second_note," and then deletes the original text file and the RAR archive.

#### hashes in `dadd0662bff0311e0be398570bc2001d.php`

To store safely the creds in our `.php` config file, I used a custom php script to generate the hashes of the password I've set for both `santiago.carrillo` and `alejandro.cerdas`.
      
The script looked like that:

```php
<?php
// Check if the script is run from CLI
if (php_sapi_name() !== 'cli') {
    die("This script must be run from the command line.");
}

// Check if the password argument is provided
if ($argc !== 2) {
    echo "Usage: php hash_generator.php password\n";
    exit(1);
}

// Retrieve the input from the command line arguments
$password = $argv[1];

// Generate the hash using password_hash()
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);

// Display the original password and the hashed password
echo "Original Password: " . htmlspecialchars($password) . "\n";
echo "Hashed Password: " . htmlspecialchars($hashedPassword) . "\n";

// End of script
?>
```

When getting the hash for `santiago.carrillo`:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ php hash_generator.php PURPLE1
Original Password: PURPLE1
Hashed Password: $2y$10$9X32ob.4/nUGk/eY.F2fbeO210.G8rbW5CSqb1X/9m6nt/mluldYG
```

After this, we're able to move the hash in output to `www-data/confidentials_files/dadd0662bff0311e0be398570bc2001d.php` in `$credentials` -> `'administracion'` -> `'password_hash'`

When getting the hash for `alejandro.cerdas`:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ php hash_generator.php lista
Original Password: lista
Hashed Password: $2y$10$5kEu7HzJQfictpkHMCqrP.X00/TlOq34WzPGY5zonsx2icXOB3sWO
```

After this, we're able to move the hash in output to `www-data/confidentials_files/dadd0662bff0311e0be398570bc2001d.php` in `$credentials` -> `'4p11d34s'` -> `'password_hash'`