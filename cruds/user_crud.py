from models import user_model,advisor_model
from schemas import user_schema, advisor_schema
from sqlalchemy.orm import Session
from security import get_password_hash,verify_password

def get_user_by_phone(db:Session,phone:str):
    return db.query(user_model.User).filter(user_model.User.phone_number==phone).first()

def create_user(db:Session,user:user_schema.UserCreate):
    #生成哈希密码
    hashed_password = get_password_hash(user.password)
    #创建用户数据库对象
    db_user=user_model.User(
        phone_number=user.phone_number,
        password=hashed_password,
        name=user.name,
        birth=user.birth,
        gender=user.gender,
        bio=user.bio,
        about=user.about,

    )
    #添加到数据库会话（加入购物车）
    db.add(db_user)
    #提交事务，执行数据库操作（结账）
    db.commit()
    #刷新对象，获取数据库生成的ID（在一步之前db_user中的id,created_at等系统字段还未更新）
    db.refresh(db_user)
    return db_user

def update_user_profile(db:Session,user_id:int,user:user_schema.UserUpdate):
    db_user=db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user is None:
        return None

    update_data=user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user