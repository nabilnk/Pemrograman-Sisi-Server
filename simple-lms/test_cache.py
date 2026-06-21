import time
from weather_api import get_weather


start = time.time()
result1 = get_weather("Jakarta")
time1 = time.time() - start
print(f"First call: {time1:.2f}s")
print(result1)

print("-" * 40)

start = time.time()
result2 = get_weather("Jakarta")
time2 = time.time() - start
print(f"Second call (cached): {time2:.2f}s")
print(result2)

print("-" * 40)

print("Third call setelah 5 menit akan lambat lagi karena cache Redis sudah expired.")