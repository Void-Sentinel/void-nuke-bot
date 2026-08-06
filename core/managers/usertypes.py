import time
import aiosqlite
from discord.ext import commands
from core.config import OWNER_IDS, DEFAULT_BL_GUILD

DB_PATH = "nuker.db"

premium_users: dict = {}


class BlacklistDB:
    def __init__(self):
        self._blacklist: set = set(DEFAULT_BL_GUILD or [])
        self._user_blacklist: set = set()

    async def init(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS blacklisted_guilds (guild_id INTEGER PRIMARY KEY)"
            )
            await db.execute(
                "CREATE TABLE IF NOT EXISTS blacklisted_users (user_id INTEGER PRIMARY KEY)"
            )
            await db.execute(
                """CREATE TABLE IF NOT EXISTS nuke_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    guild_name TEXT,
                    member_count INTEGER,
                    timestamp REAL NOT NULL
                )"""
            )
            await db.commit()
            async with db.execute("SELECT guild_id FROM blacklisted_guilds") as cursor:
                async for row in cursor:
                    self._blacklist.add(row[0])
            async with db.execute("SELECT user_id FROM blacklisted_users") as cursor:
                async for row in cursor:
                    self._user_blacklist.add(row[0])

    async def log_nuke(self, user_id: int, guild_id: int, guild_name: str, member_count: int):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO nuke_logs (user_id, guild_id, guild_name, member_count, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, guild_id, guild_name, member_count, time.time()),
            )
            await db.commit()

    def get_top_nukers(self, limit: int = 10):
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """SELECT user_id, MAX(member_count) as max_members, guild_name, guild_id
               FROM nuke_logs
               GROUP BY user_id
               ORDER BY max_members DESC
               LIMIT ?""",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_user_best(self, user_id: int):
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT guild_name, member_count FROM nuke_logs WHERE user_id = ? ORDER BY member_count DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    async def add_guild(self, guild_id: int):
        self._blacklist.add(guild_id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO blacklisted_guilds (guild_id) VALUES (?)",
                (guild_id,),
            )
            await db.commit()

    async def remove_guild(self, guild_id: int):
        self._blacklist.discard(guild_id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "DELETE FROM blacklisted_guilds WHERE guild_id = ?",
                (guild_id,),
            )
            await db.commit()

    def is_guild_blacklisted(self, guild_id: int) -> bool:
        return guild_id in self._blacklist

    async def add_user(self, user_id: int):
        self._user_blacklist.add(user_id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR IGNORE INTO blacklisted_users (user_id) VALUES (?)",
                (user_id,),
            )
            await db.commit()

    async def remove_user(self, user_id: int):
        self._user_blacklist.discard(user_id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "DELETE FROM blacklisted_users WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()

    def is_user_blacklisted(self, user_id: int) -> bool:
        return user_id in self._user_blacklist


_db = BlacklistDB()


def is_premium(user_id: int) -> bool:
    expires_at = premium_users.get(user_id)
    if expires_at is None:
        return False
    if time.time() > expires_at:
        del premium_users[user_id]
        return False
    return True


def set_premium(user_id: int, duration_seconds: int):
    premium_users[user_id] = time.time() + duration_seconds


def remove_premium(user_id: int):
    premium_users.pop(user_id, None)


def premium_cooldown(rate: int, per: float):
    def decorator(command):
        cooldowns: dict = {}

        async def predicate(ctx: commands.Context):
            user_id = ctx.author.id
            now = time.time()
            effective_per = per * 0.75 if is_premium(user_id) else per

            if user_id in cooldowns:
                last_used, remaining = cooldowns[user_id]
                if now < last_used + effective_per:
                    retry_after = (last_used + effective_per) - now
                    raise commands.CommandOnCooldown(
                        commands.Cooldown(rate, per), retry_after
                    )

            cooldowns[user_id] = (now, effective_per)
            return True

        command.checks.append(predicate)
        return command

    return decorator


def blacklisted_command():
    async def predicate(ctx: commands.Context):
        if ctx.guild and _db.is_guild_blacklisted(ctx.guild.id):
            raise commands.CheckFailure("This guild is blacklisted.")
        if _db.is_user_blacklisted(ctx.author.id):
            raise commands.CheckFailure("You are blacklisted from using this command.")
        return True
    return commands.check(predicate)


async def setup(bot: commands.Bot):
    await _db.init()


def teardown(bot: commands.Bot):
    pass
