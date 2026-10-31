# 기초 다지기 2장 예제
text = "  사과, 바나나, 포도  "
clean = text.strip()                 # 앞뒤 빈칸 지우기
fruits = clean.split(", ")           # 쉼표로 나눠 리스트로
print(clean)
print(fruits)
print(" / ".join(fruits))            # 리스트를 하나의 문자열로
print(len("디스코드"), "봇" in "디스코드봇")
word = "Python"
print(word[0], word[-1], word[0:3])  # 첫 글자, 마지막 글자, 0~2번째
print("오늘 급식<br/>김치".replace("<br/>", " "))
