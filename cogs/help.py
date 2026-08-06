import discord
from discord.ext import commands
from discord.ui import View, button
from core.config import NAME
from core.core import Errors


class HelpPaginator(View):
    def __init__(self, embeds):
        super().__init__(timeout=120)
        self.embeds = embeds
        self.index = 0

    async def update(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @button(label="◀️ Backward", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, b: discord.ui.Button):
        self.index = (self.index - 1) % len(self.embeds)
        await self.update(interaction)

    @button(label="Forward ▶️", style=discord.ButtonStyle.secondary)
    async def forward(self, interaction: discord.Interaction, b: discord.ui.Button):
        self.index = (self.index + 1) % len(self.embeds)
        await self.update(interaction)


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help", help="Show the command list or help for a specific command")
    async def help_command(self, ctx: commands.Context):
        args = ctx.message.content.split()
        if len(args) > 1:
            cmd_name = args[1].lstrip("!")
            command = self.bot.get_command(cmd_name)
            if command and not command.hidden:
                embed = Errors.send_cmd_help(command)
                await ctx.send(embed=embed)
                return
            await ctx.send(f"Command `{cmd_name}` not found.")
            return

        commands_list = []
        for command in sorted(self.bot.commands, key=lambda c: (c.name != "nuke", c.name)):
            commands_list.append(command)

        if not commands_list:
            await ctx.send("No commands available.")
            return

        pages = []
        chunk_size = 5
        for i in range(0, len(commands_list), chunk_size):
            chunk = commands_list[i:i + chunk_size]
            embed = discord.Embed(
                title=f"{NAME} - Command List",
                description="\n".join(
                    f"`!{cmd.name}` - {cmd.help or 'No description'}"
                    for cmd in chunk
                ),
            )
            pages.append(embed)

        if len(pages) == 1:
            await ctx.send(embed=pages[0])
        else:
            view = HelpPaginator(pages)
            await ctx.send(embed=pages[0], view=view)


async def setup(bot):
    await bot.add_cog(Utils(bot))


def teardown(bot):
    bot.remove_cog(Utils.__name__)
