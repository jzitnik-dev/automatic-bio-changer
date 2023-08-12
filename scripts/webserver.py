import json
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import socket
import threading
import os
import random



PORTFILE = "port.json"

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def setPort():
    port = input("Enter a port for the web server: ")
    if (is_port_in_use(int(port))):
        print("Port is in use! Select another port!")
        return setPort()
    return port

def startWebServer():
    def restartProgram():
        with open("data/realtime/restart.json", "w") as f:
            f.write('{"restart":true}')
    try:
        js = json.load(open(PORTFILE, "r"))
    except json.decoder.JSONDecodeError:
        print(f"Warning: File {PORTFILE} is not valid JSON file. Generating sample one!")
        sample = {"port": setPort()}
        with open(PORTFILE, "w") as f:
            f.write(json.dumps(sample))
        PORT = sample["port"]
    except FileNotFoundError:
        print(f"Warning: File {PORTFILE} was not found. Generating sample one!")
        sample = {"port": setPort()}
        with open(PORTFILE, "w") as f:
            f.write(json.dumps(sample))
        PORT = sample["port"]
    else:
        try:
            if (js.get("firstRun",False) == True):
                print("Let's setup a web server")
                sample = {"port": setPort()}
                with open(PORTFILE, "w") as f:
                    f.write(json.dumps(sample))
                PORT = sample["port"]
            elif is_port_in_use(int(js["port"])):
                print("Error: Port is in use. Select port that is not in use!")
                PORT = setPort()
                sample = {"port": PORT}
                with open(PORTFILE, "w") as f:
                    f.write(json.dumps(sample))
            else:
                PORT = js["port"]
        except KeyError:
            print(f"Fatal Error: Config file {PORTFILE} is invalid! Generating a sample one!")
            sample = {"port": setPort()}
            with open(PORTFILE, "w") as f:
                f.write(json.dumps(sample))
            PORT = sample["port"]

    if not os.path.exists("data/secret/sessions.json"):
        with open("data/secret/sessions.json", "w") as f:
            f.write("[]")
    with open("data/realtime/restart.json", "w") as f:
        f.write('{"restart":false}')
            
    

    app = Flask("")
    app.logger.disabled = True
    log = logging.getLogger("werkzeug")
    log.disabled = True


    # Routes

    @app.route("/")
    def index():
        if not os.path.exists("data/secret/password.txt"):
            with open("website/firsttime.html", "r") as f:
                return f.read()
        else:
            with open("website/login.html", "r") as f:
                return f.read()

    @app.route("/dashboard")
    def dashboard():
        with open("website/dashboard.html", "r") as f:
            return f.read()
        
    @app.route("/api/logout")
    def logout():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))

            if (session in sessions):
                sessions.remove(session)
                json.dump(sessions, open("data/secret/sessions.json", "w"))
                return jsonify({"message":"success"}), 200
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500
    @app.route("/api/setPassword", methods=['GET','POST'])
    def setPassword():
        try:
            data = request.json

            PASSWORD = data["password"]

            hashed_password = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt())

            with open("data/secret/password.txt", "w") as f:
                f.write(hashed_password.decode('utf-8'))

            return jsonify({"message":"success"}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/api/setTokens", methods=['GET','POST'])
    def setTokens():
        try:
            data = request.json

            SESSION = data["sessionKey"]
            DATA = data["data"]

            

            sessions = json.load(open("data/secret/sessions.json"))

            if SESSION in sessions:
                json.dump(DATA, open("data/config/tokens.json", "w"))

                restartProgram()
                return jsonify({"message":"restarting"})
            else:
                return jsonify({"message":"wrongsession"}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/api/setStrings", methods=['GET','POST'])
    def setStrings():
        try:
            data = request.json

            SESSION = data["sessionKey"]
            DATA = data["data"]

            

            sessions = json.load(open("data/secret/sessions.json"))

            if SESSION in sessions:
                json.dump(DATA, open("data/config/strings.json", "w"))
                
                return jsonify({"message":"success"})
            else:
                return jsonify({"message":"wrongsession"}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/api/setUpdating", methods=['GET','POST'])
    def setUpdating():
        try:
            data = request.json

            SESSION = data["sessionKey"]
            DATA = data["data"]

            

            sessions = json.load(open("data/secret/sessions.json"))

            if SESSION in sessions:
                config = json.load(open("data/config/config.json"))
                config["updatingInMinutes"] = DATA
                json.dump(config, open("data/config/config.json", "w"))

                return jsonify({"message":"success"})
            else:
                return jsonify({"message":"wrongsession"}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/api/setTemplate", methods=['GET','POST'])
    def setTemplate():
        try:
            data = request.json

            SESSION = data["sessionKey"]
            DATA = data["data"]

            

            sessions = json.load(open("data/secret/sessions.json"))

            if SESSION in sessions:
                config = json.load(open("data/config/config.json"))
                config["template"] = DATA
                json.dump(config, open("data/config/config.json", "w"))

                return jsonify({"message":"success"})
            else:
                return jsonify({"message":"wrongsession"}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/api/getInfo")
    def getInfo():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return open("data/realtime/data.json").read()
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/api/getStrings")
    def getStrings():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return json.dumps({"data": json.load(open("data/config/strings.json"))})
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route("/api/getTemplate")
    def getTemplate():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return {"data": json.load(open("data/config/config.json"))["template"]}
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route("/api/getUpdating")
    def getUpdating():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return {"data": json.load(open("data/config/config.json"))["updatingInMinutes"]}
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/api/getStatus")
    def getStatus():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return open("data/realtime/status.json").read()
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/api/running")
    def running():
        return "running"
            
    @app.route("/api/getTokens")
    def getTokens():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return {"data": open("data/config/tokens.json").read()}
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500



    @app.route("/api/getLogs")
    def getLogs():
        try:
            session = request.headers.get('session')
            sessions = json.load(open("data/secret/sessions.json"))
            if session in sessions:
                return {"data": open("data/realtime/log.txt").read()}
            else:
                return jsonify({"message":"wrongsession"}), 200


        except Exception as e:
            return jsonify({'error': str(e)}), 500

        
    @app.route("/api/testSession", methods=['GET','POST'])
    def testSession():
        try:
            data = request.json

            session = data["sessionKey"]

            sessions = json.load(open("data/secret/sessions.json"))

            if session in sessions:
                return jsonify({"message":"success"}), 200
            else:
                return jsonify({"message":"wrongsession"}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route("/api/login", methods=['GET','POST'])
    def login():
        try:
            def createSession(sessions):
                CONST = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
                session = ""
                for i in range(0,32):
                    session += random.choice(CONST)
                if session in sessions:
                    return createSession(sessions)
                return session
            
            data = request.json

            PASSWORD = data["password"]

            def check_password(input_password, hashed_password):
                return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


            with open("data/secret/password.txt", "r", encoding="utf-8") as f:
                HASHED = f.read().strip()

            if (check_password(PASSWORD, HASHED.encode('utf-8'))):

                sessions = json.load(open("data/secret/sessions.json"))

                session = createSession(sessions)

                sessions.append(session)

                json.dump(sessions, open("data/secret/sessions.json", "w"))
                
                return jsonify({"message":"success", "sessionKey": session}), 200
            else:
                return jsonify({"message":"wrongpass"}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500


    print(f"Starting web server on port {PORT}.")

    def startWeb():
        app.run(host="0.0.0.0", port=PORT)

    webserver = threading.Thread(target=startWeb, daemon=True)
    webserver.start()
