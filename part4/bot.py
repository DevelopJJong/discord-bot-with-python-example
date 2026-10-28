# 4부 완성 코드: 로그, 전역 오류 처리기, 전역/길드 명령어 등록까지 들어간 운영용 bot.py 입니다.
import asyncio
import logging
import os
from pathlib import Path

import aiohttp
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
DB_FILE = Path(__file__).parent / "bot.db"
EXTENSIONS = ["cogs.fun", "cogs.info", "cogs.ops"]

log = logging.getLogger("mybot")      # 우리 봇의 기록 담당


class MyBot(commands.Bot):
    async def setup_hook(self):
        self.started_at = discord.utils.utcnow()      # 켜진 시각 (/상태에서 사용)
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        self.db = await aiosqlite.connect(DB_FILE)
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS attendance ("
            " user_id INTEGER PRIMARY KEY, name TEXT,"
            " points INTEGER NOT NULL DEFAULT 0, last_date TEXT)")
        await self.db.commit()
        for name in EXTENSIONS:
            await self.load_extension(name)
        guild = discord.Object(id=GUILD_ID)
        if os.getenv("SYNC_GLOBAL") == "1":        # 운영 서버의 .env 에만 있는 값 (4부 9장)
            self.tree.clear_commands(guild=guild)   # 예전에 올린 길드 명령어 지우기
            await self.tree.sync(guild=guild)
            await self.tree.sync()                  # 모든 서버에 전역 명령어로 등록
        else:                                       # 내 컴퓨터(개발용)는 테스트 길드에만
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        log.info("확장 %d개를 불러왔어요", len(EXTENSIONS))

    async def on_ready(self):
        log.info("%s(으)로 로그인했어요. 들어가 있는 서버: %d곳", self.user, len(self.guilds))

    async def close(self):
        log.info("봇을 끕니다")
        await self.session.close()
        await self.db.close()
        await super().close()

    async def fetch_json(self, url: str, params: dict | None = None):
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    log.warning("API 오류 %s: %s", resp.status, url)
                    return None
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            log.warning("API 연결 실패: %r", error)
            return None


bot = MyBot(command_prefix="!", intents=discord.Intents.default())


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if interaction.command and interaction.command.on_error:
        return      # 명령어에 따로 붙인 @....error 가 이미 처리했다

    if isinstance(error, app_commands.MissingPermissions):
        message = "이 명령어를 쓸 권한이 없어요."
    elif isinstance(error, app_commands.CommandOnCooldown):
        message = f"조금 뒤에 다시 써 주세요. ({error.retry_after:.0f}초 남음)"
    else:
        name = interaction.command.name if interaction.command else "?"
        log.error("/%s 실행 중 오류", name, exc_info=error)
        message = "앗, 문제가 생겼어요. 관리자에게 알려 주세요."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN, root_logger=True)
