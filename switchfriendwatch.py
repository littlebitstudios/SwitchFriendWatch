import json
import yaml
import os
import subprocess
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

configpath = os.path.expanduser("~/.littlebitstudios/switchfriendwatch/configuration.yaml")

try:
  config = yaml.safe_load(open(configpath))
except FileNotFoundError:
  print("No configuration file! Create a file at", configpath, "and follow the format detailed on the project page.")
  exit()

# Setting up SMTP if email is enabled
mailsender = None
if config['email']['enabled'] == True:
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

# Gather NSO friend data from nxapi
nxapi = None
if config['windowsmode'] == True:
  nxapi = subprocess.run(["powershell.exe", "nxapi", "nso", "friends", "--json"], capture_output=True)
else:
  nxapi = subprocess.run(["nxapi", "nso", "friends", "--json"], capture_output=True)
  
friends = None
if nxapi.returncode == 0:
  friends = json.loads(nxapi.stdout.decode("utf-8"))
else:
  print("Error running nxapi. Please check the tool and its installation.")

def mailsendonline(username, game, lastchange):
  message = MIMEMultipart()
  message['From'] = "Switch Friend Watch"+" <"+config['email']['sendfrom']+">"
  message['To'] = config['email']['sendto']
  message['Subject'] = username+" is online playing "+game

  body_text = MIMEText("Your friend " + username + " is now online playing " + game + ". \nLast status update: " + lastchange.strftime("%b %d, %Y at %I:%M %p") + "." + "\n\nSwitch Friend Watch\na tool by LittleBit", 'plain')
  message.attach(body_text)

  try:
      mailsender.send_message(msg=message)
      print("Email sent successfully!")
  except smtplib.SMTPException as e:
      print(f"Error sending email: {e}")
      
def mailsendonlinewatched(username, game, lastchange):
  message = MIMEMultipart()
  message['From'] = "Switch Friend Watch"+" <"+config['email']['sendfrom']+">"
  message['To'] = config['email']['sendto']
  message['Subject'] ="[WATCHED] "+username+" is online playing "+game

  body_text = MIMEText(" Your friend " + username + " is now online playing " + game + ". \n You're watching this friend. \nLast status update: " + lastchange.strftime("%b %d, %Y at %I:%M %p") + "." + "\n\nSwitch Friend Watch\na tool by LittleBit", 'plain')
  message.attach(body_text)

  try:
      mailsender.send_message(msg=message)
      print("Email sent successfully!")
  except smtplib.SMTPException as e:
      print(f"Error sending email: {e}")
      
if config['email']['enabled']:
  if config['email']['sendtest']=="unwatched":
    print("Email enabled with sendtest flag set to unwatched, sending a test email for unwatched friend!")
    hashtagnumber=random.randint(1000,9999)
    mailsendonline("Player#"+str(hashtagnumber), "TestGame", datetime.datetime.now())
    config['email']['sendtest']="off"
    exit()
  if config['email']['sendtest']=="watched":
    print("Email enabled with sendtest flag set to watched, sending a test email for watched friend!")
    hashtagnumber=random.randint(1000,9999)
    mailsendonlinewatched("Player#"+str(hashtagnumber), "TestGame", datetime.datetime.now())
    config['email']['sendtest']="off"
    exit()
    
lastchecktime = datetime.datetime.fromisoformat(config['lastcheck'])
print("Last run time:",lastchecktime.strftime("%b %d, %Y at %I:%M %p"))

watched = list()
for user in config["watched"]:
  watched.append(user)

# Checking for watched users online, and making sure their status has changed since the last time the script ran
def check_and_send_email(user):
  last_check = datetime.datetime.fromisoformat(config['lastcheck'])
  updated_at = datetime.datetime.fromtimestamp(user['presence']['updatedAt'])

  if updated_at > last_check:
    is_online = user['presence']['state'] == "ONLINE"
    
    game_name = str()
    if is_online:
      game_name = user['presence']['game']['name']

    if (user['name'] in watched or user['id'] in watched) and is_online:
      print(user['name'], "is watched and went online!")
      if config['email']['enabled']:
        mailsendonlinewatched(user['name'], game_name, updated_at)
    elif is_online and config['watchedonly'] == False:
      print(user['name'], "went online!")
      if config['email']['enabled']:
        mailsendonline(user['name'], game_name, updated_at)
    elif not is_online:
      print(user['name'], "went offline.")

# Iterate through friends and call the check function
for friend in friends:
  check_and_send_email(friend)
                
config['lastcheck'] = datetime.datetime.now().isoformat()

with open(configpath, 'w') as outfile:
    yaml.dump(config, outfile, default_flow_style=False)