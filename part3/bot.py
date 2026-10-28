# 3부 완성 코드(1~8장): 본문의 따라 만들기와 요구사항 미션 해답을 책 순서대로 모은 한 파일 버전입니다.
# 9장의 Cog 버전은 part3_cog 폴더에 있습니다.
import asyncio
import datetime
import json
import os
import random
import re
from pathlib import Path

import aiohttp
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
MEAL_CHANNEL_ID = int(os.getenv("MEAL_CHANNEL_ID"))
DB_FILE = Path(__file__).parent / "bot.db"
HOMEWORK_FILE = Path(__file__).parent / "homework.json"

intents = discord.Intents.default()


class MyBot(commands.Bot):
    async def setup_hook(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        self.db = await aiosqlite.connect(DB_FILE)
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS attendance ("
            " user_id INTEGER PRIMARY KEY,"
            " name TEXT,"
            " points INTEGER NOT NULL DEFAULT 0,"
            " last_date TEXT)"
        )
        await self.db.commit()
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        morning_meal.start()
        meeting_reminder.start()

    async def close(self):
        await self.session.close()
        await self.db.close()
        await super().close()


bot = MyBot(command_prefix="!", intents=intents)


async def fetch_json(url: str, params: dict | None = None):
    """외부 API에 GET 요청을 보내고 JSON을 돌려준다. 실패하면 None."""
    try:
        async with bot.session.get(url, params=params) as resp:
            if resp.status != 200:
                print(f"API 오류 {resp.status}: {url}")
                return None
            return await resp.json()
    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        print(f"API 연결 실패: {error!r}")
        return None


# ---------- 2장 ----------
CITIES = {
    "서울": (37.57, 126.98), "인천": (37.46, 126.71), "부산": (35.18, 129.08),
    "대구": (35.87, 128.60), "대전": (36.35, 127.38), "광주": (35.16, 126.85),
    "제주": (33.50, 126.53),
}

WEATHER_TEXT = {
    0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림",
    45: "안개", 48: "안개", 51: "이슬비", 53: "이슬비", 55: "이슬비",
    56: "어는 이슬비", 57: "어는 이슬비", 61: "비", 63: "비", 65: "강한 비",
    66: "어는 비", 67: "어는 비", 71: "눈", 73: "눈", 75: "강한 눈", 77: "싸락눈",
    80: "소나기", 81: "소나기", 82: "강한 소나기", 85: "눈발", 86: "강한 눈발",
    95: "뇌우", 96: "우박을 동반한 뇌우", 99: "우박을 동반한 뇌우",
}


@bot.tree.command(name="날씨", description="도시의 지금 날씨를 알려 줘요")
@app_commands.describe(city="도시 이름 (예: 인천)")
@app_commands.rename(city="도시")
async def weather(interaction: discord.Interaction, city: str):
    if city not in CITIES:
        await interaction.response.send_message(
            f"아직 모르는 도시예요. 가능한 도시: {', '.join(CITIES)}", ephemeral=True)
        return

    await interaction.response.defer()
    lat, lon = CITIES[city]
    data = await fetch_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Seoul", "forecast_days": 1,
    })
    if data is None:
        await interaction.followup.send("지금은 날씨 정보를 가져올 수 없어요. 잠시 뒤에 다시 해 주세요.")
        return

    now, today = data["current"], data["daily"]
    sky = WEATHER_TEXT.get(now["weather_code"], "알 수 없음")
    embed = discord.Embed(title=f"{city}의 지금 날씨",
                          description=f"**{sky}**, {now['temperature_2m']}°C", color=0x2E8BD8)
    embed.add_field(name="최고 / 최저",
                    value=f"{today['temperature_2m_max'][0]}°C / {today['temperature_2m_min'][0]}°C")
    embed.add_field(name="비 올 확률", value=f"{today['precipitation_probability_max'][0]}%")
    embed.add_field(name="바람", value=f"{now['wind_speed_10m']} km/h")
    embed.set_footer(text="날씨 정보: Open-Meteo.com (CC BY 4.0)")
    await interaction.followup.send(embed=embed)


