# 기초 다지기 1장 예제
bot_name = "마이봇"      # 문자열 (str)
points = 12              # 정수 (int)
temperature = 17.5       # 실수 (float)
is_online = True         # 참/거짓 (bool)
channel = None           # 아직 값이 없음 (NoneType)

points = points + 3      # 오른쪽을 먼저 계산해 다시 넣는다
print(bot_name, points, temperature, is_online, channel)
print(type(points), type(temperature))
