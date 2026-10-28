# 기초 다지기 9장 예제
import asyncio


async def cook(menu: str, seconds: int):
    await asyncio.sleep(seconds)       # 기다리는 동안 다른 일을 할 수 있다
    return f"{menu} 완성"


async def main():
    results = await asyncio.gather(cook("라면", 1), cook("만두", 1))
    print(results)


asyncio.run(main())
