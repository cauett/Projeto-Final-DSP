# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.routers import categoria, pessoa, memoria, grupo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida da aplicação FastAPI.

    Actions:
        - Inicializa conexão com banco de dados na startup
        - Garante desconexão limpa no shutdown
    """
    await init_db()
    print("Conexão com o MongoDB verificada com sucesso!")

    yield

    print("Encerrando a aplicação...")


app = FastAPI(
    lifespan=lifespan,
    title="API de Memorias Pessoais",
    description="API para gerenciamento de memórias emocionais",
)

# Configura as rotas da aplicação
app.include_router(categoria.router, prefix="/categorias", tags=["Categorias"])
app.include_router(pessoa.router, prefix="/pessoas", tags=["Pessoas"])
app.include_router(memoria.router, prefix="/memorias", tags=["Memórias"])
app.include_router(grupo.router)
