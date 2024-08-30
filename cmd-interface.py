import os
import shutil

print("Welcome to command line interface of automatic bio changer!")

def remove(path):
    if os.path.exists(path):
        os.remove(path)

while True:
    print("1. Reset password")
    print("2. Logout from all devices")
    print("3. Stop server")
    print("4. Factory reset")
    print("5. Reset port of webserver")
    print("6. Reinstall program / Update")
    print("7. Exit")
    a = input("Enter your choice: ")
    if a == "1":
        print("Reseting password...")
        remove("data/secret/password.txt")
        print("Password reseted! Now go to webserver, logout and set new password.")
    elif a == "2":
        print("Logging out from all devices...")
        with open("data/secret/sessions.json", "w") as f:
            f.write("[]")
        print("Loged out from all devices!")
    elif a == "3":
        print("Turning off server...")
        with open("data/realtime/restart.json", "w") as f:
            f.write('{"restart":true}')
        print("Server was turned off!")
    elif a == "4":
        print("Do you really want factory reset? (y/n)")
        a = input()
        if a == "y":
            print("Factory reseting...")
            shutil.rmtree("data")
            print("Factory reseted! Now you can start server again.")
    elif a == "5":
        print("Reseting port of webserver...")
        with open("port.json", "w") as f:
            f.write('{"firstRun": true}')
        print("Port of webserver was reseted! Now you can restart your server and set up new port.")
    elif a == "6":
        print("\033[91m!!! IMPORTANT !!!\033[0m")
        print("Do you have git installed? (y/n)")
        a = input()
        if a == "y":
            print("Reinstalling program ")
            files = os.listdir(".")
            EXCLUDE = ["data", "port.json"]
            for f in files:
                if f in EXCLUDE: continue

                if os.path.isfile(f):
                    os.remove(f)
                else:
                    shutil.rmtree(f)

            os.mkdir("temp")
            os.system("git clone https://github.com/jzitnik-dev/automatic-bio-changer.git temp")

            filesTemp = os.listdir("temp")

            for f in filesTemp:
                if f in EXCLUDE: continue

                if os.path.isfile("temp/" + f):
                    shutil.copy("temp/" + f, f)
                else:
                    shutil.copytree("temp/" + f, f)

            shutil.rmtree("temp")

            print("Program reinstalled successfully! Now you can start webserver")
        else:
            print("Please install git first!")
    elif a == "7":
        print("Exiting...")
        break
    else:
        print("Invalid choice")
