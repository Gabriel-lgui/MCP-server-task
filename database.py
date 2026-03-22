import os
import sqlalchemy as sqla
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from models import UserCreate
from dotenv import load_dotenv


load_dotenv() # Usado para chamar DATABASE_URL do .env
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./users.db")
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)
async def start_db(): # Inicia o banco de dados e cria as tabelas, deve ser chamado no startup do servidor  
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 

class User(Base): # Modelo ORM para SQLAlchemy para criar a tabela de usuários no banco de dados
    
    __tablename__ = 'users'

    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.String, nullable=False)
    email = sqla.Column(sqla.String, nullable=False, unique=True)
    description = sqla.Column(sqla.String)
    embedding_id = sqla.Column(sqla.Integer, nullable=True)

async def create_user(session, user_data:UserCreate) -> User:
    
    new_user = User(name=user_data.name, email=user_data.email, description=user_data.description, embedding_id=None)
    session.add(new_user)
    await session.flush() # Flush para obter o ID do usuário antes de commit, para associar o embedding_id posteriormente
    await session.commit()
    await session.refresh(new_user)
    
    return new_user
        
async def get_user_id(session, user_id:int) ->User | None:
    
    result = await session.execute(sqla.select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    return user

async def get_user_embedding_id(session, embedding_id:int) -> User | None:
    
    result = await session.execute(sqla.select(User).where(User.embedding_id == embedding_id))
    user = result.scalar_one_or_none()
    
    return user
    
async def list_users(session) -> list[User]:
    
    result = await session.execute(sqla.select(User))
    users = result.scalars().all()
    
    return users