import json
import yaml
import os
import subprocess
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# Constants
softwarepath = os.path.expanduser("~/.littlebitstudios/switchfriendwatch/")
configpath = softwarepath + "configuration.yaml"
lastcheckpath = softwarepath + "lastcheck.txt"
lastchecktime = datetime.datetime.fromisoformat(open(lastcheckpath).read())

# Logic to check if a command exists
def check_command_exists(command):
    try:
        subprocess.run([command, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Ensure that Node.js and nxapi are installed
if check_command_exists('node'):
    print('Node.js is installed.')
    if check_command_exists('nxapi'):
        print('nxapi is installed.')
    else:
        print('nxapi is not installed. Run "npm install -g nxapi" to install it.')
        exit()
else:
    print('Node.js is not installed. Go to https://nodejs.org/ and follow the instructions for your OS.')
    exit()

# Load the configuration file; if not present prompt the user to create it
try:
    config = yaml.safe_load(open(configpath))
except FileNotFoundError:
    print("No configuration file! Create a file at", configpath, "and follow the format detailed on the project page.")
    exit()

# Connect to the email server if email is enabled
mailsender = None
if config.get('email', {}).get('enabled', False):
    print("Email enabled.")
    print("Connecting to email server")
    try:
        mailsender = smtplib.SMTP_SSL(config['email']['server'], config['email']['port'])
        print("Logging in to email server")
        mailsender.set_debuglevel(config['email']['debugmode'])
        mailsender.login(config['email']['user'], config['email']['pass'])
        mailsender.ehlo_or_helo_if_needed()
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPConnectError, smtplib.SMTPException) as e:
        print(f"Error connecting to email server: {e}")
        exit()

# Run nxapi to get the friends list
nxapi = None
if config.get('windowsmode', False):
    # Invoking PowerShell is required to run nxapi on Windows
    nxapi = subprocess.run(["powershell.exe", "nxapi", "nso", "friends", "--json"], capture_output=True)
else:
    nxapi = subprocess.run(["nxapi", "nso", "friends", "--json"], capture_output=True)

# Parse the JSON output from nxapi
friends = None
if nxapi.returncode == 0:
    friends = json.loads(nxapi.stdout.decode("utf-8"))
else:
    print("Error running nxapi. Please check the tool and its installation.")

# Send email for unwatched friends
def mailsendonline(username, game, lastchange):
    message = MIMEMultipart()
    message['From'] = "Switch Friend Watch" + " <" + config['email']['sendfrom'] + ">"
    message['To'] = config['email']['sendto']
    message['Subject'] = username + " is online playing " + game

    body_text = MIMEText("Your friend " + username + " is now online playing " + game + ". \nLast status update: " + lastchange.strftime("%b %d, %Y at %I:%M %p") + "." + "\n\nSwitch Friend Watch\na tool by LittleBit", 'plain')
    message.attach(body_text)

    try:
        mailsender.send_message(msg=message)
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

# Send email for watched friends
def mailsendonlinewatched(username, game, lastchange):
    message = MIMEMultipart()
    message['From'] = "Switch Friend Watch" + " <" + config['email']['sendfrom'] + ">"
    message['To'] = config['email']['sendto']
    message['Subject'] = "[WATCHED] " + username + " is online playing " + game

    body_text = MIMEText(" Your friend " + username + " is now online playing " + game + ". \n You're watching this friend. \nLast status update: " + lastchange.strftime("%b %d, %Y at %I:%M %p") + "." + "\n\nSwitch Friend Watch\na tool by LittleBit", 'plain')
    message.attach(body_text)

    try:
        mailsender.send_message(msg=message)
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

# Main function: check if status has changed since last check and send email if the user has gone online and email is enabled
def check_and_send_email(user):
    updated_at = datetime.datetime.fromtimestamp(user['presence']['updatedAt'])

    if updated_at > lastchecktime:
        # Check if the user is online
        is_online = user['presence']['state'] == "ONLINE"
        
        # Get the game name if the user is online
        game_name = str()
        if is_online:
            game_name = user['presence']['game']['name']
          
        # Main logic
        if (user['name'] in watched or user['nsaId'] in watched) and is_online: # If the user is watched and online
            print(user['name'], "is watched and went online!")
            if config['email']['enabled']:
                nick = config['aliases'].get(str(user['nsaId']), user['name'])
                mailsendonlinewatched(nick, game_name, updated_at)
        elif is_online and not config.get('watchedonly', False): # If the user is not watched and online, and watchedonly is not enabled
            print(user['name'], "went online!")
            if config['email']['enabled']:
                nick = config['aliases'].get(str(user['nsaId']), user['name'])
                mailsendonline(nick, game_name, updated_at)
        elif not is_online: # If the user went offline; no email is sent for this
            print(user['name'], "went offline.")

# If the sendtest flag is set, send a test email and exit
if config.get('email', {}).get('enabled', False):
    if config['email'].get('sendtest') == "unwatched":
        print("Email enabled with sendtest flag set to unwatched, sending a test email for unwatched friend!")
        hashtagnumber = random.randint(1000, 9999)
        mailsendonline("Player#" + str(hashtagnumber), "TestGame", datetime.datetime.now())
        exit()
    if config['email'].get('sendtest') == "watched":
        print("Email enabled with sendtest flag set to watched, sending a test email for watched friend!")
        hashtagnumber = random.randint(1000, 9999)
        mailsendonlinewatched("Player#" + str(hashtagnumber), "TestGame", datetime.datetime.now())
        exit()

# Print the last run time
print("Last run time:", lastchecktime.strftime("%b %d, %Y at %I:%M %p"))

# Load the watched users and aliases if present, return blank list/dict if not
watched = config.get("watched", [])
aliases = config.get("aliases", {})

# Invoke the main function on each friend
for friend in friends:
    check_and_send_email(friend)

# After completion, update the last check time
with open(lastcheckpath, "w") as f:
    f.write(str(datetime.datetime.now().isoformat()))