from redis.asyncio import Redis
from config import Settings # 或从 config.py 导入
settings = Settings()
# --- 在这个专用模块中初始化 ---
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
