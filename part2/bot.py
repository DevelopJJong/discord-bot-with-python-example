# 2부 완성 코드: 본문의 따라 만들기와 요구사항 미션 해답을 책 순서대로 모은 파일입니다.
import asyncio
import os
import random

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):
    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"봇 이름: {bot.user.name}")
    print(f"봇 ID: {bot.user.id}")
    print(f"길드 {len(bot.guilds)}개에 들어가 있어요")
    for guild in bot.guilds:
        print(f"- {guild.name}")
    await bot.change_presence(activity=discord.Game(name="코딩 공부하는 중"))


# 3장
@bot.tree.command(name="안녕", description="봇이 인사해요")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"안녕, {interaction.user.mention}!")


@bot.tree.command(name="소개", description="봇이 자기소개를 해요")
async def intro(interaction: discord.Interaction):
    text = (
        f"저는 {interaction.client.user.name}이에요.\n"
        f"지금 {interaction.guild.name}에서 일하고 있어요.\n"
        f"이 메시지는 {interaction.user.display_name}님에게만 보여요."
    )
    await interaction.response.send_message(text, ephemeral=True)


@bot.tree.command(name="지금", description="현재 시각을 알려 줘요")
async def now(interaction: discord.Interaction):
    stamp = discord.utils.format_dt(discord.utils.utcnow(), "F")
    await interaction.response.send_message(f"지금은 {stamp}이에요")


# 4장
@bot.tree.command(name="주사위", description="주사위를 굴려요")
@app_commands.describe(sides="주사위 면의 수 (2~100, 비우면 6)")
@app_commands.rename(sides="면")
async def dice(interaction: discord.Interaction,
               sides: app_commands.Range[int, 2, 100] = 6):
    number = random.randint(1, sides)
    await interaction.response.send_message(f"{sides}면 주사위를 굴렸어요: **{number}**")


@bot.tree.command(name="계산", description="두 수를 계산해요")
@app_commands.describe(a="첫 번째 수", b="두 번째 수", op="계산 방법")
@app_commands.rename(a="숫자1", b="숫자2", op="계산")
@app_commands.choices(op=[
    app_commands.Choice(name="더하기", value="+"),
    app_commands.Choice(name="빼기", value="-"),
    app_commands.Choice(name="곱하기", value="*"),
    app_commands.Choice(name="나누기", value="/"),
])
async def calc(interaction: discord.Interaction, a: float, b: float,
               op: app_commands.Choice[str]):
    if op.value == "/" and b == 0:
        await interaction.response.send_message("0으로는 나눌 수 없어요!", ephemeral=True)
        return

    if op.value == "+":
        result = a + b
    elif op.value == "-":
        result = a - b
    elif op.value == "*":
        result = a * b
    else:
        result = a / b
    await interaction.response.send_message(f"{a:g} {op.value} {b:g} = {result:g}")


