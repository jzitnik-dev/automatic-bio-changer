import requests
import random
import time
import sys
import logging
import threading
import os
import json
import socket
from flask import Flask, request
from datetime import datetime
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
# Clear console
def clearConsole():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except:
        print("Error occurred while clearing console.")


try:
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")) as f:
        config = json.loads(f.read())
except FileNotFoundError:
    print("Fatal Error: File config.json was not found!")
    exit()

if (not isinstance(config["randomStrings"], list)):
    print("Fatal Error: Setting randomStrings must be a list with strings!")
    exit()
if (not isinstance(config["password"], str)):
    print("Fatal Error: Setting password must be a string!")
    exit()
if (not isinstance(config["textTemplate"], str)):
    print("Fatal Error: Setting textTemplate must be a string!")
    exit()
if (isinstance(config["updatingInMinutes"], float) or isinstance(config["updatingInMinutes"], int)):
    pass
else:
    print("Fatal Error: Setting textTemplate must be a string!")
    exit()
if ((not isinstance(config["webserver"], dict) and (not isinstance(config["webserver"], bool)))):
    print("Fatal Error: Setting webserver must be a dict or a boolean!")
    exit()
elif ((not isinstance(config["webserver"], bool)) and not isinstance(config["webserver"]["host"], str)):
    print("Fatal Error: Setting webserver host must be a string with ip address.")
    exit()
elif ((not isinstance(config["webserver"], bool)) and not isinstance(config["webserver"]["port"], int)):
    print("Fatal Error: Setting webserver port must be a int.")
    exit()
if (config["password"] == ""):
    print("Fatal Error: Password cannot be empty.")
    exit()
if (config["updatingInMinutes"] < 0.2):
    print("Fatal Error: For security reasons you cannot have updating less than 0.2 minutes.")
    exit()
if (config["webserver"]):
    if (is_port_in_use(config["webserver"]["port"])):
        print("Fatal Error: Provided port is used.")
        exit()

logInfo = ""
nowtext = "unknown"
lastChange = "unknown"
validToken = True



# WebServer
app = Flask('')
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

@app.route("/stopServer")
def stopS():
    passwd = request.args.get("password")
    if (passwd == config["password"]):
        def stopServerNow():
            print("The server will be shut down from the user interface.")
            time.sleep(5)
            os._exit(1)
        stop = threading.Thread(target=stopServerNow)
        stop.daemon = True
        stop.start()
        return "true"
    else:
        return "wrongpass"
@app.route("/logs")
def logs():
    if (validToken == False):
        return "notValidToken"
    else:
        if (logInfo == ""):
            return "No log available."
        else:
            return logInfo.replace("\n", "<br>")

@app.route("/status")
def status():
    if (validToken == False):
        return "notValidToken"
    else:
        returnVal = {
            "engine": textChanger.is_alive(),
            "services": {}
        }
        if returnVal["engine"] == False:
            for i in config["tokens"]:
                returnVal["services"][i] = False
        else:
            for i in config["tokens"]:
                value = config["tokens"][i]
                if (value == False): returnVal["services"][i] = False
                else: returnVal["services"][i] = True
        return json.dumps(returnVal)

@app.route("/changeText")
def change():
    if (validToken == False):
        return "notValidToken"
    else:
        passwd = request.args.get("password")
        if (passwd == config["password"]):
            changeText()
            print("Text was changed from webserver.")
            return "true"
        else:
            return "wrongpass"

@app.errorhandler(500)
def error500(e):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"pages", "500.html")) as f:
        return f.read()

@app.errorhandler(404)
def page_not_found(e):
    if (validToken == True):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"pages", "index.html")) as f:
            return f.read().replace("$nowText", nowtext).replace("$lastChange", lastChange)
    else:
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pages", "invalidToken.html")) as f:
            return f.read()


def webserverRun():
    if (config["webserver"] != False):
        app.run(host=config["webserver"]["host"],
                port=config["webserver"]["port"])
