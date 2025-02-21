from pydantic import BaseModel
from typing import Optional

class Categoria(BaseModel):
    """
    Representa uma categoria no sistema.
    """
    _id: Optional[str] = None  # ObjectId do MongoDB convertido para string
    id: int  # ID numérico definido pelo usuário
    nome: str  # Nome da categoria

    class Config:
        arbitrary_types_allowed = True
