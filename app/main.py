from fastapi import FastAPI
from app.database import get_database
from app.routers import categoria, pessoa, memoria

app = FastAPI()

"""
Aplicação principal da API para gerenciamento de categorias, pessoas e memórias.
"""

# Configura as rotas da aplicação
app.include_router(categoria.router, prefix="/categorias", tags=["Categorias"])
app.include_router(pessoa.router, prefix="/pessoas", tags=["Pessoas"])
app.include_router(memoria.router, prefix="/memorias", tags=["Memórias"])
