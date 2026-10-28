import datetime
import logging
from pathlib import Path

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks

log = logging.getLogger("mybot")
KST = datetime.timezone(datetime.timedelta(hours=9))
BACKUP_DIR = Path(__file__).parent.parent / "backups"      # mybot/backups
KEEP = 7        # 백업을 몇 개까지 남길지 (미션 6)


def remove_old_backups(keep: int = KEEP) -> list:
    """가장 최근 keep개만 남기고 오래된 백업을 지운다. 지운 파일 목록을 돌려준다."""
    files = sorted(BACKUP_DIR.glob("bot-*.db"))       # 이름에 날짜가 있어 이름순 = 날짜순
    old = files[:-keep]
    for path in old:
        path.unlink()
    return old


class DeleteConfirm(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="삭제", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = interaction.client.db
        cursor = await db.execute("DELETE FROM attendance WHERE user_id = ?", (interaction.user.id,))
        await db.commit()
        text = "출석 기록을 모두 지웠어요." if cursor.rowcount else "지울 기록이 없어요."
        await interaction.response.edit_message(content=text, view=None)
        self.stop()

    @discord.ui.button(label="취소", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="취소했어요. 아무것도 지우지 않았어요.", view=None)
        self.stop()


class Ops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.daily_backup.start()

    async def cog_unload(self):
        self.daily_backup.cancel()

    async def make_backup(self) -> Path:
        BACKUP_DIR.mkdir(exist_ok=True)
        path = BACKUP_DIR / datetime.datetime.now(KST).strftime("bot-%Y%m%d-%H%M%S.db")
        async with aiosqlite.connect(path) as target:
            await self.bot.db.backup(target)
        return path

    @tasks.loop(time=datetime.time(hour=4, tzinfo=KST))
    async def daily_backup(self):
        path = await self.make_backup()
        removed = remove_old_backups()
        log.info("백업 완료: %s (오래된 백업 %d개 정리)", path.name, len(removed))

    @app_commands.command(name="백업", description="지금 바로 데이터베이스를 백업해요 (관리자 전용)")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def backup_now(self, interaction: discord.Interaction):
        path = await self.make_backup()
        removed = remove_old_backups()
        await interaction.response.send_message(
            f"{path.name} 로 백업했어요. 정리한 옛 백업: {len(removed)}개", ephemeral=True)

    @app_commands.command(name="상태", description="봇이 잘 돌아가고 있는지 보여 줘요")
    async def status(self, interaction: discord.Interaction):
        uptime = discord.utils.utcnow() - self.bot.started_at
        hours, rest = divmod(int(uptime.total_seconds()), 3600)
        embed = discord.Embed(title="봇 상태", color=0x22C3A6)
        embed.add_field(name="켜져 있던 시간", value=f"{hours}시간 {rest // 60}분")
        embed.add_field(name="응답 속도", value=f"{self.bot.latency * 1000:.0f}ms")
        embed.add_field(name="서버 수", value=f"{len(self.bot.guilds)}곳")
        embed.add_field(name="켜진 시각", value=discord.utils.format_dt(self.bot.started_at, "F"), inline=False)
        await interaction.response.send_message(embed=embed)
        log.info("/상태 사용: user_id=%s", interaction.user.id)

    @app_commands.command(name="내정보삭제", description="봇에 저장된 내 출석 기록을 지워요")
    async def delete_my_data(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "정말 내 출석 기록(포인트 포함)을 지울까요? 지우면 되돌릴 수 없어요.",
            view=DeleteConfirm(), ephemeral=True)


    @app_commands.command(name="내정보", description="봇에 저장된 내 정보를 보여 줘요")
    async def my_data(self, interaction: discord.Interaction):
        async with self.bot.db.execute(
                "SELECT name, points, last_date FROM attendance WHERE user_id = ?",
                (interaction.user.id,)) as cursor:
            row = await cursor.fetchone()
        if row is None:
            await interaction.response.send_message("봇에 저장된 내 기록이 없어요.", ephemeral=True)
            return
        embed = discord.Embed(title="봇에 저장된 내 정보", color=0x5B6CF0)
        embed.add_field(name="이름", value=row[0])
        embed.add_field(name="포인트", value=f"{row[1]}점")
        embed.add_field(name="마지막 출석일", value=row[2])
        embed.set_footer(text="지우고 싶으면 /내정보삭제")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="소개", description="이 봇과 개인정보 안내를 보여 줘요")
    async def about(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="마이봇을 소개해요",
            description="우리 서버의 급식, 날씨, 숙제, 출석을 알려 주는 봇이에요.",
            color=0x22C3A6)
        embed.add_field(name="대표 명령어", value="/급식 · /날씨 · /출석 (전체 목록은 /도움말)", inline=False)
        embed.add_field(name="저장하는 정보",
                        value="/출석 을 쓰면 디스코드 사용자 ID, 표시 이름, 포인트, 마지막 출석일을 저장해요. "
                              "오류를 찾기 위해 누가 언제 어떤 명령어를 썼는지 서버 로그에 남아요.",
                        inline=False)
        embed.add_field(name="보관 기간과 지우기",
                        value="/내정보 로 저장된 내용을 볼 수 있고 /내정보삭제 로 바로 지울 수 있어요. "
                              "매일 만드는 백업에는 최대 7일 동안 남았다가 오래된 백업과 함께 사라져요.",
                        inline=False)
        embed.add_field(name="만든 사람 · 문의", value="마이봇 관리자 (디스코드에서 관리자에게 DM)", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ops(bot))
