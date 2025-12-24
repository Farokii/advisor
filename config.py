import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    """应用配置类，管理所有环境变量"""
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")  # 用于JWT签名的密钥
    ALGORITHM: str = "HS256"  # JWT使用的算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # JWT令牌过期时间(分钟)
    URGENT_EXPIRE_MINUTES: int = 5 # 加急订单过期时间(分钟)
    NORMAL_EXPIRE_MINUTES: int = 10 # 普通订单过期时间(分钟）
    # 数据库配置
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "advisor_db")

    # 构建数据库连接URL
    DATABASE_URL: str = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

    #Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

    ORDER_DETAILS_EXPIRE_MINUTES: int = 60
    REVIEW_EXPIRE_MINUTES: int = 30
    COIN_TRANS_EXPIRE_DAYS: int = 3

    DEBUG: bool = os.getenv("DEBUG", "False") == "True"  # 调试模式