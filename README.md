# Switch Friend Watch
This tool uses the open-source push notification server **ntfy** and system commands to send you notifications about Nintendo Switch friend activity, gathering data from the well-known Switch API tool [samuelthomas2774/nxapi](https://github.com/samuelthomas2774/nxapi).

This tool used to send emails, but I completed a massive overhaul to switch to using ntfy because it's much simpler to work with.

# Python Dependencies
This script depends on the following Python packages:

* **`PyYAML`**: For reading the configuration file.
* **`requests`**: For sending HTTP POST requests to the ntfy server.

You can install all dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

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

If you aren't on Windows or Ubuntu, go to https://nodejs.org to install Node.js.

## Install nxapi

npm should have been installed when Node.js was installed, so you can install nxapi with this command:

```bash
npm install -g nxapi@next
```

*Installing the `next` variant of NXAPI is required because of breaking changes to Nintendo's infrastructure.*  
The `-g` flag is required because by default only global npm packages are in the PATH.

## Connect your Nintendo Account

Run `nxapi nso auth` and it will tell you how to authenticate with your Nintendo Account.

# Configuration

The script calls from a configuration file located at `<home folder>/.littlebitstudios/switchfriendwatch/configuration.yaml`. Simply copy the `.littlebitstudios` folder from the repository to your home folder.

### Configuration File Structure

This is the structure of the file:

```yaml
aliases: # optional: add aliases here in the format of <NSA ID>: <alias>
  b023adfefd82147a: LittleBit670 # example
ntfy:
  enabled: true # if false, no push notifications will be sent
  server: "https://ntfy.sh" # The base URL of your ntfy server (use a self-hosted one or the public one)
  topic: "your_unique_switch_friend_topic" # REQUIRED: The topic name to which the script will publish and your app is subscribed
  sendtest: 'off' # set to 'unwatched' or 'watched' to send a test notification on next run, must be reset to off
watched: # this field is optional
- LittleBit # example of nickname
- b023adfefd82147a # example of NSA ID
# above is the list of watched friends; you can add watches by nickname or NSA ID
# NSA IDs can be obtained using the command "nxapi nso friends" or with the nxapi desktop app
windowsmode: false # this must be true for Windows users; not needed for MacOS or Linux
watchedonly: true # if true, only watched friends will trigger a notification; the watched list is required if this is true
```

You can look in the .littlebitstudios/switchfriendwatch folder to see the example as well.

# Usage

To run the script once you have created the configuration file, just run `python3 <path to file>` like any other Python script.

The script is designed to be automated (using **cron** on Linux or possibly **Task Scheduler** on Windows), where it runs every so often to see if the status of your friend list has changed. If people go online, it will send you a **push notification** via ntfy, assuming ntfy is enabled and configured correctly.

ntfy is self-hostable and offers a web client, as well as native clients for mobile.

# Recommendations

I recommend running this on a Linux machine that stays on 24/7, such as a home server. This can also be run on your main computer under Windows/Mac/Linux, but notifications would stop if you shut down your computer.

If you want a beginner's home server, maybe look into a Linux-based single-board computer like the Raspberry Pi or a barebones x86 computer like a NUC. Commercial home server products such as the ZimaBoard, ZimaCube, or Umbrel Home rely heavily on Docker containers and I don't know if I could containerize this script since it relies on two different scripting frameworks (Node.js and Python).

# Credits

The Nintendo Switch gaming system and Nintendo Accounts are owned by Nintendo Co. Ltd. and its regional subsidiaries.

nxapi is a tool created by [@samuelthomas2774](https://github.com/samuelthomas2774), licensed under the [GNU AGPL 3.0](https://www.gnu.org/licenses/agpl-3.0).

Because this script depends on an AGPL-licensed tool, it is also licensed under the GNU AGPL 3.0. (see the LICENSE file or the link to the AGPL above)