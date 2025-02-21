from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URL, os

DB_NAME = os.getenv("MONGO_DB_NAME", "banco-memorias")  # Nome do banco vindo do .env

# Criar conexão com o banco de dados MongoDB
client = AsyncIOMotorClient(MONGO_URL)
database = client[DB_NAME]  # Agora estamos selecionando explicitamente um banco

async def get_database():
    """Retorna a instância do banco de dados MongoDB."""
    return database
