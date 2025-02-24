# config.py
from dotenv import load_dotenv
import os

load_dotenv()

# Carregar a URL do MongoDB do .env
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise ValueError(
        "MONGO_URL não encontrado no ambiente. Configure corretamente no .env"
    )


def get_mongo_url() -> str:
    """Retorna a URL de conexão do MongoDB a partir de variáveis de ambiente.

    Returns:
        str: URL completa de conexão com credenciais

    Raises:
        ValueError: Se a URL não estiver configurada
    """
    return MONGO_URL