# Text changing
class Console:
    def error(message):
        global logInfo
        print(message)
        logInfo += lastChange+" "+message+"\n"
    def log(message):
        global logInfo
        logInfo += lastChange+" "+message+"\n"
    
class Change:
    def discord(text, justarandomtext):
        try:
            r = requests.patch(url="https://discord.com/api/v9/users/@me",headers={"authorization": config["tokens"]["discord"]}, json={"bio": text})
        except requests.exceptions.ConnectTimeout:
            Console.error("Discord: No internet connection.")
        else:
            response = json.loads(r.content)
            if (response.get("message", None) != None):
                if ("401" in response["message"]):
                    print("Discord: Token is invalid! Restart server.")
                    global validToken
                    validToken = False
                    sys.exit()
                else:
                    Console.error("Discord: unknown error")
            else:
                Console.log("Discord: Text was changed to: "+justarandomtext)
    
    def github(text, justarandomtext):
        try:
            response = requests.patch('https://api.github.com/user', headers={'Authorization': 'Bearer '+config["tokens"]["github"]}, data=json.dumps({"bio": text}))
        except requests.exceptions.ConnectionError:
            Console.error("Github: No internet connection.")
        else:
            if (response.status_code == 200):
                Console.log("Github: Text was changed to: "+justarandomtext)
            elif (response.status_code == 304):
                Console.error("Github: Bio cannot be changed!")
            elif (response.status_code ==401 or response.status_code == 403):
                print("Github: Token is invalid! Restart server.")
                global validToken
                validToken = False
                sys.exit();
            elif (response.status_code == 422):
                Console.log("Github: Your bio is probably too long. Please change your template or you strings.")
            else:
                Console.error("Github: unknown error "+str(response.status_code))

def changingText():
    while True:
        changeText()
        time.sleep(config["updatingInMinutes"] * 60)
def changeText():
    textNow = random.choice(config["randomStrings"])
    now = datetime.now()
    global lastChange
    lastChange = now.strftime("%d/%m/%Y %H:%M:%S")
    final = config["textTemplate"].replace("$text", textNow)

    # Discord
    if (config["tokens"].get("discord", False) == False):
        pass
    else:
        Change.discord(final, textNow)
    # Github
    if (config["tokens"].get("github", False) == False):
        pass
    else:
        Change.github(final, textNow)
    global nowtext
    nowtext = textNow




# Make Thread
textChanger = threading.Thread(target=changingText, daemon=True)
webserver = threading.Thread(target=webserverRun, daemon=True)

# Start
print("Starting text changer engine.")
textChanger.start()
if (config["webserver"] != False):
    print("Starting webserver.")
    webserver.start()

time.sleep(1)
# Cli interface
if (validToken == False):
    print("Click enter to stop the server.")
    input()
    sys.exit()
else:
    print("Starting cli interface...")
    time.sleep(2)
    clearConsole()
    while True:
        print("""Commands:
!stop Stop a server
!log Get log information
!current Get current bio
!clear Clear console
!change Change current text
!about About automatic bio changer
""")
        ins = input("Command: ").strip()
        if (ins == "!stop"):
            sys.exit()
        elif (ins == "!log"):
            clearConsole()
            print(logInfo)
        elif (ins == "!current"):
            clearConsole()
            print("---------------")
            print(config["textTemplate"].replace("$text", nowtext))
            print("---------------")
        elif (ins == "!clear"):
            clearConsole()
        elif (ins == "!change"):
            clearConsole()
            changeText()
            print("Text was changed.")
        elif (ins == "!about"):
            clearConsole()
            print("""Automatic bio changer is script written in python to automatically change your bio on supported platforms.
Created by JZITNIK
Github repository: https://github.com/JZITNIK-github/automatic-bio-changer
""")
        else:
            print(ins+" is not a valid command.")