@weather.autocomplete("city")
async def city_autocomplete(interaction: discord.Interaction, current: str):
    return [app_commands.Choice(name=c, value=c) for c in CITIES if current in c][:25]


def outfit(t_max: float) -> str:
    if t_max >= 28:
        return "반팔·반바지"
    if t_max >= 20:
        return "얇은 긴팔"
    if t_max >= 12:
        return "가디건이나 재킷"
    if t_max >= 5:
        return "코트"
    return "패딩"


@bot.tree.command(name="옷차림", description="오늘 날씨에 맞는 옷을 추천해요")
@app_commands.describe(city="도시 이름 (예: 인천)")
@app_commands.rename(city="도시")
async def clothes(interaction: discord.Interaction, city: str):
    if city not in CITIES:
        await interaction.response.send_message("아직 모르는 도시예요.", ephemeral=True)
        return
    await interaction.response.defer()
    lat, lon = CITIES[city]
    data = await fetch_json("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon,
        "daily": "temperature_2m_max,precipitation_probability_max",
        "timezone": "Asia/Seoul", "forecast_days": 1,
    })
    if data is None:
        await interaction.followup.send("지금은 날씨 정보를 가져올 수 없어요.")
        return
    t_max = data["daily"]["temperature_2m_max"][0]
    rain = data["daily"]["precipitation_probability_max"][0]
    embed = discord.Embed(title=f"{city} 오늘의 옷차림",
                          description=f"최고 {t_max}°C → **{outfit(t_max)}**", color=0x2E8BD8)
    if rain is not None and rain >= 50:
        embed.add_field(name="우산", value=f"비 올 확률 {rain}% — 우산을 챙기세요")
    embed.set_footer(text="날씨 정보: Open-Meteo.com (CC BY 4.0)")
    await interaction.followup.send(embed=embed)


# ---------- 3장 ----------
KST = datetime.timezone(datetime.timedelta(hours=9))
SCHOOL = {"ATPT_OFCDC_SC_CODE": "E10", "SD_SCHUL_CODE": "1234567"}  # 예시 값. 꼭 우리 학교 코드로 바꾸기


def clean_menu(text: str) -> str:
    """<br/>로 나뉜 메뉴를 한 줄에 하나씩, 알레르기 번호는 빼고 돌려준다."""
    lines = text.split("<br/>")
    return "\n".join(re.sub(r"\s*\([\d.]+\)", "", line).strip() for line in lines)


async def get_meal(day: datetime.date):
    """그날의 급식 목록. 연결 실패면 None, 급식이 없으면 빈 목록."""
    data = await fetch_json("https://open.neis.go.kr/hub/mealServiceDietInfo", {
        "Type": "json", **SCHOOL, "MLSV_YMD": day.strftime("%Y%m%d"),
    })
    if data is None:
        return None
    if "mealServiceDietInfo" not in data:
        return []
    return data["mealServiceDietInfo"][1]["row"]


def make_meal_embed(day: datetime.date, rows: list) -> discord.Embed:
    embed = discord.Embed(title=f"{day.month}월 {day.day}일 급식", color=0xE0A100)
    for row in rows:
        embed.add_field(name=row["MMEAL_SC_NM"], value=clean_menu(row["DDISH_NM"]), inline=False)
    embed.set_footer(text="급식 정보: 나이스 교육정보 개방 포털")
    return embed


@bot.tree.command(name="급식", description="오늘 급식을 알려 줘요")
async def meal(interaction: discord.Interaction):
    await interaction.response.defer()
    today = datetime.datetime.now(KST).date()
    rows = await get_meal(today)
    if rows is None:
        await interaction.followup.send("지금은 급식 정보를 가져올 수 없어요.")
        return
    if not rows:
        await interaction.followup.send("오늘은 급식이 없어요. (주말·방학이거나 아직 올라오지 않았어요)")
        return
    await interaction.followup.send(embed=make_meal_embed(today, rows))


