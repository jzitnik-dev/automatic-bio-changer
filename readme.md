# Discord bio changer
Discord bio changer is program that will automatically change your Discord bio.
## Disclaimer
**This is against the DISCORD'S TERMS OF SERVICE**.

You can get banned from Discord.
**Use this program at your own risk.**

Do not spam the API to much or you will get banned.

## Features
1. Web interface
2. Cli interface
3. Custom bio template
4. Custom configuration

## Installation
You can install this program to you own server.

### 1. Clone this repository
```
git clone https://github.com/JZITNIK-github/discord-bio-changer
```

### 2. Go to src folder
```
cd custom-bio-changer/src
```

### 3. Install required libraries
```
pip install -r requirements.txt
```

### 4. Edit config.json
You need to configure the config.json file. More info [here](#configuration).

### 5. Run the server
```
python3 main.py
```
## Configuration
The configuration file: config.json
### randomStrings
randomStrings key should have a list with strings that will be randomly chosen.
### textTemplate
textTemplate key should have a string that will be used as the template.
\$text will be replaced with the randomly chosen text from randomStrings.
### token
token key should have a string with you discord token.
**Do not share this code with anyone.**
If you leaked your discord token, change your password immediately!
#### How to get your token
[Here is the link to the tutorial.](https://www.androidauthority.com/get-discord-token-3149920/)
### password
password is used to change text or shutdown the server from Web interface.
**Do not share this password with anyone.**
### updatingInMinutes
updatingInMinutes key sould have how many times should bio be updated.

If you type 2, text will be updated every 2 minutes.

Do not put this number under 0.5 minutes or you'll be probably banned for spamming the discord API.
### webserver
webserver key sould have a information about the webserver

If you don't want to have a webserver, set it to false.

If you want to have a webserver, make it dictionary with keys host and port.

Host is ip address of the webserver. default: 0.0.0.0 (all ip addresses of the server)

Port is the port number of the webserver. 0.0.0.0:**80**
