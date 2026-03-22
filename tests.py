import pytest
import numpy as np
from models import UserCreate
from embeddings import generate_embedding
from vector_store import add_vector, search_vectors
from database import create_user, get_user_id, list_users, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = async_sessionmaker(test_engine, class_=AsyncSession)

@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_generate_embedding_dimension():
    result = generate_embedding("texto de teste")
    assert len(result) == 384
    assert isinstance(result[0], float)

@pytest.mark.asyncio
async def test_add_and_search_vector():
    
    vector = [0.1] * 384
    embedding_id = add_vector(vector)
    assert isinstance(embedding_id, int)
    results = search_vectors(vector, k=1)
    assert isinstance(results[0][0], (int, np.integer))
    assert isinstance(results[0][1], (float, np.floating))

@pytest.mark.asyncio
async def test_create_and_get_user():
    
    async with TestSession() as session:
        user_data = UserCreate(name="Test User", email="test@example.com", description="teste")
        user = await create_user(session, user_data)
        user = await get_user_id(session, user.id)
        assert user.name == "Test User"
        assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_list_users():
    
    async with TestSession() as session:
        user_data1 = UserCreate(name="User One", email="user1@example.com", description="teste")
        user_data2 = UserCreate(name="User Two", email="user2@example.com", description="teste")
        await create_user(session, user_data1)
        await create_user(session, user_data2)
        
        users = await list_users(session)
        assert len(users) == 2
        assert users[0].name == "User One"
        assert users[1].name == "User Two"