import requests
import json

class Changer:
    def discord(text, token):
        try:
            r = requests.patch(
                url="https://discord.com/api/v9/users/@me",
                headers={"authorization": token},
                json={"bio": text},
            )
        except requests.exceptions.ConnectTimeout:
            return "noconnection"
        except:
            return "unknownerror"
        else:
            try:
                response = json.loads(r.content)
                if response.get("message", None) != None:
                    if "401" in response["message"]:
                        return "notvalidtoken"
                    else:
                        return "unknownerror"
                else:
                    return "success"
            except:
                return "unknownerror"

    def github(text, token):
        try:
            response = requests.patch(
                "https://api.github.com/user",
                headers={"Authorization": "Bearer " + token},
                data=json.dumps({"bio": text}),
            )
        except requests.exceptions.ConnectionError:
            return "noconnection"
        except:
            return "unknownerror"
        else:
            if response.status_code == 200:
                return "success"
            elif response.status_code == 304:
                return "cannotchange"
            elif response.status_code == 401 or response.status_code == 403:
                return "notvalidtoken"
            elif response.status_code == 422:
                return "toolong"
            else:
                return "unknownerror"
