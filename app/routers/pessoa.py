from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from typing import List, Optional
from datetime import date, datetime
from app.models.pessoa import Pessoa
from app.database import get_database

router = APIRouter()

@router.post("/", response_model=Pessoa)
async def criar_pessoa(pessoa: Pessoa, db=Depends(get_database)):
    """
    Cria uma nova pessoa com um `nome` como identificador único.
    """
    pessoa_dict = pessoa.model_dump()

    # Verifica se já existe uma pessoa com o mesmo nome
    if await db.pessoas.find_one({"nome": pessoa_dict["nome"]}):
        raise HTTPException(status_code=400, detail="Já existe uma pessoa com este nome")

    # Converte `data_nascimento` para `datetime`
    pessoa_dict["data_nascimento"] = datetime.combine(pessoa_dict["data_nascimento"], datetime.min.time())

    # Insere no MongoDB
    result = await db.pessoas.insert_one(pessoa_dict)

    # Retorna com `_id` convertido para string
    pessoa_dict["_id"] = str(result.inserted_id)
    return pessoa_dict

@router.get("/", response_model=List[Pessoa])
async def listar_pessoas(
    db=Depends(get_database),
    limit: int = Query(10, description="Número máximo de pessoas a retornar"),
    skip: int = Query(0, description="Número de registros a pular")
):
    """
    Lista todas as pessoas cadastradas com paginação.
    Retorna `_id` e as memórias associadas a cada pessoa.
    """
    pessoas_cursor = db.pessoas.find().skip(skip).limit(limit)
    pessoas = await pessoas_cursor.to_list(length=limit)

    for pessoa in pessoas:
        pessoa["_id"] = str(pessoa["_id"])  # Converter ObjectId para string
        if "data_nascimento" in pessoa and isinstance(pessoa["data_nascimento"], datetime):
            pessoa["data_nascimento"] = pessoa["data_nascimento"].date()

        # Buscar memórias associadas a essa pessoa
        memorias_cursor = db.memorias.find({"pessoa_id": str(pessoa["_id"])})
        pessoa["memorias"] = [str(memoria["_id"]) async for memoria in memorias_cursor]

    return pessoas

@router.get("/{identificador}", response_model=Pessoa)
async def obter_pessoa(identificador: str, db=Depends(get_database)):
    """
    Obtém os dados de uma pessoa pelo `_id` (ObjectId) ou pelo `nome` definido pelo usuário.
    Também retorna as memórias associadas a essa pessoa.
    """
    pessoa = None
    if ObjectId.is_valid(identificador):  # Se for um ObjectId válido, busca por _id
        pessoa = await db.pessoas.find_one({"_id": ObjectId(identificador)})
    else:  # Caso contrário, busca pelo nome
        pessoa = await db.pessoas.find_one({"nome": identificador})

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    pessoa["_id"] = str(pessoa["_id"])  # Converter ObjectId para string

    # Converter `data_nascimento` para `date`
    if "data_nascimento" in pessoa and isinstance(pessoa["data_nascimento"], datetime):
        pessoa["data_nascimento"] = pessoa["data_nascimento"].date()

    # Buscar memórias associadas a essa pessoa
    memorias_cursor = db.memorias.find({"pessoa_id": pessoa["_id"]})
    pessoa["memorias"] = [str(memoria["_id"]) async for memoria in memorias_cursor]

    return pessoa

@router.put("/{identificador}", response_model=Pessoa)
async def atualizar_pessoa(identificador: str, pessoa: Pessoa, db=Depends(get_database)):
    """
    Atualiza os dados de uma pessoa existente pelo `_id` ou `nome`.
    """
    pessoa_dict = pessoa.model_dump(exclude_unset=True)

    # Converter `data_nascimento` para `datetime` antes de salvar no MongoDB
    if "data_nascimento" in pessoa_dict and isinstance(pessoa_dict["data_nascimento"], date):
        pessoa_dict["data_nascimento"] = datetime.combine(pessoa_dict["data_nascimento"], datetime.min.time())

    filtro = {}
    if ObjectId.is_valid(identificador):
        filtro["_id"] = ObjectId(identificador)
    else:
        filtro["nome"] = identificador

    result = await db.pessoas.update_one(filtro, {"$set": pessoa_dict})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    pessoa_dict["_id"] = identificador
    return pessoa_dict

@router.delete("/{identificador}")
async def excluir_pessoa(identificador: str, db=Depends(get_database)):
    """
    Exclui uma pessoa pelo `_id` (ObjectId) ou pelo `nome`.
    Verifica se há memórias associadas antes da exclusão.
    """
    filtro = {}
    if ObjectId.is_valid(identificador):
        filtro["_id"] = ObjectId(identificador)
    else:
        filtro["nome"] = identificador

    # Verificar se há memórias associadas a essa pessoa antes da exclusão
    pessoa = await db.pessoas.find_one(filtro)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    memorias_associadas = await db.memorias.find_one({"pessoa_id": str(pessoa["_id"])})
    if memorias_associadas:
        raise HTTPException(status_code=400, detail="Não é possível excluir. Essa pessoa possui memórias associadas.")

    result = await db.pessoas.delete_one(filtro)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    
    return {"message": "Pessoa excluída com sucesso"}
