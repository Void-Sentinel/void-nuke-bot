import time

import discord
import random
from discord.ext import commands, tasks

from core.managers.counter import AttackCounter


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_random_ping_msg(self):
        with open("data/pings.txt", "r") as file:
            lines = [line.strip() for line in file if line.strip()]
        return random.choice(lines) if lines else "the void"

    @commands.command(name="ping", description="Check ping")
    async def ping(self, ctx):
        random_ping_msg = self.get_random_ping_msg()

        start = time.perf_counter()
        message = await ctx.send(
            f"it took `0ms` to ping **{random_ping_msg}** (edit: `0ms`)."
        )
        initial_ping = round((time.perf_counter() - start) * 1000)

        start = time.perf_counter()
        await message.edit(
            content=f"it took `{initial_ping}ms` to ping **{random_ping_msg}** (edit: `0ms`)."
        )
        edit_ping = round((time.perf_counter() - start) * 1000)

        await message.edit(
            content=f"it took `{initial_ping}ms` to ping **{random_ping_msg}** (edit: `{edit_ping}ms`)."
        )


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.attack_counter = AttackCounter()

    @commands.command()
    async def stats(self, ctx):
        total_attacks = self.attack_counter.get_total_attacks()
        daily_attacks = self.attack_counter.get_daily_attacks()
        avg_attack_duration = self.attack_counter.get_avg_attack_duration()

        embed = discord.Embed(
            title="Attack Statistics", color=discord.Color.from_rgb(48, 49, 54)
        )
        embed.add_field(name="Total attacks:", value=total_attacks, inline=False)
        embed.add_field(name="Today's attacks:", value=daily_attacks, inline=False)
        embed.add_field(
            name="Average attack duration (sec):",
            value=f"{avg_attack_duration:.2f}",
            inline=False,
        )

        await ctx.send(embed=embed)


class Autoleave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def leave_low_member_servers(self, threshold):
        to_leave = [
            guild for guild in self.bot.guilds if guild.member_count < threshold
        ]
        for guild in to_leave:
            try:
                await guild.leave()
            except discord.HTTPException:
                continue

    @tasks.loop(
        hours=4
    )  # Set the time, in hours/minutes/seconds, when you want the bot to leave servers.
    async def leave_task(self):
        guild_count = len(self.bot.guilds)

        if guild_count > 95:
            await self.leave_low_member_servers(50)
        elif guild_count > 75:
            await self.leave_low_member_servers(10)


async def setup(bot):
    await bot.add_cog(Ping(bot))
    await bot.add_cog(Stats(bot))
    autoleave = Autoleave(bot)
    await bot.add_cog(autoleave)
    autoleave.leave_task.start()
