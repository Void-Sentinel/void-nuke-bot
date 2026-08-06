from discord.ext import commands
from core.managers.usertypes import _db


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user}")
        guild_count = len(self.bot.guilds)
        print(f"Guild count: {guild_count}")

        if guild_count >= 99 or guild_count == 98:
            print("Leaving all guilds due to high guild count...")
            for guild in self.bot.guilds:
                try:
                    await guild.leave()
                    print(f"Left guild: {guild.name}")
                except Exception as e:
                    print(f"Failed to leave guild {guild.name}: {e}")
        elif guild_count >= 75:
            print("Leaving small guilds...")
            for guild in self.bot.guilds:
                if guild.member_count < 10:
                    try:
                        await guild.leave()
                        print(f"Left guild: {guild.name}")
                    except Exception as e:
                        print(f"Failed to leave guild {guild.name}: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if _db.is_user_blacklisted(guild.owner_id):
            await guild.leave()
            print(f"Left guild {guild.name} because owner {guild.owner_id} is blacklisted.")
            return

        if guild.member_count < 5:
            try:
                await guild.owner.send(
                    f"Left your server **{guild.name}** because it has less than 5 members."
                )
            except Exception:
                pass
            await guild.leave()
            print(f"Left guild {guild.name} due to low member count. ({guild.member_count} members)")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog(Events.__name__)
