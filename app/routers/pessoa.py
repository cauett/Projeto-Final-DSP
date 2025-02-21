from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.pessoa import Pessoa
from app.models.memoria import Memoria
from beanie import PydanticObjectId

router = APIRouter()

@router.post("/", response_model=Pessoa)
async def criar_pessoa(pessoa: Pessoa):
    """
    Cria uma nova pessoa com um `nome` como identificador único.
    """
    # Verifica se já existe uma pessoa com o mesmo nome
    if await Pessoa.find_one(Pessoa.nome == pessoa.nome):
        raise HTTPException(status_code=400, detail="Já existe uma pessoa com este nome")

    # Salvar no MongoDB usando Beanie
    await pessoa.insert()
    return pessoa


@router.get("/", response_model=List[Pessoa])
async def listar_pessoas(
    limit: int = Query(10, description="Número máximo de pessoas a retornar"),
    skip: int = Query(0, description="Número de registros a pular")
):
    """
    Lista todas as pessoas cadastradas com paginação, incluindo os nomes das memórias associadas.
    """
    pessoas = await Pessoa.find().skip(skip).limit(limit).to_list()

    for pessoa in pessoas:
        # Buscar nomes das memórias associadas
        memorias = await Memoria.find(Memoria.pessoa == pessoa).to_list()
        pessoa.memorias = [memoria.titulo for memoria in memorias]  # Lista de nomes das memórias

    return pessoas

@router.get("/{identificador}", response_model=Pessoa)
async def obter_pessoa(identificador: str):
    """
    Obtém os dados de uma pessoa pelo `_id` (ObjectId) ou pelo `nome`, incluindo os nomes das memórias associadas.
    """
    # Tentar buscar pelo ID
    if PydanticObjectId.is_valid(identificador):
        pessoa = await Pessoa.get(PydanticObjectId(identificador))
    else:
        # Buscar pelo nome (case insensitive)
        pessoa = await Pessoa.find_one(Pessoa.nome.lower() == identificador.lower())

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    # Buscar nomes das memórias associadas a essa pessoa
    memorias = await Memoria.find(Memoria.pessoa == pessoa).to_list()
    pessoa.memorias = [memoria.titulo for memoria in memorias]  # Lista de nomes das memórias

    return pessoa

@router.put("/{identificador}", response_model=Pessoa)
async def atualizar_pessoa(identificador: str, pessoa: Pessoa):
    """
    Atualiza os dados de uma pessoa existente pelo `_id` ou `nome`.
    """
    existing_pessoa = None
    try:
        existing_pessoa = await Pessoa.get(PydanticObjectId(identificador))  # Busca por ID
    except:
        existing_pessoa = await Pessoa.find_one(Pessoa.nome == identificador)  # Busca por nome

    if not existing_pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    # Atualizar os campos
    existing_pessoa.nome = pessoa.nome
    existing_pessoa.data_nascimento = pessoa.data_nascimento

    await existing_pessoa.save()
    return existing_pessoa

@router.delete("/{identificador}")
async def excluir_pessoa(identificador: str):
    """
    Exclui uma pessoa pelo `_id` (ObjectId) ou pelo `nome`.
    """
    pessoa = None
    try:
        pessoa = await Pessoa.get(PydanticObjectId(identificador))  # Busca por ID
    except:
        pessoa = await Pessoa.find_one(Pessoa.nome == identificador)  # Busca por nome

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    # Verificar se há memórias associadas a essa pessoa
    memorias_associadas = await Memoria.find_one(Memoria.pessoa == pessoa)
    if memorias_associadas:
        raise HTTPException(status_code=400, detail="Não é possível excluir. Essa pessoa possui memórias associadas.")

    await pessoa.delete()
    return {"message": "Pessoa excluída com sucesso"}

@router.get("/{pessoa_id}/memorias", response_model=List[Memoria])
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
