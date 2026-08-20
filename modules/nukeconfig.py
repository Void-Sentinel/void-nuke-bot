import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from discord import ButtonStyle, TextStyle

from core.managers.config import NukeConfig


class SpamMessageModal(Modal, title="spam message"):
    message = TextInput(
        label="spam message",
        style=TextStyle.paragraph,
        placeholder="the message to spam during the nuke",
        max_length=2000,
        required=True,
    )

    def __init__(self, config: NukeConfig):
        super().__init__()
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        self.config.set_spam_message(self.message.value)
        await interaction.response.send_message(
            "spam message updated.", ephemeral=True
        )


class ChannelNamesModal(Modal, title="channel names"):
    name1 = TextInput(label="channel name 1", max_length=100, required=False)
    name2 = TextInput(label="channel name 2", max_length=100, required=False)
    name3 = TextInput(label="channel name 3", max_length=100, required=False)
    name4 = TextInput(label="channel name 4", max_length=100, required=False)
    name5 = TextInput(label="channel name 5", max_length=100, required=False)

    def __init__(self, config: NukeConfig):
        super().__init__()
        self.config = config
        existing = self.config.get_channel_names()
        for index, value in enumerate(existing[:5]):
            self.children[index].default = value

    async def on_submit(self, interaction: discord.Interaction):
        names = [child.value for child in self.children]
        self.config.set_channel_names(names)
        await interaction.response.send_message(
            "channel names updated (max 5).", ephemeral=True
        )


class GuildSettingsModal(Modal, title="guild settings"):
    server_name = TextInput(
        label="server name",
        max_length=100,
        required=True,
    )
    server_description = TextInput(
        label="server description",
        style=TextStyle.paragraph,
        max_length=1000,
        required=False,
    )

    def __init__(self, config: NukeConfig):
        super().__init__()
        self.config = config
        settings = self.config.get_guild_settings()
        self.server_name.default = settings.get("name", "")
        self.server_description.default = settings.get("description", "")

    async def on_submit(self, interaction: discord.Interaction):
        self.config.set_guild_settings(
            self.server_name.value, self.server_description.value
        )
        await interaction.response.send_message(
            "guild settings updated.", ephemeral=True
        )


class NukeConfigView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.config = NukeConfig()

    @Button(label="guild settings", style=ButtonStyle.blurple)
    async def guild_settings(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(GuildSettingsModal(self.config))

    @Button(label="channel names", style=ButtonStyle.blurple)
    async def channel_names(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(ChannelNamesModal(self.config))

    @Button(label="spam message", style=ButtonStyle.blurple)
    async def spam_message(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(SpamMessageModal(self.config))


class NukeConfigCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nukeconfig")
    async def nukeconfig(self, ctx: commands.Context):
        embed = discord.Embed(
            title="nvke editor.",
            description=(
                "use the buttons below to edit your nuke settings.\n"
                "-# please keep in mind that putting custom invites is forbidden and will be replaced"
            ),
        )
        view = NukeConfigView()
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(NukeConfigCmd(bot))
