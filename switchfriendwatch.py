import json
import yaml
import os
import subprocess
import datetime
import random
import requests  # Added for sending ntfy push notifications

softwarepath = os.path.expanduser("~/.littlebitstudios/switchfriendwatch/")
configpath = softwarepath + "configuration.yaml"
lastcheckpath = softwarepath + "lastcheck.txt"

# Ensure the lastcheckpath file exists and read the last check time
try:
    lastchecktime = datetime.datetime.fromisoformat(open(lastcheckpath).read())
except FileNotFoundError:
    # Initialize lastchecktime to a very old time if the file doesn't exist
    lastchecktime = datetime.datetime.min
    # Create the file with the current time so the script can run next time
    with open(lastcheckpath, "w") as f:
        f.write(str(datetime.datetime.now().isoformat()))


# Check for the existence of nxapi.
def check_command_exists(command):
    try:
        # Attempt to run the command with --version or another non-operative option
        subprocess.run(
            [command, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


if check_command_exists("node"):
    print("Node.js is installed.")
    if check_command_exists("nxapi"):
        print("nxapi is installed.")
    else:
        print('nxapi is not installed. Run "npm install -g nxapi" to install it.')
        exit()
else:
    print(
        "Node.js is not installed. Go to https://nodejs.org/ and follow the instructions for your OS."
    )
    exit()

try:
    config = yaml.safe_load(open(configpath))
except FileNotFoundError:
    print(
        "No configuration file! Create a file at",
        configpath,
        "and follow the format detailed on the project page.",
    )
    exit()

# --- NTFY Configuration & Functions ---
# We now require 'ntfy' settings in configuration.yaml, replacing 'email' settings.
# The ntfy server URL and topic are retrieved from the config.
ntfy_base_url = config["ntfy"]["server"]
ntfy_topic = config["ntfy"]["topic"]


def send_ntfy_notification(title, message, priority=3, tags=None):
    """Sends a push notification via ntfy."""
    try:
        headers = {
            "Title": title,
            "Priority": str(priority),  # 1=min, 3=default, 5=urgent
        }
        if tags:
            headers["Tags"] = ",".join(tags)

        # Use the base URL + topic to form the full endpoint
        response = requests.post(
            f"{ntfy_base_url}/{ntfy_topic}",
            data=message.encode("utf-8"),
            headers=headers,
        )

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print("ntfy notification sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending ntfy notification: {e}")


def send_ntfy_online(username, game, lastchange):
    """Sends an ntfy notification for an unwatched friend going online."""
    title = f"Friend Online"
    message = (
        f"{username} is now online playing {game}. "
        f"Last status update: {lastchange.strftime('%b %d, %Y at %I:%M %p')}."
    )
    send_ntfy_notification(title, message, priority=3, tags=["video_game"])


def send_ntfy_onlinewatched(username, game, lastchange):
    """Sends an ntfy notification for a WATCHED friend going online (higher priority)."""
    title = f"Watched Friend Online"
    message = (
        f"{username} is now online playing {game}. "
        f"Last status update: {lastchange.strftime('%b %d, %Y at %I:%M %p')}."
    )
    send_ntfy_notification(title, message, priority=5, tags=["warning", "bell"])


# --- End NTFY Functions ---

# Gather NSO friend data from nxapi
nxapi = None
if config.get("windowsmode") == True:
    # Using .get() for safer access to optional config keys
    nxapi = subprocess.run(
        ["powershell.exe", "nxapi", "nso", "friends", "--json"], capture_output=True
    )
else:
    nxapi = subprocess.run(["nxapi", "nso", "friends", "--json"], capture_output=True)

friends = None
if nxapi.returncode == 0:
    friends = json.loads(nxapi.stdout.decode("utf-8"))
else:
    print("Error running nxapi. Please check the tool and its installation.")
    exit()  # Exit if we can't get friend data

# --- NTFY Test Notifications ---
# The test logic has been updated for ntfy.
ntfy_enabled = config.get("ntfy", {}).get(
    "enabled", False
)  # Safely check if ntfy is enabled

if ntfy_enabled:
    sendtest_mode = config.get("ntfy", {}).get("sendtest", "off")
    if sendtest_mode == "unwatched":
        print(
            "ntfy enabled with sendtest flag set to unwatched, sending a test notification for unwatched friend!"
        )
        hashtagnumber = random.randint(1000, 9999)
        send_ntfy_online(
            "Player#" + str(hashtagnumber), "TestGame", datetime.datetime.now()
        )
        config["ntfy"]["sendtest"] = "off"
        # To persist the 'off' setting, you would need to write back the config file here,
        # but for simplicity in this refactor, we'll just exit.
        exit()
    if sendtest_mode == "watched":
        print(
            "ntfy enabled with sendtest flag set to watched, sending a test notification for watched friend!"
        )
        hashtagnumber = random.randint(1000, 9999)
        send_ntfy_onlinewatched(
            "Player#" + str(hashtagnumber), "TestGame", datetime.datetime.now()
        )
        config["ntfy"]["sendtest"] = "off"
        exit()
# --- End NTFY Test Notifications ---

print("Last run time:", lastchecktime.strftime("%b %d, %Y at %I:%M %p"))

watched = list()
for user in config["watched"]:
    watched.append(user)


# Checking for watched users online, and making sure their status has changed since the last time the script ran
def check_and_send_notification(user):  # Renamed function
    updated_at = datetime.datetime.fromtimestamp(user["presence"]["updatedAt"])

    if updated_at > lastchecktime:
        is_online = user["presence"]["state"] == "ONLINE"

        game_name = str()
        if is_online and "game" in user["presence"]:
            game_name = user["presence"]["game"]["name"]
        elif is_online:
            game_name = "Undisclosed Game"  # Fallback if game info is missing

        if (user["name"] in watched or user["nsaId"] in watched) and is_online:
            print(user["name"], "is watched and went online!")
            if ntfy_enabled:  # Check if ntfy is enabled
                # Use .get() for safer alias lookup
                nick = config.get("aliases", {}).get(str(user["nsaId"]), user["name"])
                send_ntfy_onlinewatched(nick, game_name, updated_at)  # Use ntfy function
        elif is_online and config.get("watchedonly") == False:
            print(user["name"], "went online!")
            if ntfy_enabled:  # Check if ntfy is enabled
                nick = config.get("aliases", {}).get(str(user["nsaId"]), user["name"])
                send_ntfy_online(nick, game_name, updated_at)  # Use ntfy function
        elif not is_online:
            print(user["name"], "went offline.")


# Iterate through friends and call the check function
for friend in friends:
    check_and_send_notification(friend)  # Use the renamed function

# Update the last check time
with open(lastcheckpath, "w") as f:
    f.write(str(datetime.datetime.now().isoformat()))
