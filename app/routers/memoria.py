from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from typing import List, Optional
from datetime import date, datetime
from app.models.memoria import Memoria
from app.database import get_database

router = APIRouter()

@router.post("/", response_model=Memoria)
async def criar_memoria(memoria: Memoria, db=Depends(get_database)):
    """
    Cria uma nova memória, verificando se a `pessoa_id` e `categoria_id` existem.
    """
    memoria_dict = memoria.model_dump()

    # Verifica se a pessoa existe
    if memoria_dict["pessoa_id"] and not await db.pessoas.find_one({"_id": ObjectId(memoria_dict["pessoa_id"])}):
        raise HTTPException(status_code=400, detail="Pessoa não encontrada")

    # Verifica se a categoria existe
    if memoria_dict["categoria_id"] and not await db.categorias.find_one({"id": memoria_dict["categoria_id"]}):
        raise HTTPException(status_code=400, detail="Categoria não encontrada")

    # Converte `data` para `datetime`
    memoria_dict["data"] = datetime.combine(memoria_dict["data"], datetime.min.time())

    # Insere no MongoDB
    result = await db.memorias.insert_one(memoria_dict)

    # Retorna com `_id` convertido para string
    memoria_dict["_id"] = str(result.inserted_id)
    return memoria_dict

@router.get("/", response_model=List[Memoria])
async def listar_memorias(
    db=Depends(get_database),
    limit: int = Query(10, description="Número máximo de memórias a retornar"),
    skip: int = Query(0, description="Número de registros a pular")
):
    """
    Lista todas as memórias com paginação.
    """
    cursor = db.memorias.find().skip(skip).limit(limit)
    memorias = await cursor.to_list(length=limit)
    
    for memoria in memorias:
        memoria["_id"] = str(memoria["_id"])
        if "data" in memoria and isinstance(memoria["data"], datetime):
            memoria["data"] = memoria["data"].date()

    return memorias

@router.get("/{id}", response_model=Memoria)
async def obter_memoria(id: str, db=Depends(get_database)):
    """
    Obtém uma memória específica pelo `_id`.
    """
    memoria = await db.memorias.find_one({"_id": ObjectId(id)})
    if not memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

    memoria["_id"] = str(memoria["_id"])
    if "data" in memoria and isinstance(memoria["data"], datetime):
        memoria["data"] = memoria["data"].date()

    return memoria

@router.put("/{id}", response_model=Memoria)
async def atualizar_memoria(id: str, memoria: Memoria, db=Depends(get_database)):
    """
    Atualiza os dados de uma memória existente.
    """
    memoria_dict = memoria.model_dump(exclude_unset=True)

    # Converte `data` para `datetime`
    if "data" in memoria_dict and isinstance(memoria_dict["data"], date):
        memoria_dict["data"] = datetime.combine(memoria_dict["data"], datetime.min.time())

    result = await db.memorias.update_one({"_id": ObjectId(id)}, {"$set": memoria_dict})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Memória não encontrada")
    
    memoria_dict["_id"] = id
    return memoria_dict

@router.delete("/{id}")
async def excluir_memoria(id: str, db=Depends(get_database)):
    """
    Exclui uma memória pelo `_id`.
    """
    result = await db.memorias.delete_one({"_id": ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Memória não encontrada")
    
    return {"message": "Memória excluída com sucesso"}

@router.get("/categoria/{categoria_id}", response_model=List[Memoria])
async def listar_memorias_por_categoria(
    categoria_id: int,
    db=Depends(get_database),
    limit: int = Query(10),
    skip: int = Query(0)
):
    """
    Lista memórias de uma categoria específica.
    """
    cursor = db.memorias.find({"categoria_id": categoria_id}).skip(skip).limit(limit)
    memorias = await cursor.to_list(length=limit)

    for memoria in memorias:
        memoria["_id"] = str(memoria["_id"])

    return memorias

@router.get("/pessoa/{pessoa_id}", response_model=List[Memoria])
async def listar_memorias_por_pessoa(
    pessoa_id: str,
    emocao: Optional[str] = None,
    db=Depends(get_database),
    limit: int = Query(10),
    skip: int = Query(0)
):
    """
    Lista memórias de uma pessoa específica, com opção de filtrar por emoção.
    """
    filtro = {"pessoa_id": pessoa_id}
    if emocao:
        filtro["emocao"] = emocao

    cursor = db.memorias.find(filtro).skip(skip).limit(limit)
    memorias = await cursor.to_list(length=limit)

    for memoria in memorias:
        memoria["_id"] = str(memoria["_id"])

    return memorias

@router.get("/datas/")
async def listar_memorias_por_datas(
    data_inicio: date,
    data_fim: date,
    emocao: Optional[str] = None,
    db=Depends(get_database),
    limit: int = Query(10),
    skip: int = Query(0)
):
    """
    Lista memórias dentro de um intervalo de datas, com filtro opcional por emoção.
    """
    filtro = {"data": {"$gte": datetime.combine(data_inicio, datetime.min.time()), "$lte": datetime.combine(data_fim, datetime.min.time())}}
    if emocao:
        filtro["emocao"] = emocao

    cursor = db.memorias.find(filtro).sort("data", -1).skip(skip).limit(limit)
    memorias = await cursor.to_list(length=limit)

    for memoria in memorias:
        memoria["_id"] = str(memoria["_id"])

    return memorias

@router.get("/agregacoes/total-por-categoria/")
async def total_memorias_por_categoria(db=Depends(get_database)):
    """
    Retorna a quantidade total de memórias agrupadas por categoria.
    """
    pipeline = [
        {"$group": {"_id": "$categoria_id", "total_memorias": {"$sum": 1}}},
        {"$sort": {"total_memorias": -1}}
    ]
    resultado = await db.memorias.aggregate(pipeline).to_list(length=None)

    return [{"categoria_id": d["_id"], "total_memorias": d["total_memorias"]} for d in resultado]

@router.get("/busca/")
async def buscar_memorias_por_titulo(
    texto: str,
    db=Depends(get_database),
    limit: int = Query(10),
    skip: int = Query(0)
):
    """
    Busca memórias cujo título contenha o texto especificado.
    """
    filtro = {"titulo": {"$regex": texto, "$options": "i"}}

    cursor = db.memorias.find(filtro).skip(skip).limit(limit)
    memorias = await cursor.to_list(length=limit)

    for memoria in memorias:
        memoria["_id"] = str(memoria["_id"])

    return memorias
