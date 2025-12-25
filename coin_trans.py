from datetime import datetime, timedelta, timezone
import json, time
from redis_client import redis_client
from config import Settings

settings = Settings()

def add_coin_trans(user_type: str, user_id: int, log_type: str, credit: str):
    key = f"coin_trans:{user_type}:{user_id}"
    now = int(time.time()) # 时间戳，类似1717236000，用作score
    log = json.dumps(
        {
            "type": log_type,
            "credit": credit,
            "time": datetime.now(timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    redis_client.zadd(key, {log: now}) # 向sortedset中添加流水记录
    redis_client.zremrangebyscore(key, 0, now-settings.COIN_TRANS_EXPIRE_DAYS * 24 * 3600) # 删除过期流水信息
    return

def get_coin_trans(user_type: str, user_id: int):
    key = f"coin_trans:{user_type}:{user_id}"
    now = int(time.time()) # 时间戳，类似1717236000，用作score
    redis_client.zremrangebyscore(key, 0, now - settings.COIN_TRANS_EXPIRE_DAYS * 24 * 3600)  # 删除过期流水信息
    # 倒序排列，最新在前
    logs_raw = redis_client.zrevrange(key, 0 ,-1) # 取所有记录
    logs = []
    for item in logs_raw:
        try:
            log = json.loads(item)
            logs.append(log)
        except json.decoder.JSONDecodeError:
            continue

    return logs

