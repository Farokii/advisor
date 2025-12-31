import pytest
import asyncio
from sqlalchemy import inspect
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from SQL.database import Base, get_db
from routers import users, advisors
from httpx import AsyncClient, ASGITransport
import os

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL) # 连接池

# 创建测试数据库
@pytest.fixture(scope="session", autouse=True)
async def ini_table():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# 确保异步后段统一性
@pytest.fixture(scope="session")
async def anyio_backend():
    return 'asyncio'

# 创建测试app
@pytest.fixture(scope="function")
async def test_app(test_session) -> FastAPI:
    app = FastAPI(version="1.0.0")
    app.include_router(users.router)
    app.include_router(advisors.router)

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    return app


# 创建测试客户端
@pytest.fixture(scope="function")
async def client(test_app: FastAPI):
    transport = ASGITransport(test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as aclient:
        yield aclient


# 创建数据库会话
@pytest.fixture(scope="function")
async def test_session():
    conn = await test_engine.connect()
    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    #await conn.begin_nested()
    try:
        yield session
    finally:
        await trans.rollback()
        await session.close()
        await conn.close()
