import asyncio
import os
from pathlib import Path

import aiohttp
import aiosqlite
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
DB_FILE = Path(__file__).parent / "bot.db"
EXTENSIONS = ["cogs.fun", "cogs.info"]      # 불러올 Cog 파일 목록 (날씨·급식 Cog는 미션 8에서 직접 나눠 보세요)


class MyBot(commands.Bot):
    async def setup_hook(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        self.db = await aiosqlite.connect(DB_FILE)
        for name in EXTENSIONS:
            await self.load_extension(name)
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def close(self):
        await self.session.close()
        await self.db.close()
        await super().close()

    async def fetch_json(self, url: str, params: dict | None = None):
        try:
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    print(f"API 오류 {resp.status}: {url}")
                    return None
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            print(f"API 연결 실패: {error!r}")
            return None


bot = MyBot(command_prefix="!", intents=discord.Intents.default())
bot.run(TOKEN)