@bot.tree.command(name="내일급식", description="내일 급식을 미리 알려 줘요")
async def meal_tomorrow(interaction: discord.Interaction):
    day = datetime.datetime.now(KST).date() + datetime.timedelta(days=1)
    if day.weekday() >= 5:
        await interaction.response.send_message("내일은 주말이에요!")
        return
    await interaction.response.defer()
    rows = await get_meal(day)
    if rows is None:
        await interaction.followup.send("지금은 급식 정보를 가져올 수 없어요.")
        return
    if not rows:
        await interaction.followup.send("내일은 급식 정보가 없어요.")
        return
    weekday = "월화수목금토일"[day.weekday()]
    embed = discord.Embed(title=f"{day.month}월 {day.day}일 ({weekday}) 급식", color=0xE0A100)
    for row in rows:
        embed.add_field(name=f"{row['MMEAL_SC_NM']} · {row['CAL_INFO']}",
                        value=clean_menu(row["DDISH_NM"]), inline=False)
    embed.set_footer(text="급식 정보: 나이스 교육정보 개방 포털")
    await interaction.followup.send(embed=embed)


ALLERGY = {"1": "난류", "2": "우유", "3": "메밀", "4": "땅콩", "5": "대두", "6": "밀", "7": "고등어",
           "8": "게", "9": "새우", "10": "돼지고기", "11": "복숭아", "12": "토마토", "13": "아황산류",
           "14": "호두", "15": "닭고기", "16": "쇠고기", "17": "오징어", "18": "조개류", "19": "잣"}


def allergy_names(text: str) -> str:
    numbers = set()
    for group in re.findall(r"\(([\d.]+)\)", text):
        numbers.update(n for n in group.split(".") if n)
    return ", ".join(ALLERGY[n] for n in sorted(numbers, key=int) if n in ALLERGY)


# ---------- 4장 ----------
MET = "https://collectionapi.metmuseum.org/public/collection"


def make_art_embed(art: dict) -> discord.Embed:
    """작품 정보(딕셔너리)로 임베드를 만든다. 비어 있는 값은 '알 수 없음'으로."""
    embed = discord.Embed(title=(art["title"] or "제목 없음")[:256], url=art["objectURL"], color=0xD9487A)
    embed.add_field(name="작가", value=art["artistDisplayName"] or "알 수 없음")
    embed.add_field(name="연도", value=art["objectDate"] or "알 수 없음")
    embed.add_field(name="재료", value=(art["medium"] or "알 수 없음")[:1024], inline=False)
    if art["primaryImageSmall"]:
        embed.set_image(url=art["primaryImageSmall"])
    embed.set_footer(text=f"No.{art['objectID']} · 출처: The Metropolitan Museum of Art (CC0)")
    return embed


@bot.tree.command(name="작품", description="작품 번호로 미술관 작품을 보여 줘요")
@app_commands.describe(number="작품 번호 (예: 436535)")
@app_commands.rename(number="번호")
async def artwork(interaction: discord.Interaction, number: app_commands.Range[int, 1, 99_999_999]):
    await interaction.response.defer()
    art = await fetch_json(f"{MET}/v1/objects/{number}")
    if art is None:
        await interaction.followup.send("그 번호의 작품이 없거나, 지금은 정보를 가져올 수 없어요.")
        return
    await interaction.followup.send(embed=make_art_embed(art))


