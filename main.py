import os
import tracemalloc
from dotenv import load_dotenv
import discord
from discord.ext import commands
from core.events import Events
from core.core import Errors, setup_errors

tracemalloc.start()
load_dotenv()
# vibe coded bot bro!
#voby7isafemboyhahauwu
#n
#
# boiii so mango
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.token = os.getenv("DISCORD_TOKEN", "")

    async def setup_hook(self):
        from pathlib import Path
        cog_dirs = [Path(__file__).resolve().parent / "cogs"]

        for cog_dir in cog_dirs:
            for py_file in cog_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                module_name = f"{cog_dir.name}.{py_file.stem}"
                try:
                    await self.load_extension(module_name)
                    print(f"Loaded cog: {module_name}")
                except Exception as exc:
                    print(f"[X] Failed to load cog {module_name}: {exc}")

        await self.add_cog(Events(self))
        await setup_errors(self)
        from core.managers.usertypes import setup as usertypes_setup
        await usertypes_setup(self)

async def run_bot():
    bot = Bot()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("[!] DISCORD_TOKEN is not set in .env")
    await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
