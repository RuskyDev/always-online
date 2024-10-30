import os
import json
import asyncio
import platform
import requests
import websockets
from colorama import init, Fore
init(autoreset=True)

with open('settings.json') as settings_file:
    settings = json.load(settings_file)

TOKEN = settings["TOKEN"]
if not TOKEN:
    print(f"{Fore.WHITE}[{Fore.LIGHTRED_EX}ERROR{Fore.WHITE}] We couldn't find a token inside settings.json Please add a token inside settings.json")
    input()

status_texts = settings["STATUS_TEXT"]
status_rotation_seconds = int(settings.get("STATUS_TEXT_ROTATION_SECONDS", 300))
status = settings.get("STATUS_TYPE", "online")

headers = {"Authorization": TOKEN, "Content-Type": "application/json"}

check_token = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers)
if check_token.status_code != 200:
    print(f"{Fore.WHITE}[{Fore.LIGHTRED_EX}ERROR{Fore.WHITE}] The token you provided might be invalid Please double check the token you entered in settings.json")
    input()

userinfo = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers).json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

async def Main(token, status, custom_status):
    async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
        start = json.loads(await ws.recv())
        heartbeat = start["d"]["heartbeat_interval"]

        auth = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "Windows 10",
                    "$browser": "Google Chrome",
                    "$device": "Windows",
                },
                "presence": {"status": status, "afk": False},
            },
        }
        await ws.send(json.dumps(auth))

        cstatus = {
            "op": 3,
            "d": {
                "since": 0,
                "activities": [
                    {
                        "type": 4,
                        "state": custom_status,
                        "name": "Custom Status",
                        "id": "custom",
                    }
                ],
                "status": status,
                "afk": False,
            },
        }
        await ws.send(json.dumps(cstatus))

        online = {"op": 1, "d": "None"}
        
        if len(json.dumps(online)) > 1048576:
            return
        else:
            await ws.send(json.dumps(online))

        await asyncio.sleep(heartbeat / 1000)

async def Run():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    print(f"{Fore.WHITE}[{Fore.LIGHTGREEN_EX}INFO{Fore.WHITE}] Logged in as {Fore.LIGHTGREEN_EX_EX}{username} {Fore.WHITE}({userid})")
    current_status_index = 0
    while True:
        custom_status = status_texts[current_status_index]
        await Main(TOKEN, status, custom_status)
        current_status_index = (current_status_index + 1) % len(status_texts)
        await asyncio.sleep(status_rotation_seconds)

asyncio.run(Run())
