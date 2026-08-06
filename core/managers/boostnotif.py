import discord
import aiohttp
from discord.ext import commands, tasks
from core.config import DEFAULT_BL_GUILD, RICH_CH, RICH_WEB
from core.managers.usertypes import set_premium, remove_premium

PREMIUM_DURATION = 14 * 24 * 60 * 60

GUILD_IDS = DEFAULT_BL_GUILD if isinstance(DEFAULT_BL_GUILD, list) else [DEFAULT_BL_GUILD]


class BoostNotif(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.boost_extension_loop.start()

    def cog_unload(self):
        self.boost_extension_loop.cancel()

    @tasks.loop(hours=24)
    async def boost_extension_loop(self):
        await self.bot.wait_until_ready()
        for guild_id in GUILD_IDS:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            for member in guild.members:
                if member.premium_since is not None:
                    set_premium(member.id, PREMIUM_DURATION)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.guild.id not in GUILD_IDS:
            return

        started_boosting = before.premium_since is None and after.premium_since is not None
        stopped_boosting = before.premium_since is not None and after.premium_since is None

        if not (started_boosting or stopped_boosting):
            return

        if started_boosting:
            set_premium(after.id, PREMIUM_DURATION)

        if stopped_boosting:
            remove_premium(after.id)
            await self.send_broke_embed(after)
            return

        if started_boosting:
            await self.send_rich_embed(after)

    async def send_rich_embed(self, user):
        embed = discord.Embed(
            description=f"## {user.name} is now RICH!\nThanks {user.name} for boosting the server, you got premium."
        )
        await self._send_embed(embed)

    async def send_broke_embed(self, user):
        embed = discord.Embed(
            description=f"## {user.name} is BROKE!\n{user.name} stopped boosting the server. premium revoked."
        )
        await self._send_embed(embed)

    async def _send_embed(self, embed):
        channel = self.bot.get_channel(RICH_CH)
        try:
            if channel:
                await channel.send(embed=embed)
                return
        except Exception:
            pass

        if RICH_WEB:
            await self._send_webhook(embed)

    async def _send_webhook(self, embed):
        payload = {
            "embeds": [
                {
                    "description": embed.description,
                    "color": embed.color.value if embed.color else 0
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(RICH_WEB, headers=headers, json=payload) as resp:
                if resp.status >= 400:
                    text = await resp.text()
                    print(f"[X] BoostNotif webhook failed: HTTP {resp.status} {text}")


async def setup(bot: commands.Bot):
    await bot.add_cog(BoostNotif(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog(BoostNotif.__name__)
