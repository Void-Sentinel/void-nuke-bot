import disnake
from disnake.ext import commands


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


def setup(bot):
    bot.add_cog(Ping(bot))
