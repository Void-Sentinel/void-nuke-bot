import discord
from discord.ext import commands
from core.config import NAME, OWNER_IDS
from core.managers.usertypes import is_premium, premium_users, _db
import time


class Others(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="leaderboard", help="Show top 10 nukers")
    async def leaderboard(self, ctx: commands.Context):
        top = _db.get_top_nukers(10)
        if not top:
            await ctx.send("No nukes recorded yet.")
            return

        description_lines = []
        for idx, row in enumerate(top, start=1):
            user_id = row["user_id"]
            member_count = row["max_members"]
            guild_name = row["guild_name"]
            user = self.bot.get_user(user_id)
            username = user.name if user else f"Unknown User ({user_id})"
            description_lines.append(f"{idx}. {username}\n> {guild_name} - {member_count} members.")

        embed = discord.Embed(
            title=f"{NAME} - Leaderboard",
            description="\n".join(description_lines),
            color=15277598,
        )

        author_pos = 1
        for idx, row in enumerate(top, start=1):
            if row["user_id"] == ctx.author.id:
                author_pos = idx
                break
        embed.set_footer(text=f"You are in position {author_pos}")

        await ctx.send(embed=embed)

    @commands.command(name="userinfo", help="Show user info")
    async def userinfo(self, ctx: commands.Context, user: discord.User = None):
        target = user or ctx.author

        best = _db.get_user_best(target.id)
        if best:
            best_server = best["guild_name"]
            best_members = best["member_count"]
        else:
            best_server = "N/A"
            best_members = 0

        if is_premium(target.id):
            premium_status = "Premium"
            expires_at = premium_users.get(target.id)
            if expires_at:
                remaining = max(0, int(expires_at - time.time()))
                if remaining <= 0:
                    premium_remaining = "Expired"
                else:
                    days = remaining // 86400
                    hours = (remaining % 86400) // 3600
                    premium_remaining = f"{days}d {hours}h"
            else:
                premium_remaining = "N/A"
        elif target.id in OWNER_IDS:
            premium_status = "Owner"
            premium_remaining = "9 Years"
            best_server = f"{NAME}"
            best_members = "23456"
        else:
            premium_status = "Basic"
            premium_remaining = "N/A"

        embed = discord.Embed(
            title=f"{target.display_name}'s Info",
            color=15277598,
        )
        embed.add_field(name="Type", value=premium_status, inline=True)
        embed.add_field(name="Highest Server Nuked", value=f"{best_server} - {best_members} members.", inline=True)
        embed.add_field(name="Premium Remaining", value=premium_remaining, inline=False)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Others(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog(Others.__name__)
