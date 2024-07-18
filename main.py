from datetime import datetime, timedelta
import sys
import threading
import json
import time
import random
import os
from scripts.changer import Changer
from scripts.webserver import startWebServer

class Generator:
    @staticmethod
    def generateConfigjson():
        sampleconfig = {
            "template": "Random quote: $text\n\nMade using automatic bio changer by JZITNIK.",
            "updatingInMinutes": 2,
        }
        json.dump(sampleconfig, open("data/config/config.json", "w"))
        return sampleconfig

    @staticmethod
    def generateStringsjson():
        samplestrings = [
            "Something > Nothing",
            "Quality > Quantity",
        ]
        json.dump(samplestrings, open("data/config/strings.json", "w"))
        return samplestrings

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Warning: Folder {folder_path} was not found! Creating it.")

create_folder_if_not_exists("data");
create_folder_if_not_exists("data/config");
create_folder_if_not_exists("data/realtime");
create_folder_if_not_exists("data/secret");

# Load config.js
def loadConfigJs():
    global CONFIG
    try:
        CONFIG = json.load(open("data/config/config.json"))
    except FileNotFoundError:
        print("Warning: File data/config/config.json was not found! Generating sample one!")
        CONFIG = Generator.generateConfigjson()
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in data/config/config.json! Generating sample one!")
        CONFIG = Generator.generateConfigjson()
    if CONFIG.get("template", False) == False:
        print("Warning! Setting template is missing! Saving a default value!")
        CONFIG["template"] = "Random quote: $text\n\nMade using automatic bio changer!"
        json.dump(CONFIG, open("data/config/config.json", "w"))
    if CONFIG.get("updatingInMinutes", False) == False:
        print("Warning! Setting updatingInMinutes is missing! Saving a default value!")
        CONFIG["updatingInMinutes"] = 2
        json.dump(CONFIG, open("data/config/config.json", "w"))
loadConfigJs()
# Load tokens.json
try:
    TOKENS = json.load(open("data/config/tokens.json"))
except FileNotFoundError:
    print("Warning: File data/config/tokens.json was not found! Creating a empty one!")
    with open("data/config/tokens.json", "w") as f:
        f.write("{}")
    TOKENS = {}
except json.JSONDecodeError:
    print("Warning: Invalid JSON in data/config/tokens.json! Creating a empty one!")
    with open("data/config/tokens.json", "w") as f:
        f.write("{}")
    TOKENS = {}

# Load strings.json
def loadStringsJs():
    global STRINGS
    try:
        STRINGS = json.load(open("data/config/strings.json"))
    except FileNotFoundError:
        print(
            "Warning: File data/config/strings.json was not found! Generating sample one!"
        )
        STRINGS = Generator.generateStringsjson()
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in data/config/strings.json! Generating sample one!")
        STRINGS = Generator.generateStringsjson()
loadStringsJs()

# Reset values
json.dump({},open("data/realtime/data.json","w"))
with open("data/realtime/log.txt","w") as f: f.write("")
json.dump({},open("data/realtime/status.json","w"))
json.dump({},open("data/realtime/time.json","w"))


# Start webserver
startWebServer()

# Set
class Set:
    @staticmethod
    def addToLog(text):
        try:
            with open("data/realtime/log.txt","a") as f:
                time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                f.write(f"{time} {text}\n")
        except:
            print("Error while saving the log. Literally it is saved to a TEXT FILE! IDK your system is probably messed up...")
    @staticmethod
    def data(typestr, text):
        time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        currentData = json.load(open("data/realtime/data.json"))
        currentData[typestr] = {"status": "working", "change": time, "text": text}
        json.dump(currentData, open("data/realtime/data.json","w"))
        Set.addToLog(f"Success {typestr}: Bio was changed to: {text}")
    @staticmethod
    def tokenError(typestr):
        currentData = json.load(open("data/realtime/data.json"))
        currentData[typestr] = {"status": "tokenerror"}
        json.dump(currentData, open("data/realtime/data.json","w"))
        Set.addToLog(f"Error {typestr}: Token is invalid!")
    @staticmethod
    def error(typestr, errormsg):
        Set.addToLog(f"Error {typestr}: {errormsg}")
    @staticmethod
    def time(typestr, time):
        currentData = json.load(open("data/realtime/time.json"))
        current_datetime = datetime.now()
        delta = timedelta(seconds=time*60)
        new_datetime = current_datetime + delta
        currentData[typestr] = new_datetime.strftime("%d.%m.%Y %H:%M:%S")
        json.dump(currentData, open("data/realtime/time.json","w"))

