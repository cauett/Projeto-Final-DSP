from dotenv import load_dotenv
import os

load_dotenv()

# Carregar a URL do MongoDB do .env
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise ValueError("MONGO_URL não encontrado no ambiente. Configure corretamente no .env")
