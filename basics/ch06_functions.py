# 기초 다지기 5장 예제
def outfit(t_max: float) -> str:
    """최고 기온에 맞는 옷을 돌려준다."""
    if t_max >= 28:
        return "반팔"
    if t_max >= 20:
        return "얇은 긴팔"
    return "겉옷"


def greet(name: str, emoji: str = "👋") -> str:
    return f"{emoji} {name}님 안녕하세요"


print(outfit(30), outfit(21.5), outfit(5))
print(greet("시온"))
print(greet("바다", emoji="🎉"))      # 키워드 인자: 이름을 붙여 넘기기
