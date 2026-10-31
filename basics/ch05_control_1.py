# 기초 다지기 4장 예제
temp = 24
if temp >= 28:
    print("반팔")
elif temp >= 20:                 # 위 조건이 거짓일 때만 검사
    print("얇은 긴팔")
else:
    print("겉옷")

age = 15
has_account = True
if age >= 14 and has_account:
    print("디스코드 사용 가능")
if not has_account or age < 14:
    print("가입 조건 확인 필요")
