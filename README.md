# Switch Friend Watch
This tool uses smtplib and system commands to send you emails about Nintendo Switch friend activity, gathering data from well-known Switch API tool [samuelthomas2774/nxapi](https://github.com/samuelthomas2774/nxapi).

# Python Dependencies
This script depends on PyYAML and smtplib. Other imports should be installed by default.

# Installing nxapi
This script relies on being able to send commands through the operating system to a Node.js tool called nxapi. This tool is on GitHub: [samuelthomas2774/nxapi](https://github.com/samuelthomas2774/nxapi).

## Install Node.js
nxapi is based on Node.js, so you will need to install it.

For Windows:
```powershell
winget install OpenJS.NodeJS
```

For Ubuntu:
```bash
sudo apt install nodejs
```

Follow separate instructions for your OS if you aren't using Windows or Ubuntu.

## Install nxapi
npm should have been installed when Node.js was installed, so you can install nxapi with this command:
```bash
npm install -g nxapi
```
The -g flag is required because by default only global npm packages are in the PATH.

## Connect your Nintendo Account
Run `nxapi nso auth` and it will tell you how to authenticate with your Nintendo Account.

# Configuration
The script calls from a configuration file located at `<home folder>/.littlebitstudios/switchfriendwatch/configuration.yaml`. Simply copy the `.littlebitstudios` folder from the repository to your home folder.

This is the structure of the file:
```yaml
email:
  debugmode: false # enable this if you're troubleshooting smtplib
  enabled: true # leave this true, setting this false will suppress emails
  pass: 'password' # SMTP password, if a service uses 2FA you may need a specific app password
  port: 465 # SMTP port, check with your email provider
  sendfrom: example@example.com # the source email address
  sendtest: 'off' # send a test email by setting this to 'watched' or 'unwatched' and running the script
  sendto: you@example.com # the email you want to receive notifications at
  server: smtp.example.com # the SMTP server of the source email address
  user: example@example.com # SMTP username, this is usually the source email address but could be different depending on provider
lastcheck: '2024-05-27T13:49:22.643963' # do not change this, the script uses this timestamp as a reference for when it last ran
watched: # list of watched players
- Player
watchedonly: false # set this to true to only be notified about watched players
windowsmode: false # set this to true if running on a Windows machine
```

Please be aware that all comments in the file will disappear when the script is ran for the first time, as the script constantly rewrites the configuration file 

# Usage
To run the script once you have created the configuration file, just run `python3 <path to file>` like any other Python script.

The script is designed to be automated (using cron on Linux or possibly Task Scheduler on Windows), where it runs every so often to see if the status of your friend list has changed. If people go online, then it will send you an email about it assuming that email is enabled in the configuration.

# Recommendations
I recommend running this on a Linux machine that stays on 24/7, such as a home server. This can also be run on your main computer under Windows/Mac/Linux, but notifications would stop if you shut down your computer. 

If you want a beginner's home server, maybe look into a Linux-based single-board computer like the Raspberry Pi or a barebones x86 computer like a NUC. Commercial home server products such as the ZimaBoard, ZimaCube, or Umbrel Home rely heavily on Docker containers and I don't know if I could containerize this script since it relies on two different scripting frameworks (Node.js and Python).

# Credits
The Nintendo Switch gaming system and Nintendo Accounts are owned by Nintendo Co. Ltd. and its regional subsidiaries.

nxapi is a tool created by [@samuelthomas2774](https://github.com/samuelthomas2774), licensed under the [GNU AGPL 3.0](https://www.gnu.org/licenses/agpl-3.0).

Because this script depends on an AGPL-licensed tool, it is also licensed under the GNU AGPL 3.0. (see the LICENSE file or the link to the AGPL above)