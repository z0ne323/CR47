![BANNER](https://github.com/user-attachments/assets/bc1828fa-e687-4140-ac24-d9cc997f3175)


You can find the Write-Up just [here](https://github.com/z0ne323/CR47/blob/main/Walkthrough/Walkthrough.md) and if you're interested about this new "concept", I also created a `Roadmap.md` file just [there](https://github.com/z0ne323/CR47/blob/main/Roadmap.md)

# CR47 set up guide
## Installing the server
### Create the VM
1) Download the latest ubuntu server ISO on https://ubuntu.com/download/server
2) Now it's time to verify the iso through the `SHA256` checksum:
- On windows: `Get-FileHash .\ubuntu-VERSION-live-server-amd64.iso -Algorithm SHA256`
- On Linux: `sha256sum ubuntu-VERSION-live-server-amd64.iso`
3) After getting and verifying the ISO, follow the installation process for this new VM on your favorite hypervisor. (Pick always default options for everything)

### Booting the VM - Installing Ubuntu Server
1) Launch the VM and when booting the ISO, select your language and keyboard layout
2) When asked what type of install you want, make sure you select the default `Ubuntu Server`.
3) For the network connections step, just wait a little bit to make sure the VM is able to connect to your interface. When this is done you should see the button switch from `Continue without network` to `Done`
4) No proxy address needs to be set up
5) For `Configuring Ubuntu archive mirror` make sure you have `http://archive.ubuntu.com/ubuntu/` (wait a little bit to make sure the mirror location pass all the tests)
6) When arriving at the `Guided Storage configuration` step, just hit `tab` five times to go straight to the `Done` button. When hitting it, you should get to `FILE SYSTEM SUMMARY` part, hit done again, confirm by switching from `No` to `Continue` when prompted and get to the next step.
7) On the `Profile configuration` part, set your name, username and password to `temp`. Set the server's name to `cr47`. When this is done, hit `Done` button and go to the next step 
8) When asked to `Upgrade to Ubuntu Pro` just hit `Continue` to skip.
9) On the `SSH Setup` part, hit space to check the `Install Openssh server` line, then hit tab twice to go on the `Done` button. 
10) Last step will be to skip the part of the `Featured Server Snaps`, to do so, just hit tab to go on the `Done` button and hit enter to start the install!
11) Go grab a tea or coffee while the server is installing on the VM, when it's done just hit the `Reboot Now` button and hit `ENTER` when asked, then you should be good to go :)

### Creating user `scubaman`, setting `root` password and `ssh` access

1) First step for you is to log in to the server with the `temp` user like so: `ssh temp@IP` (`temp` is the password you set up normally and you'll have to find the machine `IP`)
2) Now that you're on the server as `temp`, change user to `root` like so: `sudo su`, then type `cd` to get to the home `root` folder.
3) You should be able to create a new user called `scubaman` with a new home folder like so: `useradd -m scubaman`
4) Set this password for `scubaman` (`5cu84m4n157h3u171m473dud3`) using this command: `passwd scubaman`
5) Now that this is done, we need to change the default shell from `sh` to `bash`, we can do it this way: `chsh -s /bin/bash scubaman`
6) Set this password for root (`2007h45m023219h757h4n5cu84m4n`) using this command: `passwd` as `root`
7) Lastly configure ssh access for `root` before logging off like so: `sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config && service ssh restart`

### Deleting user `temp`

1) Now that it's done, last step is to remove completely the user `temp`, to do so first log off from the machine and log back in as `root` like so: `ssh root@IP`.
2) Finally, use this command: `userdel temp && rm -rfv /home/temp`.

Now we should be good user wise, let's move on!!

### Updating the machine

First step is to use any SSH client you want to connect to your newly installed machine.

Since you're logged in as `root`, get update from your sources list, upgrade your packages and remove packages that were automatically installed to satisfy dependencies for other packages that are now no longer needed. To do all of this just use this command: 

`apt update -y && apt full-upgrade -y && apt autoremove -y`

When this is done, start to read what's next...

### 1 - Clearing history / Disabling Command History Log
This step will be extremly important to make sure we don't leak anything, you can do so by following these steps as `scubaman` (`su scubaman`, then `cd`):

1) First clear any previous history by doing `history -c`
1) Create a symbolic link from .bash_history to /dev/null like so: `ln -sf /dev/null ~/.bash_history`
3) Validate the previous command by doing: `ls -l ~/.bash_history`

When this is done, repeat the same process but this time as `root`, do `su` from `scubaman` user and go to the root home foler (`cd`). As a side note, please don't forget to remove the `snap/` folder from `root` like so : `rm -rfv /root/snap`. When this is done repeat the three steps you followed above with `scubaman` but as `root` this time.

### 2 - Installing necessary packages - Making sure everything is up to date, upgraded and / or removed
To make everything work for this challenges, we will need to have a few packages installed, to do so follow the steps below:

1) As `root`, use this command to install the packages: `apt install apache2 php python3-pip -y`
2) After installing them do as `root`: `apt update -y && apt full-upgrade -y && apt autoremove -y` just to make sure we're all good on the package side.

