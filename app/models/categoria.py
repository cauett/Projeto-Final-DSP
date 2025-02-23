# categoria.py
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional

class Categoria(Document):
    """
    Representa uma categoria para classificação de memórias.
    
    Attributes:
        categoria_id (Indexed(int)): Identificador único numérico da categoria
        nome (str): Nome descritivo da categoria

    Raises:
        ValueError: Se categoria_id não for único na coleção
    """
    categoria_id: Indexed(int, unique=True)
    nome: str = Field(..., description="Nome da categoria")

    class Settings:
        """Configurações do banco de dados para a coleção de categorias"""
        collection = "categorias"