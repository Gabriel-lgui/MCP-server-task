import os
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from models import UserCreate
from dotenv import load_dotenv

load_dotenv()
Base = declarative_base()
engine = create_async_engine(os.getenv("DATABASE_URL"))
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class User(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, unique=True)
    description = sa.Column(sa.String)
    embedding_id = sa.Column(sa.Integer, nullable=True)

async def create_user(session, user_data:UserCreate) -> User:
    new_user = User(name=user_data.name, email=user_data.email, description=user_data.description, embedding_id=None)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
        
async def get_user_by_id(session, user_id:int) ->User | None:
    result = await session.execute(sa.select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user

async def get_user_embedding_id(session, embedding_id:int) -> User | None:
    result = await session.execute(sa.select(User).where(User.embedding_id == embedding_id))
    user = result.scalar_one_or_none()
    return user
    
async def list_users(session) -> list[User]:
    result = await session.execute(sa.select(User))
    users = result.scalars().all()
    return users