from mcp.server.fastmcp import FastMCP
from database import AsyncSessionLocal, create_user, get_user_by_id, init_db, list_users
from embeddings import generate_embedding

mcp = FastMCP("user-server")

@mcp.on_startup
async def startup():
    await init_db()