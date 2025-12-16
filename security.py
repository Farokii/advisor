import jwt
from datetime import timezone, timedelta, datetime
from typing import Optional
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import Settings

settings = Settings()

# 初始化密码哈希上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # JWT令牌获取端点


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希密码是否匹配

    数据流动：
    1. 从用户注册/登录请求获取明文密码
    2. 从数据库获取哈希密码
    3. 使用bcrypt验证匹配
    4. 返回布尔值表示是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码的哈希值

    数据流动：
    1. 获取明文密码
    2. 使用bcrypt生成哈希值
    3. 返回哈希值用于存储
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT访问令牌

    数据流动：
    1. 接收用户ID等数据
    2. 设置令牌过期时间
    3. 使用SECRET_KEY和ALGORITHM签名
    4. 返回JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前认证用户信息

    数据流动：
    1. 从请求头获取JWT令牌
    2. 验证令牌签名和有效期
    3. 从令牌中提取用户ID
    4. 返回用户ID（后续可扩展为完整用户对象）

    注意：此函数将被用作依赖项，用于需要身份验证的接口
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:#except=万一
        raise credentials_exception
    return {"id": int(user_id)}