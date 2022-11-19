#from dotenv import dotenv_values
import requests, json
from dotenv import dotenv_values

config = dotenv_values("../environment/allsky.env")
pushover_userKey = config['pushover_userKey']
pushover_token = config['pushover_token']
url = "https://api.pushover.net/1/messages.json"



def send_pushover_message(title, message, device=""):
    payload = json.dumps({
    "token": f"{pushover_token}",
    "user": f"{pushover_userKey}",
    "title": f"{title}",
    "message": f"{message}",
    "device": f"{device}"
    })

    headers = {
    'Content-Type': 'application/json'
    }

    proxies = {}
    files = []

    r = requests.post(url=url, data=payload, headers=headers, proxies=proxies, files=files)
    print(r.status_code)
    jsonText = json.loads(r.text)
    print(jsonText)

