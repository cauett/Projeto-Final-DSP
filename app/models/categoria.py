from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional

class Categoria(Document):
    """
    Modelo da categoria armazenado no MongoDB.
    """
    categoria_id: Indexed(int, unique=True)  # Índice único
    nome: str = Field(..., description="Nome da categoria")

    class Settings:
        collection = "categorias"

class CategoriaResponse(BaseModel):
    """
    Modelo de resposta para ocultar o _id e mostrar apenas o categoria_id.
    """
    categoria_id: int
    nome: str
