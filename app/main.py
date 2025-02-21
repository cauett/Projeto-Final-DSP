from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.routers import categoria, pessoa, memoria

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação."""
    await init_db()  # Inicializa o Beanie e verifica a conexão
    print("Conexão com o MongoDB verificada com sucesso!")
    
    yield  # A aplicação está pronta para receber requisições

    print("Encerrando a aplicação...")

# Passa o gerenciador de ciclo de vida para o FastAPI
app = FastAPI(lifespan=lifespan)

# Configura as rotas da aplicação
app.include_router(categoria.router, prefix="/categorias", tags=["Categorias"])
app.include_router(pessoa.router, prefix="/pessoas", tags=["Pessoas"])
app.include_router(memoria.router, prefix="/memorias", tags=["Memórias"])
