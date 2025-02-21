from beanie import Document
from datetime import date
from typing import Optional
from .categoria import Categoria
from .pessoa import Pessoa

class Memoria(Document):
    """
    Representa uma memória no sistema.
    """
    titulo: str
    descricao: str
    data: date  # Data da memória
    emocao: str  # Exemplo: "Feliz", "Triste"
    categoria: Optional[Categoria] = None  # Referência para Categoria
    pessoa: Optional[Pessoa] = None  # Referência para Pessoa

    class Settings:
        collection = "memorias"  # Nome da coleção no MongoDB
