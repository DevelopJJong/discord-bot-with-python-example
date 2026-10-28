# 기초 다지기 3장 예제
user = {"name": "하늘", "points": 12}
print(user["name"])
user["points"] = user["points"] + 1      # 값 바꾸기
user["level"] = 2                         # 새 키 추가
print(user)
print(user.get("email", "없음"))          # 없는 키는 기본값
for key, value in user.items():
    print(key, "→", value)
