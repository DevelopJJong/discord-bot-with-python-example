# 기초 다지기 4장 예제
scores = [80, 45, 92, 67]
passed = [s for s in scores if s >= 60]        # 리스트 컴프리헨션
print(passed, sum(scores), max(scores))
words = ["바보", "안녕"]
print(any(w in "너 바보야" for w in words))    # 하나라도 들어 있나?
