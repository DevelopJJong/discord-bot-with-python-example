import discord
from discord import app_commands
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="도움말", description="봇의 명령어 목록을 보여 줘요")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="명령어 목록", color=0x5B6CF0)
        for cmd in self.bot.tree.get_commands():
            embed.add_field(name=f"/{cmd.name}", value=cmd.description or "설명 없음", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="새로고침", description="Cog를 다시 불러와요 (봇 주인 전용)")
    @app_commands.describe(name="cogs 폴더의 파일 이름 (예: fun)")
    @app_commands.rename(name="이름")
    async def reload(self, interaction: discord.Interaction, name: str):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message("봇 주인만 쓸 수 있어요.", ephemeral=True)
            return
        await self.bot.reload_extension(f"cogs.{name}")
        await interaction.response.send_message(f"cogs.{name}을 다시 불러왔어요.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
