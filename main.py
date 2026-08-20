import os

import discord
from art import text2art
from discord.ext import commands

from core.config.token import TOKEN
from core.config.config import NAME


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("V.", "v.", "!", "."),
            intents=discord.Intents.all(),
        )

    async def on_ready(self):
        print(text2art(NAME, font="fire_font-s"))
        print(f"""
        [#] Started {NAME} NB
        [#] Developer: voby7 | github.com/Ramimnur20
              """)
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.load_cogs()
        self.print_invite_link()

    async def load_cogs(self):
        for filename in os.listdir("modules"):
            if filename.endswith(".py") and not filename.startswith("__"):
                await self.load_extension(f"modules.{filename[:-3]}")
                print(f"Loaded {filename[:-3]} loaded!")

    def print_invite_link(self):
        invite_link = discord.utils.oauth_url(self.user.id, permissions=discord.Permissions(permissions=8))
        print(f"Invite link for the bot: {invite_link}")


def main():
    Bot().run(TOKEN)


if __name__ == "__main__":
    main()
