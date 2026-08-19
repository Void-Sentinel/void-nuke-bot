import logging
import os

import disnake
from art import text2art
from disnake.ext import commands

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("V.", "v.", "!", "."),
            intents=disnake.Intents.all(),
        )

    async def on_ready(self):
        print(text2art("Void", font="fire_font-s"))
        print("""
        [#] Started Void NB
        [#] Developer: voby7 | github.com/Ramimnur20
              """)
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        self.load_cogs()
        self.print_invite_link()

    def load_cogs(self):
        for filename in os.listdir("src/cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded {filename[:-3]} loaded!")

    def print_invite_link(self):
        permissions = disnake.Permissions(permissions=8)
        invite_link = disnake.utils.oauth_url(self.user.id, permissions=permissions)
        logger.info(f"Invite link for the bot: {invite_link}")
