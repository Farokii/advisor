from models import user_model,advisor_model,order_model, review_model, favorites_model
from schemas import user_schema, advisor_schema, review_schema, favorites_schema
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from security import get_password_hash,verify_password
from redis_client import redis_client
from fastapi import APIRouter, Depends, HTTPException, status
from cruds import user_crud, advisor_crud, order_crud
import json

async def save_advisor(db: AsyncSession, user_id: int, advisor_id: int):
    db_advisor = await advisor_crud.get_advisor_by_id(db, advisor_id)
    db_favorite = (await db.execute(
        select(favorites_model.Favorite).where(
            favorites_model.Favorite.user_id == user_id,
            favorites_model.Favorite.advisor_id == advisor_id,
        )
    )).scalar_one_or_none()

    if not db_advisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Advisor not found")
    if db_favorite:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"The user {user_id} has already saved advisor {advisor_id}")
    db_favorite = favorites_model.Favorite(advisor_id=advisor_id, user_id=user_id)
    db.add(db_favorite)
    await db.commit()
    await db.refresh(db_favorite)
    save_advisor_response = favorites_schema.SaveAdvisorResponse(
        advisor_id=advisor_id,
        advisor_name=db_advisor.name,
        bio=db_advisor.bio,
        saved_at=db_favorite.created_at,
    )
    return save_advisor_response


async def unsave_advisor(db: AsyncSession, user_id: int, advisor_id: int):
    db_favorite = (await db.execute(
        select(favorites_model.Favorite).where(
            favorites_model.Favorite.user_id == user_id,
            favorites_model.Favorite.advisor_id == advisor_id,
        )
    )).scalar_one_or_none()
    if not db_favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"The user {user_id} hasn't saved advisor {advisor_id}")

    await db.delete(db_favorite)
    await db.commit()
    return {"message": f"The user {user_id} has successfully unsaved advisor {advisor_id}."}


async def favorites_list(db: AsyncSession, user_id: int):
    db_favorites = (await db.execute(
        select(favorites_model.Favorite).where(favorites_model.Favorite.user_id == user_id).options(
           joinedload(favorites_model.Favorite.advisor),
        )
    )).scalars().all()

    if not db_favorites:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The user {user_id} has not saved advisors.")
    favorites = [
        favorites_schema.SaveAdvisorResponse(
            advisor_id=favorite.advisor.id,
            advisor_name=favorite.advisor.name,
            bio=favorite.advisor.bio,
            saved_at=favorite.created_at,
        ) for favorite in db_favorites
    ]
    return favorites
