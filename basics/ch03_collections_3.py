# 기초 다지기 3장 예제
data = {
    "current": {"temperature_2m": 17.7, "weather_code": 3},
    "daily": {"temperature_2m_max": [18.0, 20.1]},
}
print(data["current"]["temperature_2m"])
print(data["daily"]["temperature_2m_max"][0])
point = (37.46, 126.71)            # 튜플: 바꿀 수 없는 리스트
lat, lon = point                   # 한 번에 나눠 담기
print(lat, lon)