### 3 - Setting up the web challenges (foothold)

(Unless specified, all the commands below should be run as `root`)

#### A - html
1) Enable these two modules for apache by running: `a2enmod rewrite ssl`
2) Generate our cert and private key like that: `openssl req -x509 -nodes -newkey rsa:4096 -keyout /etc/ssl/private/cr_airport-selfsigned.key -out /etc/ssl/certs/cr_airport-selfsigned.crt -days 3650 -subj "/C=CR/ST=Limón/L=Puerto Limón/O=Aeropuerto Internacional de Limón/CN=NoName/emailAddress=NoEmail@NoEmail.com"`
3) Let's remove our listener on port 80 (`http`), by doing: `sed -i '/Listen 80/s/^/#/' /etc/apache2/ports.conf`
4) After this, create a new `.conf` file for our `vhost`: `nano /etc/apache2/sites-available/cr_airport.conf`, in there put:
    ```
    <VirtualHost *:443>
        ServerAdmin webmaster@lio.com
        ServerName lio.airport
        DocumentRoot /var/www/html

        SSLEngine on
        SSLCertificateFile /etc/ssl/certs/cr_airport-selfsigned.crt
        SSLCertificateKeyFile /etc/ssl/private/cr_airport-selfsigned.key

        <Directory /var/www/confidential_files>
            Require all denied
        </Directory>

        ErrorLog /dev/null
        CustomLog /dev/null combined
    </VirtualHost>
    ```
5) Now you can just enable our site configuration like so: `a2ensite cr_airport.conf`
6) Finally, do `rm -rfv /var/www/html` first, then you can move all the folders you'll find under `www-data` here (`chatbot`, `confidential_files`, `html`) under `/var/www` on the machine
7) Make sure to change the ownership of everything under `/var/www` to `www-data` (the user that apache run as). You can do this like that: `chown -R www-data:www-data /var/www/*`
8) Don't forget to change certain permissions for our `confidential_files` folder by doing: `chmod 750 /var/www/confidential_files && chmod -R 440 /var/www/confidential_files/*` 
9) Last thing of course is to reboot the service to incorporate the change. We can do so like this as `root`: `service apache2 restart`

#### B - chatbot

1) You'll have to remove this directory: `rm /usr/lib/python3.12/EXTERNALLY-MANAGED`
2) Then installed Flask like so: `pip3 install Flask`
3) Open `crontab` as `www-data` like so: `crontab -u www-data -e`
4) Put at the end of the file this line: `@reboot cd /var/www/chatbot && /usr/bin/python3 /var/www/chatbot/app.py`

### 4 - Setting up the API challenge (foothold)

(Unless specified, all the commands below should be run as `scubaman`)

1) Move the `scubaman/NFMS` folder from the repo to the home `scubaman` folder of the machine
2) Now don't forget to make it executable: `chmod +x ~/NFMS/server ~/NFMS/start_nfms.sh`
3) Finally just open `crontab` as `scubaman` like so: `crontab -u scubaman -e`
4) Add this line at the end of the file: `@reboot cd /home/scubaman/NFMS && /home/scubaman/NFMS/start_nfms.sh`

### 5 - Setting up the final challenge (privesc)

1) First as `scubaman`:
- Move `scubaman/sss_over_udp` folder from the repo to the home folder of `scubaman`

2) Then as `root`:
- Move `root/sss_over_udp` folder from the repo to the home folder of `root`
- Open the cronjobs like so: `crontab -u root -e`
- Add this line at the end of the file: `@reboot cd /root/sss_over_udp && /usr/bin/python3 /root/sss_over_udp/server.py`

### 6 - Making sure our hacker is welcomed graciously (`ssh`)

1) Do this: `sed -i 's/^#\?\(PubkeyAuthentication\s*\).*/\1yes/' /etc/ssh/sshd_config` to make sure we can authenticate with keys 
2) As `root`, do this command: `sed -i 's/^#* *PrintLastLog yes/PrintLastLog no/' /etc/ssh/sshd_config`, to remove the last login line when connecting with `ssh`
3) As `root` do this command: `sed -i 's/^#* *PrintMotd no/PrintMotd yes/' /etc/ssh/sshd_config`, to create a Message Of The Day
4) As `root` create a file like this: `nano /etc/motd` and then put this inside:
```
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
```
5) As `root`, do this command **TWICE** (after the first time restart your `ssh` service and do it again): `sed -i 's/^session    optional     pam_motd.so  motd=\/run\/motd.dynamic/# session    optional     pam_motd.so  motd=\/run\/motd.dynamic/' /etc/pam.d/sshd && sudo sed -i 's/^session    optional     pam_motd.so noupdate/# session    optional     pam_motd.so noupdate/' /etc/pam.d/sshd`, to remove the Welcome Message when connecting with `ssh`
6) As `root`, to apply the changes, do `service ssh restart`.
7) Finally, reboot using the command: `reboot` still as `root`
