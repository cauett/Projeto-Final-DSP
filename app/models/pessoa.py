from beanie import Document, Indexed
from datetime import date
from typing import List, Optional

class Pessoa(Document):
    """
    Representa uma pessoa no sistema.
    """
    nome: Indexed(str, unique=True)  # Índice único para otimizar buscas por nome
    data_nascimento: date  # Data de nascimento
    memorias: Optional[List[str]] = []  # Agora armazena nomes das memórias em vez de IDs

    class Settings:
        collection = "pessoas"
