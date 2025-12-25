import security
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from schemas import advisor_schema, order_schema
from cruds import advisor_crud, order_crud
from models import order_model
from coin_trans import get_coin_trans
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
            detail="Failed to update advisor profile",
        )
    return updated_advisor
#4.顾问端-主页
def profile(db: Session, advisor_id: int):
    advisor_profile = advisor_crud.profile(db, advisor_id)
    if advisor_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to view profile",
        )
    return advisor_crud.profile(db, advisor_id)
#5.顾问端-接单状态更新
def update_work_status(db: Session, advisor_id: int, advisor: advisor_schema.UpdateWorkStatus):
    updated_advisor = advisor_crud.update_work_status(db, advisor_id, advisor)
    if updated_advisor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update advisor work status",
        )
    return updated_advisor
#6.顾问端-服务状态修改
def update_service_status(db: Session, advisor_id: int, advisor: advisor_schema.UpdateServiceStatus):
    updated_advisor = advisor_crud.update_service_status(db, advisor_id, advisor)
    if updated_advisor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update advisor service status",
        )
    return updated_advisor
#7.顾问端-价格修改
def update_price(db: Session, advisor_id: int, advisor: advisor_schema.UpdatePrice):
    updated_advisor = advisor_crud.update_price(db, advisor_id, advisor)
    if updated_advisor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update advisor price",
        )
    return updated_advisor
# 8.顾问端-查看订单列表
def order_list(db: Session, advisor_id: int):
    return order_crud.advisor_order_list(db, advisor_id)
# 9.顾问端-查看订单详情
def order_details(db: Session, advisor_id: int, order_id: int):
    order = order_crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if order.advisor_id != advisor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The advisor {advisor_id} is not allowed to see order {order_id} details",
        )
    return order_crud.get_order_details(db, order_id)
# 10.顾问端-回复订单
def complete_order(db: Session, advisor_id: int, order_id: int, reply: advisor_schema.Reply):
    order = order_crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if order.advisor_id != advisor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Advisor {advisor_id} is not allowed to complete order {order_id}",
        )
    if order.order_status != order_model.OrderStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order {order_id} is not pending",
        )
    return order_crud.complete_order(db, order_id, advisor_id,reply)

#顾问端-流水列表
def coin_trans(advisor_id: int):
    logs=get_coin_trans("advisor", advisor_id)
    return [
        order_schema.CoinTransResponse(
            type=log.get("type"),
            credit=log.get("credit"),
            time=log.get("time"),
        )for log in logs
    ]
