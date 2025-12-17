from models import advisor_model
from schemas import advisor_schema
from sqlalchemy.orm import Session
from security import get_password_hash

def get_advisor_by_phone(db:Session,phone:str):
    return db.query(advisor_model.Advisor).filter(advisor_model.Advisor.phone_number==phone).first()

def create_advisor(db:Session, advisor: advisor_schema.AdvisorCreate):
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
    db.commit()
    db.refresh(db_advisor)
    return db_advisor

def update_profile(db:Session, advisor: advisor_schema.AdvisorUpdateProfile, advisor_id:int):
    db_advisor = db.query(advisor_model.Advisor).filter(advisor_model.Advisor.id == advisor_id).first()
    if db_advisor is None:
        return None
    update_data = advisor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_advisor, key, value)
    db.commit()
    db.refresh(db_advisor)
    return db_advisor

