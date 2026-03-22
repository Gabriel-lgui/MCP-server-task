import logging
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from models import UserCreate, UserReturn
from database import (
    start_db, AsyncSessionLocal,
    create_user as db_create_user,
    get_user_id,
    get_user_embedding_id,
    list_users as db_list_users
)
from vector_store import add_vector, search_vectors, save_index, load_index, INDEX_PATH
from embeddings import generate_embedding

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("user-server")

# Inicialização do banco e do índice FAISS
@asynccontextmanager
async def lifespan(server):
    await start_db()
    logger.info("Banco de dados iniciado e tabelas criadas.")
    load_index(INDEX_PATH)
    logger.info("Índice FAISS carregado.")
    yield

# Criação do servidor MCP
mcp = FastMCP("user-server", lifespan=lifespan)

# Tools
@mcp.tool()
async def create_user(name: str, email: str, description: str) -> dict:
    try:
        async with AsyncSessionLocal() as session:
            user_data = UserCreate(name=name, email=email, description=description)
            new_user = await db_create_user(session, user_data)
            embedding = generate_embedding(description)
            embedding_id = add_vector(embedding)
            new_user.embedding_id = embedding_id
            await session.commit()
            save_index(INDEX_PATH)
        logger.info(f"Usuário criado com ID {new_user.id}")
        return {"id": new_user.id}
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        return {"error": str(e)}

@mcp.tool()
async def search_users(query: str, top_k: int) -> list[dict]:
    try:
        embedding = generate_embedding(query)
        search_results = search_vectors(embedding, k=top_k)
        async with AsyncSessionLocal() as session:
            users = []
            for embedding_id, distance in search_results:
                user = await get_user_embedding_id(session, int(embedding_id))
                if user:
                    users.append({
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "description": user.description,
                        "score": float(distance)
                    })
        logger.info(f"Busca por '{query}': {len(users)} usuários encontrados.")
        return users
    except Exception as e:
        logger.error(f"Erro ao buscar usuários: {e}")
        return {"error": str(e)}

@mcp.tool()
async def get_user(user_id: int) -> dict:
    try:
        async with AsyncSessionLocal() as session:
            user = await get_user_id(session, user_id)
        if user:
            return UserReturn.model_validate(user).model_dump()
        logger.warning(f"Usuário id={user_id} não encontrado.")
        return {"error": f"Usuário id={user_id} não encontrado."}
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return {"error": str(e)}

@mcp.tool()
async def list_users() -> list[dict]:
    try:
        async with AsyncSessionLocal() as session:
            users = await db_list_users(session)
        logger.info(f"Listando usuários: {len(users)} encontrados.")
        return [UserReturn.model_validate(u).model_dump() for u in users]
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")