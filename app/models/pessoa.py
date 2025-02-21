from beanie import Document
from datetime import date
from typing import List, Optional

class Pessoa(Document):
    """
    Representa uma pessoa no sistema.
    """
    nome: str  # Nome único da pessoa
    data_nascimento: date  # Data de nascimento
    memorias: Optional[List[str]] = []  # Agora armazena nomes das memórias em vez de IDs

    class Settings:
        collection = "pessoas"
