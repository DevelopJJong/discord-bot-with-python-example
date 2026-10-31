# 기초 다지기 8장 예제
class Pet:
    def __init__(self, name: str):     # 객체를 만들 때 한 번 실행
        self.name = name               # self.이름 = 이 객체의 속성
        self.level = 1

    def level_up(self):                # 메서드: 첫 매개변수는 늘 self
        self.level += 1
        return f"{self.name} 레벨 {self.level}!"


a = Pet("뭉치")
b = Pet("구름")
print(a.level_up(), a.level_up())
print(b.name, b.level)


class RobotPet(Pet):                   # Pet 의 기능을 모두 물려받는다
    def __init__(self, name: str, battery: int):
        super().__init__(name)         # 부모(Pet)의 __init__ 도 실행
        self.battery = battery

    def level_up(self):                # 부모의 메서드를 새로 정의(덮어쓰기)
        self.battery -= 10
        return super().level_up() + f" (배터리 {self.battery}%)"


r = RobotPet("삐삐", 100)
print(r.level_up())
print(isinstance(r, Pet))
