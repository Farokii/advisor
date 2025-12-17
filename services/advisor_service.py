import security
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from schemas import advisor_schema
from cruds import advisor_crud
#1.顾问端-注册
def register(db: Session, advisor: advisor_schema.AdvisorCreate):
    #检查手机号是否已注册
    db_advisor=advisor_crud.get_advisor_by_phone(db, phone=advisor.phone_number)
    if db_advisor:
        raise HTTPException(status_code=400, detail="Phone already registered")
    return advisor_crud.create_advisor(db,advisor)

#2.顾问端-登录
def login(db: Session, advisor: advisor_schema.AdvisorLogin):
    # 通过手机号验证登录用户是否存在
    db_advisor = advisor_crud.get_advisor_by_phone(db, advisor.phone_number)
    if not db_advisor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",  # 不要透露是手机号泄漏了还是密码错了，方式信息泄漏
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not security.verify_password(advisor.password, db_advisor.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = security.create_access_token(
        data={"sub": str(db_advisor.id)},
        #expires_delta=access_token_expires
    )
    return {"access_token":access_token,"token_type":"bearer"}

#3.顾问端-信息修改
def update_profile(db: Session, advisor: advisor_schema.AdvisorUpdateProfile, advisor_id: int):
    updated_advisor = advisor_crud.update_profile(db, advisor, advisor_id)
    if updated_advisor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user profile",
        )
    return updated_advisor