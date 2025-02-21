from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.models.memoria import Memoria
from app.models.categoria import Categoria
from app.models.pessoa import Pessoa
from beanie import PydanticObjectId

router = APIRouter()

@router.post("/", response_model=Memoria)
async def criar_memoria(memoria: Memoria):
    """
    Cria uma nova memória, verificando se a `pessoa_id` e `categoria_id` existem.
    """
    # Verifica se a pessoa existe
    if memoria.pessoa and not await Pessoa.get(memoria.pessoa.id):
        raise HTTPException(status_code=400, detail="Pessoa não encontrada")

    # Verifica se a categoria existe
    if memoria.categoria and not await Categoria.get(memoria.categoria.id):
        raise HTTPException(status_code=400, detail="Categoria não encontrada")

    # Salvar no MongoDB usando Beanie
    await memoria.insert()
    return memoria

@router.get("/", response_model=List[Memoria])
async def listar_memorias(
    limit: int = Query(10, description="Número máximo de memórias a retornar"),
    skip: int = Query(0, description="Número de registros a pular")
):
    """
    Lista todas as memórias com paginação.
    """
    memorias = await Memoria.find().skip(skip).limit(limit).to_list()
    return memorias

@router.get("/{id}", response_model=Memoria)
async def obter_memoria(id: str):
    """
    Obtém uma memória específica pelo `_id`.
    """
    memoria = await Memoria.get(PydanticObjectId(id))
    if not memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

    return memoria

@router.put("/{id}", response_model=Memoria)
async def atualizar_memoria(id: str, memoria: Memoria):
    """
    Atualiza os dados de uma memória existente.
    """
    existing_memoria = await Memoria.get(PydanticObjectId(id))
    if not existing_memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

    # Atualizar os campos
    existing_memoria.titulo = memoria.titulo
    existing_memoria.descricao = memoria.descricao
    existing_memoria.data = memoria.data
    existing_memoria.emocao = memoria.emocao
    existing_memoria.categoria = memoria.categoria
    existing_memoria.pessoa = memoria.pessoa

    await existing_memoria.save()
    return existing_memoria

@router.delete("/{id}")
async def excluir_memoria(id: str):
    """
    Exclui uma memória pelo `_id`.
    """
    memoria = await Memoria.get(PydanticObjectId(id))
    if not memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

    await memoria.delete()
    return {"message": "Memória excluída com sucesso"}

@router.get("/categoria/{categoria_id}", response_model=List[Memoria])
async def listar_memorias_por_categoria(categoria_id: int):
    """
    Lista todas as memórias associadas a uma determinada categoria.
    """
    categoria = await Categoria.find_one(Categoria.categoria_id == categoria_id)

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    memorias = await Memoria.find(Memoria.categoria == categoria).to_list()

    if not memorias:
        raise HTTPException(status_code=404, detail="Nenhuma memória encontrada para esta categoria")

    return memorias

@router.get("/pessoa/{pessoa_id}", response_model=List[Memoria])
async def listar_memorias_por_pessoa(pessoa_id: PydanticObjectId):
    """
    Lista todas as memórias associadas a uma determinada pessoa.
    """
    pessoa = await Pessoa.get(pessoa_id)

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    memorias = await Memoria.find(Memoria.pessoa == pessoa).to_list()

    if not memorias:
        raise HTTPException(status_code=404, detail="Nenhuma memória encontrada para esta pessoa")

    return memorias
