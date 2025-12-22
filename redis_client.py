import redis
from config import Settings # 或从 config.py 导入
settings = Settings()
# --- 在这个专用模块中初始化 ---
redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL)
redis_client = redis.Redis(connection_pool=redis_pool)