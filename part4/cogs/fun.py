import discord
from discord import app_commands
from discord.ext import commands

MET = "https://collectionapi.metmuseum.org/public/collection"


class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="작품", description="작품 번호로 미술관 작품을 보여 줘요")
    @app_commands.describe(number="작품 번호 (예: 436535)")
    @app_commands.rename(number="번호")
    async def artwork(self, interaction: discord.Interaction,
                      number: app_commands.Range[int, 1, 99_999_999]):
        await interaction.response.defer()
        art = await self.bot.fetch_json(f"{MET}/v1/objects/{number}")
        if art is None:
            await interaction.followup.send("그 번호의 작품이 없거나, 지금은 정보를 가져올 수 없어요.")
            return
        embed = discord.Embed(title=(art["title"] or "제목 없음")[:256],
                              description=art["artistDisplayName"] or "작가 미상")
        if art["primaryImageSmall"]:
            embed.set_image(url=art["primaryImageSmall"])
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