@bot.tree.command(name="가위바위보", description="봇과 가위바위보를 해요")
@app_commands.describe(choice="낼 것을 고르세요")
@app_commands.rename(choice="선택")
@app_commands.choices(choice=[
    app_commands.Choice(name="가위", value="가위"),
    app_commands.Choice(name="바위", value="바위"),
    app_commands.Choice(name="보", value="보"),
])
async def rps(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    me = choice.value
    bot_pick = random.choice(["가위", "바위", "보"])
    wins = {"가위": "보", "바위": "가위", "보": "바위"}
    if me == bot_pick:
        result = "비겼어요"
    elif wins[me] == bot_pick:
        result = "이겼어요!"
    else:
        result = "졌어요"
    await interaction.response.send_message(f"나: {me} / 봇: {bot_pick} → **{result}**")


@bot.tree.command(name="뽑기", description="후보 중 하나를 뽑아요")
@app_commands.describe(options="쉼표로 구분한 후보 (예: 짜장면,짬뽕)")
@app_commands.rename(options="후보")
async def pick(interaction: discord.Interaction, options: str):
    items = [x.strip() for x in options.split(",") if x.strip()]
    if len(items) < 2:
        await interaction.response.send_message("후보를 2개 이상 쉼표로 적어 주세요.", ephemeral=True)
        return
    await interaction.response.send_message(f"뽑힌 것은... **{random.choice(items)}**!")


# 5장
@bot.tree.command(name="프로필", description="멤버 정보를 보여 줘요")
@app_commands.describe(member="정보를 볼 멤버 (비우면 나)")
@app_commands.rename(member="멤버")
async def profile(interaction: discord.Interaction, member: discord.Member | None = None):
    member = member or interaction.user

    embed = discord.Embed(
        title=member.display_name,
        description=f"{member.mention}님의 프로필이에요",
        color=discord.Color.blurple(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="계정 만든 날", value=discord.utils.format_dt(member.created_at, "D"))
    embed.add_field(name="서버에 온 날", value=discord.utils.format_dt(member.joined_at, "R"))
    embed.add_field(name="역할 수", value=f"{len(member.roles) - 1}개", inline=False)
    embed.set_footer(text="마이봇 · /프로필")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="동아리소개", description="우리 동아리를 소개해요")
async def club(interaction: discord.Interaction):
    embed = discord.Embed(title="코딩 동아리", description="봇과 게임을 만드는 모임", color=0x5B6CF0)
    embed.add_field(name="모이는 시간", value="토요일 오후 2시")
    embed.add_field(name="하는 활동", value="디스코드봇 만들기")
    embed.add_field(name="다음 모임 준비물", value="노트북, 충전기", inline=False)
    embed.set_footer(text=f"요청: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="서버정보", description="이 서버의 정보를 보여 줘요")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=guild.name, color=discord.Color.green())
    embed.add_field(name="멤버 수", value=f"{guild.member_count}명")
    embed.add_field(name="만들어진 날", value=discord.utils.format_dt(guild.created_at, "D"))
    if guild.icon is not None:
        embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)


# 6장
@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.system_channel
    if channel is not None:
        await channel.send(f"{member.mention}님, {member.guild.name}에 오신 걸 환영해요!")


BANNED_WORDS = ["바보", "멍청이"]
warnings = {}


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if any(word in message.content for word in BANNED_WORDS):
        await message.delete()
        warnings[message.author.id] = warnings.get(message.author.id, 0) + 1
        count = warnings[message.author.id]
        text = f"{message.author.mention} 고운 말을 써 주세요! (경고 {count}회)"
        if count >= 3:
            text += " 관리자에게 알려요."
        await message.channel.send(text, delete_after=5)
        return
    if "숙제" in message.content:
        await message.add_reaction("📚")
        await message.reply("숙제 화이팅! 마감은 지키자")


# 7장
class VoteView(discord.ui.View):
    def __init__(self, question: str, owner_id: int):
        super().__init__(timeout=300)
        self.question = question
        self.yes = 0
        self.no = 0
        self.voters = set()
        self.owner_id = owner_id

    def text(self):
        return f"**{self.question}**\n찬성 {self.yes}표 · 반대 {self.no}표"

    async def count(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id in self.voters:
            await interaction.response.send_message("이미 투표했어요!", ephemeral=True)
            return
        self.voters.add(interaction.user.id)
        if choice == "찬성":
            self.yes += 1
        else:
            self.no += 1
        await interaction.response.edit_message(content=self.text(), view=self)

    @discord.ui.button(label="찬성", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.count(interaction, "찬성")

    @discord.ui.button(label="반대", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.count(interaction, "반대")

    @discord.ui.button(label="마감", style=discord.ButtonStyle.secondary)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("투표를 연 사람만 마감할 수 있어요.", ephemeral=True)
            return
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content=self.text() + "\n(투표 마감)", view=self)
        self.stop()


@bot.tree.command(name="투표", description="찬반 투표를 열어요")
@app_commands.describe(question="투표할 질문")
@app_commands.rename(question="질문")
async def vote(interaction: discord.Interaction, question: str):
    view = VoteView(question, interaction.user.id)
    await interaction.response.send_message(view.text(), view=view)


class QuizView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    async def answer(self, interaction: discord.Interaction, correct: bool):
        if correct:
            await interaction.response.send_message("정답이에요! 빠짐없이, 순서대로 = TCP", ephemeral=True)
        else:
            await interaction.response.send_message("아쉬워요, 다시 생각해 봐요", ephemeral=True)

    @discord.ui.button(label="UDP", style=discord.ButtonStyle.primary)
    async def b1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.answer(interaction, False)

    @discord.ui.button(label="TCP", style=discord.ButtonStyle.primary)
    async def b2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.answer(interaction, True)

    @discord.ui.button(label="DNS", style=discord.ButtonStyle.primary)
    async def b3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.answer(interaction, False)

    @discord.ui.button(label="JSON", style=discord.ButtonStyle.primary)
    async def b4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.answer(interaction, False)


@bot.tree.command(name="퀴즈", description="CS 퀴즈를 내요")
async def quiz(interaction: discord.Interaction):
    await interaction.response.send_message("패킷을 빠짐없이, 순서대로 전달하는 프로토콜은?", view=QuizView())


# 8장
@bot.tree.command(name="청소", description="최근 메시지를 지워요")
@app_commands.describe(amount="지울 메시지 수 (1~50)")
@app_commands.rename(amount="개수")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 50]):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"메시지 {len(deleted)}개를 지웠어요.", ephemeral=True)


@clear.error
async def clear_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("메시지 관리 권한이 있는 사람만 쓸 수 있어요.", ephemeral=True)


@bot.tree.command(name="타이머", description="정해진 시간 뒤에 알려 줘요")
@app_commands.describe(seconds="몇 초 뒤에 알려 줄까요? (1~600)")
@app_commands.rename(seconds="초")
async def timer(interaction: discord.Interaction, seconds: app_commands.Range[int, 1, 600]):
    await interaction.response.send_message(f"{seconds}초 타이머를 시작했어요!")
    await asyncio.sleep(seconds)
    await interaction.followup.send(f"{interaction.user.mention} 시간이 끝났어요!")


@bot.tree.command(name="알림", description="몇 분 뒤에 메모를 알려 줘요")
@app_commands.describe(minutes="몇 분 뒤 (1~10)", memo="알려 줄 내용")
@app_commands.rename(minutes="분", memo="메모")
async def remind(interaction: discord.Interaction,
                 minutes: app_commands.Range[int, 1, 10], memo: str):
    await interaction.response.send_message(f"{minutes}분 뒤에 알려 줄게요!", ephemeral=True)
    await asyncio.sleep(minutes * 60)
    embed = discord.Embed(title="알림", description=memo, color=discord.Color.orange())
    await interaction.followup.send(content=interaction.user.mention, embed=embed)
