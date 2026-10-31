# 기초 다지기 6장 예제
import random
import datetime
from pathlib import Path

random.seed(1)                         # 예제의 결과를 늘 같게 만들기
print(random.randint(1, 6))            # 1~6 사이 정수
print(random.choice(["가위", "바위", "보"]))
day = datetime.date(2026, 10, 24)
print(day.strftime("%Y년 %m월 %d일"), day.weekday())   # 월요일=0
print(day + datetime.timedelta(days=1))
print(Path("bot.py").suffix)
