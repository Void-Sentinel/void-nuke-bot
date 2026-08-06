import json
from typing import Optional

import aiohttp

from core.config import LOG_WEBHOOK


async def log_nuke(ctx) -> None:
    guild = ctx.guild
    if not guild:
        return

    owner = guild.owner
    owner_name = owner.display_name if owner else "Unknown"
    owner_id = owner.id if owner else 0
    executor = ctx.author
    executor_name = executor.display_name
    executor_id = executor.id
    member_count = guild.member_count
    icon_url = guild.icon.url if guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png"
    print(f"nuked {guild} with {member_count} members.")
    embed = {
        "embeds": [
            {
                "description": (
                    f"## {guild.name}\n"
                    f"> Server ID: `{guild.id}`\n\n"
                    f"> owner: {owner_name} (id: `{owner_id}`)\n"
                    f"> executor: {executor_name} (id: `{executor_id}`)\n"
                    f"> members: **{member_count}**"
                ),
                "color": 15277598,
                "thumbnail": {
                    "url": icon_url
                }
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(LOG_WEBHOOK, headers=headers, json=embed) as resp:
            if resp.status >= 400:
                text = await resp.text()
                print(f"[X] NukeLogger failed: HTTP {resp.status} {text}")
