# 기초 다지기 4장 예제
ranking = ["하늘", "바다", "구름"]
for i, name in enumerate(ranking, start=1):    # 번호와 값을 함께
    print(f"{i}위 {name}")

for n in range(3):            # 0, 1, 2
    print("주사위", n)

count = 3
while count > 0:              # 조건이 참인 동안 반복
    print(count)
    count = count - 1
print("발사!")