# Changer
def getRandomString(app, i=0):
    LEN = {"discord": 190, "github" : 160}
    randomStr = random.choice(STRINGS)
    data = json.load(open("data/realtime/data.json"))
    if (data.get(app,{}).get("text",False) == randomStr):
        return getRandomString(app)
    if (len(CONFIG["template"].replace("$text", randomStr)) > LEN[app]):
        if (i <= 20):
            Set.addToLog(f"Warning {app}: Bio is too long! Selecting new random string.")
            return getRandomString(app, i + 1)
        else:
            Set.addToLog(f"Error {app}: It wasn't possible to select a bio that was shorter than {LEN[app]} characters in 20 attempts. Giving up.")
            return ""
    return randomStr


def discordChangerFunction():
    while True:
        try:
            text = getRandomString("discord")
            final = CONFIG["template"].replace("$text", text)
            response = Changer.discord(final, TOKENS["discord"])

            if response == "success":
                Set.data("discord", text)
            elif response == "notvalidtoken":
                Set.tokenError("discord")
            elif response == "noconnection":
                Set.error("discord", "Couldn't change bio on discord. No internet connection.")
            elif response == "unknownerror":
                Set.error("discord", "Couldn't change bio on discord. Unknown error.")
            Set.time("discord", CONFIG["updatingInMinutes"])
            time.sleep(CONFIG["updatingInMinutes"] * 60)
        except:
            Set.error("discord", "Internal error while changing bio on discord.")

discordChangerThread = threading.Thread(target=discordChangerFunction, daemon=True)
if "discord" in TOKENS.keys():
    discordChangerThread.start()


def githubChangerFunction():
    while True:
        try:
            text = getRandomString("github")
            final = CONFIG["template"].replace("$text", text)
            response = Changer.github(final, TOKENS["github"])

            if response == "success":
                Set.data("github", text)
            elif response == "notvalidtoken":
                Set.tokenError("github")
            elif response == "noconnection":
                Set.error("github", "Couldn't change bio on github. No internet connection.")
            elif response == "toolong":
                Set.error("github", "Couldn't change bio on github. Bio is too long.")
            elif response == "cannotchange":
                Set.error("github", "Couldn't change bio on github. Error occured!")
            elif response == "unknownerror":
                Set.error("github", "Couldn't change bio on github. Unknown error.")
            Set.time("github", CONFIG["updatingInMinutes"])
            time.sleep(CONFIG["updatingInMinutes"] * 60)
        except:
            Set.error("github", "Internal error while changing bio on github.")

githubChangerThread = threading.Thread(target=githubChangerFunction, daemon=True)
if "github" in TOKENS.keys():
    githubChangerThread.start()


# Status checker
def statusCheckerFunction():
    while True:
        try:
            status = {}
            if "discord" in TOKENS.keys(): status["discord"] = discordChangerThread.is_alive()
            if "github" in TOKENS.keys(): status["github"] = githubChangerThread.is_alive()
            json.dump(status, open("data/realtime/status.json","w"))
            time.sleep(5)
        except:
            Set.error("internal", "Exception in status checker. Status on website might not be accurate.")
statusCheckerThred = threading.Thread(target=statusCheckerFunction, daemon=True)
statusCheckerThred.start()


def configUpdater():
    while True:
        try:
            loadConfigJs()
            loadStringsJs()
            time.sleep(1)
        except:
            Set.error("internal", "Exception in config updater. Consider restarting automatic bio changer manually.")

configUpdaterThread = threading.Thread(target=configUpdater, daemon=True)
configUpdaterThread.start()
    

while True:
    try:
        time.sleep(5)
        data = json.load(open("data/realtime/restart.json"))
        if (data["restart"]):
            json.dump({}, open("data/realtime/restart.json", "w"))
            sys.exit()
    except:
        Set.error("internal", "Exception in stop checker. Stop functionality might not work properly.")
