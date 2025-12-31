from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from config import Settings

#所有表需要继承同一个base，不然create_all不会生效
Base = declarative_base()

#SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:123@127.0.0.1:3308/db1"

engine = create_async_engine(
    Settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()