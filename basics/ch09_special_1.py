# 기초 다지기 9장 예제
commands = {}


def command(name: str):
    def register(func):
        commands[name] = func      # 함수를 이름표와 함께 등록
        return func
    return register


@command("안녕")
def hello():
    return "안녕하세요!"


print(commands["안녕"]())
