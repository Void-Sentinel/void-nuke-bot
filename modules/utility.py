import disnake
from disnake.ext import commands, tasks

from core.managers.counter import AttackCounter


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", description="Check ping")
    async def ping(self, ctx):
        message = await ctx.send("Pinging...")
        embed = disnake.Embed(title="Ping", color=disnake.Color.from_rgb(48, 49, 54))
        embed.add_field(
            name="Pong! 🏓", value=f"`{round(self.bot.latency * 1000)}ms`", inline=False
        )
        await message.edit(embed=embed)


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.attack_counter = AttackCounter()

    @commands.command()
    async def stats(self, ctx):
        total_attacks = self.attack_counter.get_total_attacks()
        daily_attacks = self.attack_counter.get_daily_attacks()
        avg_attack_duration = self.attack_counter.get_avg_attack_duration()

        embed = disnake.Embed(
            title="Attack Statistics", color=disnake.Color.from_rgb(48, 49, 54)
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
        self.leave_task.start()

    @tasks.loop(
        hours=4
    )  # Set the time, in hours/minutes/seconds, when you want the bot to leave servers.
    async def leave_task(self):
        for guild in self.bot.guilds:
            await guild.leave()


def setup(bot):
    bot.add_cog(Ping(bot))
    bot.add_cog(Stats(bot))
    bot.add_cog(Autoleave(bot))
