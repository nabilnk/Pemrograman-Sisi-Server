import time
import json
import redis


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)


def get_weather(city):
    cache_key = f"weather:{city.lower()}"

    # GET: cek data dari cache
    cached_data = redis_client.get(cache_key)

    if cached_data:
        print("Data diambil dari Redis cache")
        return json.loads(cached_data)

    # Simulasi API call lambat
    print("Data belum ada di cache, memanggil API...")
    time.sleep(2)

    # Simulasi response API
    result = {
        "city": city,
        "temperature": 30,
        "condition": "Sunny"
    }

    # SET: simpan data ke Redis
    redis_client.set(cache_key, json.dumps(result))

    # EXPIRE: cache berlaku 300 detik / 5 menit
    redis_client.expire(cache_key, 300)

    return result