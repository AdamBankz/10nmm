import asyncio
import json
import websockets
import requests
import re
import colorama


# Replace with your actual bot token and channel ID
TOKEN = ""
CHANNEL_ID1 = 1408190325968736307  # Replace with your channel ID
CHANNEL_ID2 = 1408190362924748890
WEBHOOK_URL_1M = "https://discord.com/api/webhooks/1412224756836733008/3cBJdYh3FOz4PRHqbustGwovbCn7mWjeNkX2CtWMfOnI9PNdOYWNkLnVhtBVX1et5rwb"
WEBHOOK_URL_10M = "https://discord.com/api/webhooks/1412460089641799700/YQuQXgaKQpTv-M2gpt38NebCxcdkwoYGD77siQvoEiWtxS-rxfei5_mJwsCgTx9z04av"
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
API_URL = "https://job-id-whisperer.vercel.app/api/jobid"

def post_job_id(job_id_pc, job_id_mobile):
    payload = {"job_id_pc": job_id_pc,
               "job_id_mobile": job_id_mobile}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            print(Fore.GREEN + "POST Request sent successfully" + Fore.RESET)
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")    

def parse_game_notifier(text):
    data = {}
    
    # Regular expressions for each piece of information
    patterns = {
        'name': r"🏷️ Name\n\*\*(.*?)\*\*",
        'money_per_sec': r"💰 Money per sec\n\*\*(.*?)\*\*",
        'players': r"👥 Players\n\*\*(.*?)\*\*",
        'join_link': r"Join Link\n\[Click to Join\]\((.*?)\)",
        'job_id_mobile': r"Job ID \(Mobile\)\n(.*?)\n",
        'job_id_pc': r"Job ID \(PC\)\n```(.*?)```",
        'join_script_pc': r"Join Script \(PC\)\n```lua\n(.*?)\n```"
    }
    
    # Iterate through the patterns and extract data
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            data[key] = match.group(1).strip()
    
    return data

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))

def send_to_webhook_10m(parsed_data: dict):
    """
    Sends parsed game data to a webhook as an embedded message.

    Args:
        parsed_data (dict): A dictionary containing the extracted game information.
    """
    # The webhook URL must be a valid URL, otherwise this will fail.
    if not WEBHOOK_URL_10M.startswith('http'):
        print("Error: WEBHOOK_URL is not set. Please replace 'YOUR_WEBHOOK_HERE' with a valid URL.")
        return

    # Create the embed structure
    embed = {
        "title": f"🏷️ {parsed_data.get('name', 'N/A')}",
        "color": 65280,  # A nice green color
        "fields": [
            {"name": "💰 Money per sec", "value": parsed_data.get('money_per_sec', 'N/A'), "inline": True},
            {"name": "👤 Players", "value": parsed_data.get('players', 'N/A'), "inline": True},
            {"name": "🆔 JobID (Mobile)", "value": f"```{parsed_data.get('job_id_mobile', 'N/A')}```", "inline": True},
            {"name": "🆔 JobID (PC)", "value": f"```{parsed_data.get('job_id_pc', 'N/A')}```", "inline": True}]
    }
    
    data = {
        "embeds": [embed]
    }

    try:
        response = requests.post(WEBHOOK_URL_10M, json=data)
        if response.status_code == 204:
            print(Fore.BLUE + "[10M+ Brainrot Detected]" + Fore.GREEN + "[Forwarded Successfully]" + Fore.RESET)
        else:
            print(f"Failed to send message to webhook: {response.status_code} - {response.text}")
        post_job_id(parsed_data.get('job_id_pc', 'N/A'), parsed_data.get('job_id_mobile', 'N/A'))
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the message: {e}")
        
def send_to_webhook_1m(parsed_data: dict):
    """
    Sends parsed game data to a webhook as an embedded message.

    Args:
        parsed_data (dict): A dictionary containing the extracted game information.
    """
    # The webhook URL must be a valid URL, otherwise this will fail.
    if not WEBHOOK_URL_1M.startswith('http'):
        print("Error: WEBHOOK_URL is not set. Please replace 'YOUR_WEBHOOK_HERE' with a valid URL.")
        return

    # Create the embed structure
    embed = {
        "title": f"🏷️ {parsed_data.get('name', 'N/A')}",
        "color": 65280,  # A nice green color
        "fields": [
            {"name": "💰 Money per sec", "value": parsed_data.get('money_per_sec', 'N/A'), "inline": True},
            {"name": "👤 Players", "value": parsed_data.get('players', 'N/A'), "inline": True},
            {"name": "🔗 Join Link", "value": f"[Click to Join!]({parsed_data.get('join_link', '')})", "inline": False},
            {"name": "🆔 JobID (Mobile)", "value": f"```{parsed_data.get('job_id_mobile', 'N/A')}```", "inline": True},
            {"name": "🆔 JobID (PC)", "value": f"```{parsed_data.get('job_id_pc', 'N/A')}```", "inline": True}]
    }
    
    data = {
        "embeds": [embed]
    }

    try:
        response = requests.post(WEBHOOK_URL_1M, json=data)
        if response.status_code == 204:
            print(Fore.BLUE + "[1M+ Brainrot Detected]" + Fore.GREEN + "[Forwarded Successfully]" + Fore.RESET)
        else:
            print(f"Failed to send message to webhook: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the message: {e}")


async def listen():
    async with websockets.connect(GATEWAY_URL) as ws:
        hello = await ws.recv()
        hello_data = json.loads(hello)
        heartbeat_interval = hello_data['d']['heartbeat_interval']

        asyncio.create_task(heartbeat(ws, heartbeat_interval))

        identify_payload = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "my_library",
                    "$device": "my_library"
                },
                "intents": 33280,
                "presence": {
                    "status": "online"
                }
            }
        }
        await ws.send(json.dumps(identify_payload))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data['op'] == 0:
                event = data['t']
                event_data = data['d']

                if event == "MESSAGE_CREATE":
                    channel_id = int(event_data['channel_id'])
                    author = event_data['author']['username']
                    content = event_data.get('content', '')

                    # Handle embedded messages if content is empty
                    if not content and event_data.get('embeds'):
                        embeds = event_data['embeds']
                        embed_texts = []
                        for embed in embeds:
                            title = embed.get('title', '')
                            description = embed.get('description', '')
                            embed_texts.append(title)
                            embed_texts.append(description)
                            if 'fields' in embed:
                                for field in embed['fields']:
                                    embed_texts.append(field.get('name', ''))
                                    embed_texts.append(field.get('value', ''))
                        # Join all non-empty parts with newlines
                        content = '\n'.join(filter(None, embed_texts))

                    if channel_id == CHANNEL_ID1:
                        text_blocks = content.strip().split("Brainrot Notify | Dark Notifier")

                        parsed_data = []
                        for block in text_blocks:
                            if block.strip():
                                info = parse_game_notifier(block)
                                if info:
                                    parsed_data.append(info)

                        if parsed_data:
                            for i, entry in enumerate(parsed_data, 1):
                                pass  # Removed printing logic

                            send_to_webhook_1m(entry)

                    elif channel_id == CHANNEL_ID2:
                        text_blocks = content.strip().split("Brainrot Notify | Dark Notifier")

                        parsed_data = []
                        for block in text_blocks:
                            if block.strip():
                                info = parse_game_notifier(block)
                                if info:
                                    parsed_data.append(info)

                        if parsed_data:
                            for i, entry in enumerate(parsed_data, 1):
                                pass  # Removed printing logic

                            send_to_webhook_10m(entry)

    asyncio.run(listen())





