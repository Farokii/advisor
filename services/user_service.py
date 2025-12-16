#处理业务逻辑，与数据库操作解耦
from passlib.handlers.django import django_bcrypt_sha256

import crud,security
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from schemas import user_schema
#1.用户端-注册
def register_user(db: Session, user: user_schema.UserCreate):
    #检查手机号是否已注册
    db_user=crud.get_user_by_phone(db, phone=user.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")
    return crud.create_user(db,user)

#2.用户端-登录
def login_user(db: Session, user: user_schema.UserLogin):
    # 通过手机号验证登录用户是否存在
    db_user = crud.get_user_by_phone(db, user.phone_number)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",  # 不要透露是手机号泄漏了还是密码错了，方式信息泄漏
            headers={"WWW-Authenticate": "Bearer"}
        )
    # 验证密码是否正确
    if not security.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    #账号密码匹配成功，生成token
    from datetime import timedelta
    from config import Settings
    settings = Settings()
    #定义令牌过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    #创建令牌
    access_token = security.create_access_token(
        data={"sub": str(db_user.id)},#加入type，区分用户和顾问
        expires_delta=access_token_expires
    )
    return {"access_token":access_token,"token_type":"bearer"}

#用户端-更新个人信息
#def update_user_profile(db: Session,id:int,user: user_schema.UserUpdate,):
