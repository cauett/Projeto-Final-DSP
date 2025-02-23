# memoria.py
from beanie import Document, Indexed
from datetime import date
from typing import Optional
from .categoria import Categoria
from .pessoa import Pessoa

class Memoria(Document):
    """
    Representa uma memória associada a experiências pessoais.
    
    Attributes:
        titulo (Indexed(str)): Título da memória com índice de texto para buscas
        descricao (str): Descrição detalhada do acontecimento
        data (date): Data em que a memória foi registrada
        emocao (str): Estado emocional associado (ex: Feliz, Triste)
        categoria (Optional[Categoria]): Categoria de classificação da memória
        pessoa (Optional[Pessoa]): Pessoa associada à memória
    """
    titulo: Indexed(str, index_type="text")
    descricao: str
    data: date
    emocao: str
    categoria: Optional[Categoria] = None
    pessoa: Optional[Pessoa] = None

    class Settings:
        """Configurações do banco de dados para a coleção de memórias"""
        collection = "memorias"