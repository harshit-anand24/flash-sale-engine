import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
INVENTORY_KEY = "flash_sale:inventory:shoe_101"

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)