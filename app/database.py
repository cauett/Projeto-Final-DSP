# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import MONGO_URL
from app.models.categoria import Categoria
from app.models.pessoa import Pessoa
from app.models.memoria import Memoria
import os

DB_NAME = os.getenv("MONGO_DB_NAME", "banco-memorias")

# Criar cliente do MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def init_db():
    """Inicializa a conexão com o MongoDB e configura os modelos do Beanie.
    
    Configura:
        - Conexão assíncrona com o banco de dados
        - Registro dos modelos de documento (Categoria, Pessoa, Memoria)
    
    Raises:
        ServerSelectionTimeoutError: Se falhar a conexão com o MongoDB
    """
    await init_beanie(database=db, document_models=[Categoria, Pessoa, Memoria])