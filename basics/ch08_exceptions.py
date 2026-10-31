# 기초 다지기 7장 예제
def to_number(text: str):
    try:
        return int(text)
    except ValueError:
        return None


print(to_number("42"), to_number("사십이"))

scores = {"시온": 12}
try:
    print(scores["바다"])
except KeyError as error:
    print("없는 이름:", error)
finally:
    print("검사 끝")