@bot.tree.command(name="작품검색", description="영어 낱말로 미술관 작품을 찾아 하나를 보여 줘요")
@app_commands.describe(word="영어 낱말 (예: cat, sunflowers)")
@app_commands.rename(word="낱말")
async def art_search(interaction: discord.Interaction, word: str):
    await interaction.response.defer()
    found = await fetch_json(f"{MET}/v1.1/search", {"q": word, "hasImages": "true", "limit": 20})
    if found is None:
        await interaction.followup.send("지금은 검색할 수 없어요.")
        return
    ids = found["objectIDs"] or []              # 찾은 게 없으면 None 이 온다
    picks = random.sample(ids, min(5, len(ids)))
    arts = await asyncio.gather(*(fetch_json(f"{MET}/v1/objects/{i}") for i in picks))
    art = next((a for a in arts if a and a["primaryImageSmall"]), None)
    if art is None:
        await interaction.followup.send(f"'{word}'(으)로 사진이 있는 작품을 찾지 못했어요.")
        return
    await interaction.followup.send(f"'{word}' 검색 결과 {found['total']}개 중 하나예요.",
                                    embed=make_art_embed(art))


# ---- 미션 3 해답 ----
art_cache = {}


async def get_art(number: int):
    """작품 정보를 캐시에서 먼저 찾고, 없으면 API로 받아 저장한다."""
    if number in art_cache:
        return art_cache[number]
    art = await fetch_json(f"{MET}/v1/objects/{number}")
    if art is not None:
        art_cache[number] = art
    return art


def year_text(year: int) -> str:
    return f"기원전 {-year}년" if year < 0 else f"{year}년"


@bot.tree.command(name="작품비교", description="두 작품 중 어느 것이 더 오래됐는지 비교해요")
@app_commands.rename(first="번호1", second="번호2")
async def art_compare(interaction: discord.Interaction,
                      first: app_commands.Range[int, 1, 99_999_999],
                      second: app_commands.Range[int, 1, 99_999_999]):
    if first == second:
        await interaction.response.send_message("서로 다른 번호 두 개를 넣어 주세요.", ephemeral=True)
        return
    await interaction.response.defer()
    a, b = await asyncio.gather(get_art(first), get_art(second))
    missing = [str(n) for n, art in ((first, a), (second, b)) if art is None]
    if missing:
        await interaction.followup.send(f"{', '.join(missing)}번 작품을 가져올 수 없어요.")
        return
    embed = discord.Embed(title="어느 작품이 더 오래됐을까?", color=0xD9487A)
    for art in (a, b):
        embed.add_field(name=(art["title"] or "제목 없음")[:256],
                        value=f"{art['artistDisplayName'] or '작가 미상'}\n{year_text(art['objectBeginDate'])}")
    gap = abs(a["objectBeginDate"] - b["objectBeginDate"])
    if gap == 0:
        embed.description = "두 작품은 **같은 해**에 시작됐어요."
    else:
        older = a if a["objectBeginDate"] < b["objectBeginDate"] else b
        embed.description = f"**{older['title']}** 이(가) {gap}년 더 오래됐어요."
    embed.set_footer(text="출처: The Metropolitan Museum of Art (CC0)")
    await interaction.followup.send(embed=embed)


