# 기초 다지기 3장 예제
menu = ["짜장", "짬뽕"]
menu.append("볶음밥")          # 맨 뒤에 추가
print(menu, len(menu))
print(menu[0], menu[-1])
menu.remove("짬뽕")            # 값으로 지우기
print(menu)
first = menu.pop(0)            # 0번을 꺼내며 지우기
print(first, menu)
