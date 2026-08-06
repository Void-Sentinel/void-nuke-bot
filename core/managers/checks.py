from discord.ext import commands
from core.config import OWNER_IDS
from core.utils.usertypes import is_premium as _is_premium


def is_owner():
    async def predicate(ctx: commands.Context):
        return ctx.author.id in OWNER_IDS
    return commands.check(predicate)


def is_premium():
    async def predicate(ctx: commands.Context):
        if not _is_premium(ctx.author.id):
            raise commands.CheckFailure("You need premium to use this command.")
        return True
    return commands.check(predicate)
