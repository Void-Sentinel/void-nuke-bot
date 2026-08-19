from disnake.ext import commands, tasks

# The simplest auto-leaver on planet earth.


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
    bot.add_cog(Autoleave(bot))
