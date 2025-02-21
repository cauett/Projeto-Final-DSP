from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class Pessoa(BaseModel):
    """
    Representa uma pessoa no sistema.
    """
    _id: Optional[str] = None  # ObjectId do MongoDB convertido para string
    nome: str  # Nome único da pessoa
    data_nascimento: date  # Data de nascimento
    memorias: Optional[List[str]] = []  # Lista de IDs de memórias associadas

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {date: lambda d: d.strftime("%Y-%m-%d")}
