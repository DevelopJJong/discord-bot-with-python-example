# 기초 다지기 9장 예제
from pathlib import Path

with open("memo.txt", "w", encoding="utf-8") as f:    # 파일을 열고
    f.write("봇 메모")                                 # 쓰고
# with 블록이 끝나면 파일이 자동으로 닫힌다
print(Path("memo.txt").read_text(encoding="utf-8"))
