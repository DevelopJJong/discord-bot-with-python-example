# 나만의 디스코드 봇 만들기 (with Python) — 예제 코드

C&AI Institute가 쓴 책 《나만의 디스코드 봇 만들기 (with Python)》의 예제 코드 저장소입니다.
책의 따라 만들기 코드와 요구사항 미션 해답을 부별로 모았습니다.

## 폴더 구성

| 폴더 | 내용 |
| --- | --- |
| basics/ | PART 0 준비하기 — 파이썬 핵심 문법 예제 (파일 이름의 번호는 장 번호, ch02~ch10) |
| part2/ | 2부 discord.py로 기능 만들기 — 완성 bot.py (본문 + 미션 해답, 8장 Components V2 포함) |
| part3/ | 3부 외부 API와 데이터 저장 — 1~8장 완성 bot.py (본문 + 미션 해답) |
| part3_cog/ | 3부 9장 — Cog로 나눈 구조 (bot.py + cogs/) |
| part4/ | 4부 24시간 봇 운영하기 — 운영용 bot.py, cogs/ops.py, systemd 서비스 파일, update.sh |

## 실행 방법

1. Python 3.10 이상과 PyCharm을 설치합니다 (책 1부 11장).
2. 이 저장소를 내려받아 PyCharm에서 엽니다. 가상환경(Project venv)을 만들고 Terminal에서 설치합니다.

   ```
   pip install -r requirements.txt
   ```

3. 실행할 폴더(예: part2)에 `.env.example`을 복사해 `.env`를 만들고, 내 봇의 토큰과 서버 ID를 적습니다.
4. 그 폴더의 `bot.py`를 실행합니다 (PyCharm: 우클릭 → Run 'bot').

> **토큰은 절대 커밋하지 마세요.** `.env`는 `.gitignore`에 들어 있어 GitHub에 올라가지 않습니다.

## 외부 API와 데이터 출처

- 날씨: [Open-Meteo](https://open-meteo.com) (CC BY 4.0, 비상업적 용도)
- 학교·급식: [나이스 교육정보 개방 포털](https://open.neis.go.kr)
- 미술관 작품: [The Metropolitan Museum of Art Collection API](https://metmuseum.github.io) (CC0)

3부의 급식 코드는 예시 학교 코드(1234567)를 쓰므로, 우리 학교의 코드로 바꿔야 동작합니다 (책 3부 3장).

## 안내

- 코드는 discord.py 2.7.1, Python 3.10 이상에서 확인했습니다. 라이브러리와 외부 API가 바뀌면 동작이 달라질 수 있습니다.
- Discord는 Discord Inc.의 등록 상표이며, 이 저장소와 책은 Discord Inc.의 공식 후원이나 승인을 받지 않은 독립 출판물입니다.
- 문의: C&AI Institute (portal.cnai-ins.com)

## 라이선스

예제 코드는 MIT 라이선스로 자유롭게 쓸 수 있습니다. 책의 본문(글과 그림)은 저작권법의 보호를 받습니다.