# ---------- 5장 ----------
class MealDayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.select(placeholder="날짜를 고르세요", options=[
        discord.SelectOption(label="오늘", value="0"),
        discord.SelectOption(label="내일", value="1"),
        discord.SelectOption(label="모레", value="2"),
    ])
    async def pick_day(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer(ephemeral=True, thinking=True)
        day = datetime.datetime.now(KST).date() + datetime.timedelta(days=int(select.values[0]))
        rows = await get_meal(day)
        if not rows:
            await interaction.followup.send("그날은 급식 정보가 없어요.", ephemeral=True)
            return
        await interaction.followup.send(embed=make_meal_embed(day, rows), ephemeral=True)


@bot.tree.command(name="급식보기", description="날짜를 골라 급식을 봐요")
async def meal_menu(interaction: discord.Interaction):
    await interaction.response.send_message("언제 급식을 볼까요?", view=MealDayView())


class SchoolSelect(discord.ui.Select):
    def __init__(self, schools: list):
        self.schools = {s["SD_SCHUL_CODE"]: s for s in schools}
        options = [discord.SelectOption(label=s["SCHUL_NM"], value=s["SD_SCHUL_CODE"],
                                        description=(s["ORG_RDNMA"] or "")[:100]) for s in schools]
        super().__init__(placeholder="학교를 고르세요", options=options)

    async def callback(self, interaction: discord.Interaction):
        s = self.schools[self.values[0]]
        embed = discord.Embed(title=s["SCHUL_NM"], color=0x2E8BD8)
        embed.add_field(name="주소", value=s["ORG_RDNMA"] or "없음", inline=False)
        embed.add_field(name="전화", value=s["ORG_TELNO"] or "없음")
        embed.add_field(name="시도교육청 코드", value=s["ATPT_OFCDC_SC_CODE"])
        embed.add_field(name="학교 코드", value=s["SD_SCHUL_CODE"])
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SchoolView(discord.ui.View):
    def __init__(self, schools: list):
        super().__init__(timeout=120)
        self.add_item(SchoolSelect(schools))


@bot.tree.command(name="학교찾기", description="학교 이름으로 학교 코드를 찾아요")
@app_commands.describe(name="학교 이름 (예: 우리 학교 이름)")
@app_commands.rename(name="이름")
async def find_school(interaction: discord.Interaction, name: str):
    await interaction.response.defer(ephemeral=True)
    data = await fetch_json("https://open.neis.go.kr/hub/schoolInfo", {"Type": "json", "SCHUL_NM": name})
    if data is None:
        await interaction.followup.send("지금은 학교 정보를 가져올 수 없어요.", ephemeral=True)
        return
    if "schoolInfo" not in data:
        await interaction.followup.send("찾는 학교가 없어요.", ephemeral=True)
        return
    schools = data["schoolInfo"][1]["row"]
    await interaction.followup.send(f"{len(schools)}개를 찾았어요.", view=SchoolView(schools), ephemeral=True)


# ---------- 6장 ----------
def load_homework() -> list:
    if HOMEWORK_FILE.exists():
        return json.loads(HOMEWORK_FILE.read_text(encoding="utf-8"))
    return []


def save_homework():
    HOMEWORK_FILE.write_text(json.dumps(homework, ensure_ascii=False, indent=2), encoding="utf-8")


homework = load_homework()


@bot.tree.command(name="숙제등록", description="숙제를 등록해요")
@app_commands.describe(subject="과목", content="숙제 내용", due="마감일 (예: 10월 30일)")
@app_commands.rename(subject="과목", content="내용", due="마감")
async def homework_add(interaction: discord.Interaction, subject: str, content: str, due: str):
    homework.append({"subject": subject, "content": content, "due": due,
                     "by": interaction.user.display_name, "done": False})
    save_homework()
    await interaction.response.send_message(f"[{subject}] 숙제를 등록했어요.")


@bot.tree.command(name="숙제목록", description="남은 숙제를 보여 줘요")
async def homework_list(interaction: discord.Interaction):
    embed = discord.Embed(title="남은 숙제", color=0x13A889)
    for number, item in enumerate(homework, start=1):
        if not item["done"]:
            embed.add_field(name=f"{number}. [{item['subject']}] 마감 {item['due']}",
                            value=f"{item['content']} (등록: {item['by']})", inline=False)
    if not embed.fields:
        await interaction.response.send_message("남은 숙제가 없어요!")
        return
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="숙제완료", description="끝난 숙제를 완료로 표시해요")
@app_commands.describe(number="/숙제목록 의 번호")
@app_commands.rename(number="번호")
async def homework_done(interaction: discord.Interaction, number: int):
    if not 1 <= number <= len(homework) or homework[number - 1]["done"]:
        await interaction.response.send_message("없는 번호이거나 이미 완료한 숙제예요.", ephemeral=True)
        return
    item = homework[number - 1]
    item["done"] = True
    save_homework()
    left = sum(1 for h in homework if not h["done"])
    await interaction.response.send_message(f"[{item['subject']}] 숙제를 완료했어요! 남은 숙제 {left}개")


