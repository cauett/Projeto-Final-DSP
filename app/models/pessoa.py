# pessoa.py
from beanie import Document, Indexed
from datetime import date
from typing import List, Optional


class Pessoa(Document):
    """
    Representa uma pessoa associada às memórias registradas.

    Attributes:
        nome (Indexed(str)): Nome completo com índice único
        data_nascimento (date): Data de nascimento no formato AAAA-MM-DD
        memorias (Optional[List[str]]): Lista de títulos de memórias associadas
    """

    nome: Indexed(str, unique=True)
    data_nascimento: date
    memorias: Optional[List[str]] = []

    class Settings:
        """Configurações do banco de dados para a coleção de pessoas"""

        collection = "pessoas"
