# models/grupo.py
from beanie import Document, Link, Indexed
from pydantic import BaseModel, Field
from typing import List
from .pessoa import Pessoa
from .memoria import Memoria

class PessoaRef(BaseModel):
    """
    Representa uma referência a uma pessoa dentro de um grupo.
    
    Attributes:
        id (str): Identificador único da pessoa.
        nome (str): Nome da pessoa.
        memorias (List[str]): Lista de identificadores das memórias associadas.
    """
    id: str  
    nome: str
    memorias: List[str] = []

class Grupo(Document):
    """
    Representa um grupo de pessoas associado a memórias compartilhadas.
    
    Attributes:
        nome (Indexed(str)): Nome único do grupo.
        pessoas (List[PessoaRef]): Lista de referências às pessoas que fazem parte do grupo.
    
    Configurações:
        collection (str): Nome da coleção no banco de dados.
    """
    nome: Indexed(str, unique=True) = Field(..., description="Nome do grupo")
    pessoas: List[PessoaRef] = []

    class Settings:
        collection = "grupos"
