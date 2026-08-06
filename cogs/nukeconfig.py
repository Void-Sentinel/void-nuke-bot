#premuim users only
import re
import aiosqlite
from discord.ext import commands
from discord import app_commands, ui, Embed, TextStyle, Interaction
from core.config import SERVER_INVITE
from core.managers.usertypes import is_premium
import discord
from core.config import NAME
DB_PATH = "nuker.db"

INVITE_PATTERN = re.compile(
    r"(https?://)?(www\.)?(discord\.gg|discord\.me|discordapp\.com/invite)/[^\s]+",
    re.IGNORECASE,
)


def _replace_invites(text: str, user_id: int = None) -> str:
    if user_id and is_premium(user_id):
        return text
    return INVITE_PATTERN.sub(SERVER_INVITE, text)


class ChannelNamesModal(ui.Modal, title="Channel Names Configuration"):
    name1 = ui.TextInput(
        label="Channel Name 1",
        max_length=100,
        required=False,
        placeholder="nuked",
    )
    name2 = ui.TextInput(
        label="Channel Name 2",
        max_length=100,
        required=False,
        placeholder="raid",
    )
    name3 = ui.TextInput(
        label="Channel Name 3",
        max_length=100,
        required=False,
        placeholder="destroyed",
    )
    name4 = ui.TextInput(
        label="Channel Name 4",
        max_length=100,
        required=False,
    )
    name5 = ui.TextInput(
        label="Channel Name 5",
        max_length=100,
        required=False,
    )

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: Interaction):
        names = [
            self.name1.value,
            self.name2.value,
            self.name3.value,
            self.name4.value,
            self.name5.value,
        ]
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO user_config (user_id, channel_name_1, channel_name_2, channel_name_3, channel_name_4, channel_name_5)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    channel_name_1 = excluded.channel_name_1,
                    channel_name_2 = excluded.channel_name_2,
                    channel_name_3 = excluded.channel_name_3,
                    channel_name_4 = excluded.channel_name_4,
                    channel_name_5 = excluded.channel_name_5
                """,
                (self.user_id, *names),
            )
            await db.commit()
        await interaction.response.send_message("Channel names updated.", ephemeral=True)


class SpamMessageModal(ui.Modal, title="Spam Message Configuration"):
    content = ui.TextInput(
        label="Spam Message Content",
        style=TextStyle.paragraph,
        required=False,
        placeholder=f"@everyone Nuked by {NAME}",
    )

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: Interaction):
        cleaned = _replace_invites(self.content.value or "", self.user_id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO user_config (user_id, spam_message)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET spam_message = excluded.spam_message
                """,
                (self.user_id, cleaned),
            )
            await db.commit()
        await interaction.response.send_message("Spam message updated.", ephemeral=True)


class ServerSettingsModal(ui.Modal, title="Server Settings Configuration"):
    server_name = ui.TextInput(
        label="New Server Name",
        max_length=100,
        required=False,
        placeholder=f"Owned by {NAME}",
    )
    server_description = ui.TextInput(
        label="New Server Description",
        style=TextStyle.paragraph,
        required=False,
        placeholder="This place has been obliterated...",
    )

    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction: Interaction):
        name = self.server_name.value or ""
        description = self.server_description.value or ""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO user_config (user_id, server_name, server_description)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    server_name = excluded.server_name,
                    server_description = excluded.server_description
                """,
                (self.user_id, name, description),
            )
            await db.commit()
        await interaction.response.send_message("Server settings updated.", ephemeral=True)


class ConfigView(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id

    @ui.button(label="Channel Names", style=discord.ButtonStyle.secondary)
    async def channel_names(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(ChannelNamesModal(self.user_id))

    @ui.button(label="Spam Message", style=discord.ButtonStyle.secondary)
    async def spam_message(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(SpamMessageModal(self.user_id))

    @ui.button(label="Server Settings", style=discord.ButtonStyle.secondary)
    async def server_settings(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_modal(ServerSettingsModal(self.user_id))


class NukeConfig(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="edit_config", aliases=["editconfig", "config"], help="Edit your nuke configuration")
    async def edit_config(self, ctx: commands.Context):
        embed = Embed(
            title="Nuke Configuration Editor",
            description="Click a button below to configure your nuke settings.",
            color=15277598,
        )
        view = ConfigView(ctx.author.id)
        await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_config (
                user_id INTEGER PRIMARY KEY,
                channel_name_1 TEXT,
                channel_name_2 TEXT,
                channel_name_3 TEXT,
                channel_name_4 TEXT,
                channel_name_5 TEXT,
                channel_name_6 TEXT,
                spam_message TEXT,
                server_name TEXT,
                server_description TEXT
            )
            """
        )
        await db.commit()
    await bot.add_cog(NukeConfig(bot))


def teardown(bot: commands.Bot):
    bot.remove_cog(NukeConfig.__name__)


async def get_user_nuke_config(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT channel_name_1, channel_name_2, channel_name_3, channel_name_4, channel_name_5, spam_message, server_name, server_description FROM user_config WHERE user_id = ?",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
    if not row:
        return {}
    return {
        "channel_names": [n for n in row[:5] if n],
        "spam_message": row[5] or "",
        "server_name": row[6] or "",
        "server_description": row[7] or "",
    }