# ---------- 7장 ----------
@bot.tree.command(name="출석", description="오늘 출석하고 포인트를 받아요")
async def attend(interaction: discord.Interaction):
    today = datetime.datetime.now(KST).date().isoformat()
    user = interaction.user
    async with bot.db.execute(
            "SELECT points, last_date FROM attendance WHERE user_id = ?", (user.id,)) as cursor:
        row = await cursor.fetchone()

    if row is None:
        points = 1
        await bot.db.execute(
            "INSERT INTO attendance (user_id, name, points, last_date) VALUES (?, ?, ?, ?)",
            (user.id, user.display_name, points, today))
    elif row[1] == today:
        await interaction.response.send_message("오늘은 이미 출석했어요!", ephemeral=True)
        return
    else:
        points = row[0] + 1
        await bot.db.execute(
            "UPDATE attendance SET points = ?, name = ?, last_date = ? WHERE user_id = ?",
            (points, user.display_name, today, user.id))

    await bot.db.commit()
    await interaction.response.send_message(f"{user.mention} 출석 완료! 지금까지 {points}포인트")


@bot.tree.command(name="랭킹", description="출석 포인트 순위를 보여 줘요")
async def ranking(interaction: discord.Interaction):
    async with bot.db.execute(
            "SELECT name, points FROM attendance ORDER BY points DESC LIMIT 5") as cursor:
        rows = await cursor.fetchall()
    if not rows:
        await interaction.response.send_message("아직 출석한 사람이 없어요.")
        return
    lines = [f"{rank}위 {name} — {points}포인트" for rank, (name, points) in enumerate(rows, start=1)]
    embed = discord.Embed(title="출석 랭킹", description="\n".join(lines), color=0x3FA34D)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="내포인트", description="내 포인트와 순위를 알려 줘요")
async def my_points(interaction: discord.Interaction):
    async with bot.db.execute("SELECT points FROM attendance WHERE user_id = ?",
                              (interaction.user.id,)) as cursor:
        row = await cursor.fetchone()
    if row is None:
        await interaction.response.send_message("아직 출석 기록이 없어요.", ephemeral=True)
        return
    async with bot.db.execute("SELECT COUNT(*) FROM attendance WHERE points > ?", (row[0],)) as cursor:
        higher = (await cursor.fetchone())[0]
    await interaction.response.send_message(f"{row[0]}포인트, {higher + 1}위예요.", ephemeral=True)


# ---------- 8장 ----------
@tasks.loop(time=datetime.time(hour=7, minute=30, tzinfo=KST))
async def morning_meal():
    today = datetime.datetime.now(KST).date()
    if today.weekday() >= 5:
        return
    rows = await get_meal(today)
    if not rows:
        return
    channel = bot.get_channel(MEAL_CHANNEL_ID)
    if channel is not None:
        await channel.send("좋은 아침이에요! 오늘 급식이에요.", embed=make_meal_embed(today, rows))


@morning_meal.before_loop
async def before_morning_meal():
    await bot.wait_until_ready()


MEETING_WEEKDAY = 5


@tasks.loop(time=datetime.time(hour=20, minute=0, tzinfo=KST))
async def meeting_reminder():
    tomorrow = datetime.datetime.now(KST).date() + datetime.timedelta(days=1)
    if tomorrow.weekday() != MEETING_WEEKDAY:
        return
    channel = bot.get_channel(MEAL_CHANNEL_ID)
    if channel is None:
        return
    left = sum(1 for h in homework if not h["done"])
    embed = discord.Embed(title="내일은 모임 날!", color=0x5B6CF0)
    embed.add_field(name="준비물", value="노트북, 충전기", inline=False)
    embed.add_field(name="남은 숙제", value=f"{left}개")
    await channel.send(embed=embed)


@meeting_reminder.before_loop
async def before_meeting_reminder():
    await bot.wait_until_ready()
