from models import advisor_model
from schemas import advisor_schema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from security import get_password_hash
from fastapi import HTTPException, status

async def get_advisor_by_phone(db: AsyncSession, phone: str):
    db_advisor = (await db.execute(
        select(advisor_model.Advisor).where(advisor_model.Advisor.phone_number == phone)
    )).scalar_one_or_none()
    return db_advisor


async def get_advisor_by_id(db: AsyncSession, advisor_id: int):
    db_advisor = (await db.execute(
        select(advisor_model.Advisor).where(advisor_model.Advisor.id == advisor_id)
    )).scalar_one_or_none()
    return db_advisor


async def create_advisor(db: AsyncSession, advisor: advisor_schema.AdvisorCreate):
    hashed_password = get_password_hash(advisor.password)
    db_advisor = advisor_model.Advisor(
        phone_number=advisor.phone_number,
        password=hashed_password,
        name=advisor.name,
        bio=advisor.bio,
        about=advisor.about,
        work_experience=advisor.work_experience
    )
    db.add(db_advisor)
    await db.commit()
    await db.refresh(db_advisor)
    return db_advisor


async def update_profile(db: AsyncSession, advisor: advisor_schema.AdvisorUpdateProfile, advisor_id: int):
    db_advisor = await get_advisor_by_id(db, advisor_id)

    if db_advisor is None:
        raise HTTPException(status_code=404, detail="Advisor not found")

    update_data = advisor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advisor, key, value)
    await db.commit()
    await db.refresh(db_advisor)
    return db_advisor

async def profile(db: AsyncSession, advisor_id: int):
    db_advisor = await get_advisor_by_id(db, advisor_id)

    if db_advisor is None:
        return None
    return db_advisor

async def update_work_status(db: AsyncSession, advisor_id: int, advisor: advisor_schema.UpdateWorkStatus):
    db_advisor = await get_advisor_by_id(db, advisor_id)

    if db_advisor is None:
        return None

    db_advisor.work_status = advisor.work_status

    await db.commit()
    await db.refresh(db_advisor)
    return db_advisor

async def update_service_status(db: AsyncSession, advisor_id: int, advisor: advisor_schema.UpdateServiceStatus):
    db_advisor = await get_advisor_by_id(db, advisor_id)

    if db_advisor is None:
        return None

    db_advisor.service_status = advisor.service_status

    await db.commit()
    await db.refresh(db_advisor)
    return db_advisor

async def update_price(db: AsyncSession, advisor_id: int, advisor: advisor_schema.UpdatePrice):
    db_advisor = await get_advisor_by_id(db, advisor_id)

    if db_advisor is None:
        return None

    update_data = advisor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advisor, key, value)

    await db.commit()
    await db.refresh(db_advisor)
    return db_advisor