import requests
import time
import datetime

webhook_url = "https://discord.com/api/webhooks/1318211521524011179/b9rFC_MsWfZndQ0aoeUlol4q1O5Z4c8Alz7umWFSCdT1dHw-kUv23gXy0PDkODp4rr4y"
playerUUIDs = ["572133d1-a28e-4e8f-9af4-f43167f672a3", "28237084-488c-4cf0-a05b-947b9edd579e", "c25be85a-0d8a-478a-956e-9839ebd58cb3", "001ec66e-f729-4d7d-ace0-a243d49a857b", "0d768882-6006-4db5-a9c5-e9c96b00262d", "171e54c1-1918-44bc-8d2f-5beafb794358", "0c90fb66-49c5-4305-9b46-50bdf26aa4ff", "a1dcd9be-63a1-4728-aa6e-0bc60a341ea8", "2f14c1f2-8a80-4a44-801c-acd0df53db56", "74f70623-8a16-45bc-9002-f798fa08833b", "bb194f5a-6ca4-4f25-8393-4b0730b7207f", "68f9872a-f7bf-499e-94ed-ec0627a37698", "72eda40c-bc36-47cd-a03d-edddd14d0407", "90e58b5e-6044-4080-952b-8c2eb4f3399a", "e8c5415e-2a9b-4c47-aa5f-2ec2eaabc435", "43c05878-94ce-4650-ba6c-8f7fa783f1e2", "36ee3dc5-678c-4291-94f1-bcb098f64309", "faf778ca-ffae-4f8a-b7b9-b67a479ad071", "b3990d64-f6b6-4571-acea-185f8c529036"]
personalOpps = ["572133d1-a28e-4e8f-9af4-f43167f672a3"]
friend_data = {uuid: {"online": False, "last_logout": None} for uuid in playerUUIDs}
first_run = True
log_api_duration = True

print("Started Tracking Player Status")

def handle_rate_limit(response):
    if response.status_code == 429:  # Too Many Requests
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 10))
        wait_time = reset_time - time.time() + 1
        print(f"Rate limited. Waiting for {wait_time:.2f} seconds...")
        time.sleep(wait_time)  # Sleep until the rate limit is reset
        return True
    return False

def check_online_status():
    global first_run

    for uuid in playerUUIDs:
        try:
            start_time = time.time()

            response = requests.get(f'https://pitpanda.rocks/api/players/{uuid}')
            
            # rate limit handler for response from the API
            while handle_rate_limit(response):
                response = requests.get(f'https://pitpanda.rocks/api/players/{uuid}')

            data = response.json()

            end_time = time.time()
            api_call_duration = end_time - start_time

            if log_api_duration:
                print(f"{datetime.datetime.now()} - API call duration for the UUID {uuid}: {api_call_duration:.2f} seconds")

            if data["success"]:
                player_data = data.get("data", {})
                username = player_data.get("name", "Unknown")
                is_online = player_data.get("online", False)
                last_logout_timestamp = player_data.get("lastLogout")

                if first_run or is_online != friend_data[uuid]["online"]:
                    send_discord_notification(
                        f"{username} is {'now online!' if is_online else 'offline.'}",
                        username, 
                        parse_last_login(last_logout_timestamp), 
                        is_online, uuid
                    )

                if is_online and not friend_data[uuid]["online"]:
                    friend_data[uuid]["online"] = True
                    friend_data[uuid]["last_logout"] = None

                elif not is_online and friend_data[uuid]["online"]:
                    friend_data[uuid]["online"] = False

        except Exception as e:
            print(f"{datetime.datetime.now()} - Error checking status for the UUID {uuid}: {e}")

    first_run = False

def send_discord_notification(message, username, last_logout, is_online, uuid):
    try:
        formatted_last_logout = parse_and_format_last_logout(last_logout)

        content = ""
        if uuid in personalOpps:
            if is_online:
                content = "<@708023038226071654> hes online Retard PS I MADE THE FUCKING THINGY TO PRING YOU AUTOAMTICALLY ARE YOU HAPPY?!?! NIGGER"
            else: content = f"{username} is spawnlocked irl LOL <@708023038226071654> HES OFFLINE NIGGER"

        description = ""
        if not is_online: 
            description = f"**Last seen on Hypixel**\n*{formatted_last_logout}*"

        payload = {
            "content": content,
            "embeds": [
                {
                    "title": f"**{message}**",
                    "description": description,
                    "color": 65280 if is_online else 16711680,
                    "footer": {
                        "text": "PitHunter Status Tracker || Alerts"
                    }
                }
            ]
        }

        # Discord Webhook Section
        response = requests.post(webhook_url, json=payload)
        
        # rate limit handler for Discord webhook response
        while handle_rate_limit(response):
            response = requests.post(webhook_url, json=payload)

        time.sleep(1)  # 1s delay between requests

    except Exception as e:
        print(f"{datetime.datetime.now()} - Error sending Discord notification: {e}")

def parse_last_login(last_login_timestamp):
    if last_login_timestamp is not None:
        last_login_datetime = datetime.datetime.fromtimestamp(last_login_timestamp / 1000.0)
        return last_login_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return None

def parse_and_format_last_logout(last_logout):
    if last_logout:
        last_logout_datetime = datetime.datetime.strptime(last_logout, "%Y-%m-%d %H:%M:%S")
        formatted_last_logout = last_logout_datetime.strftime("%m/%d/%Y %I:%M%p")
        return formatted_last_logout
    return None

while True:
    try:
        check_online_status()
    except Exception as e:
        print(f"{datetime.datetime.now()} - Error in the main loop: {e}")

    time.sleep(5)  # delay between checking each player