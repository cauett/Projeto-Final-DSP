from pydantic import BaseModel
from typing import Optional
from datetime import date

class Memoria(BaseModel):
    """
    Representa uma memória no sistema.
    """
    _id: Optional[str] = None  # ObjectId do MongoDB convertido para string
    titulo: str
    descricao: str
    data: date  # Data da memória
    emocao: str  # Exemplo: "Feliz", "Triste"
    categoria_id: Optional[int]  # Referência para Categoria (ID numérico)
    pessoa_id: Optional[str]  # Referência para Pessoa (ObjectId convertido para string)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {date: lambda d: d.strftime("%Y-%m-%d")}
