from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime
from app.models.pessoa import Pessoa
from app.models.memoria import Memoria
from beanie import PydanticObjectId
from pymongo import DESCENDING, ASCENDING

router = APIRouter()

@router.post("/", response_model=Pessoa)
async def criar_pessoa(pessoa: Pessoa):
    """
    Cria uma nova pessoa com um `nome` como identificador único.
    """
    if await Pessoa.find_one(Pessoa.nome == pessoa.nome):
        raise HTTPException(status_code=400, detail="Já existe uma pessoa com este nome")

    await pessoa.insert()
    return pessoa

@router.get("/", response_model=List[Pessoa])
async def listar_pessoas(
    limit: int = Query(10, description="Número máximo de pessoas a retornar"),
    skip: int = Query(0, description="Número de registros a pular"),
):
    """
    Lista todas as pessoas com paginação, incluindo os títulos das memórias associadas.
    """
    pessoas = await Pessoa.find().skip(skip).limit(limit).to_list()

    for pessoa in pessoas:
        memorias_pessoa = await Memoria.find(Memoria.pessoa == pessoa).to_list()
        pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return pessoas


@router.get("/{identificador}", response_model=Pessoa)
async def obter_pessoa(identificador: str):
    """
    Obtém os dados de uma pessoa pelo `_id` ou pelo `nome`, incluindo os títulos das memórias associadas.
    """
    pessoa = None
    try:
        pessoa = await Pessoa.get(PydanticObjectId(identificador))  # Busca por ID
    except:
        pessoa = await Pessoa.find_one(Pessoa.nome == identificador)  # Busca por nome

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    # Adicionar títulos das memórias associadas
    memorias_pessoa = await Memoria.find(Memoria.pessoa == pessoa).to_list()
    pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return pessoa

@router.put("/{identificador}", response_model=Pessoa)
async def atualizar_pessoa(identificador: str, pessoa: Pessoa):
    """
    Atualiza os dados de uma pessoa existente pelo `_id` ou `nome`.
    """
    existing_pessoa = None

    try:
        existing_pessoa = await Pessoa.get(PydanticObjectId(identificador))
    except:
        existing_pessoa = await Pessoa.find_one(Pessoa.nome == identificador)

    if not existing_pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    existing_pessoa.nome = pessoa.nome
    existing_pessoa.data_nascimento = pessoa.data_nascimento
    await existing_pessoa.save()

    return existing_pessoa

@router.delete("/{identificador}")
async def excluir_pessoa(identificador: str):
    """
    Exclui uma pessoa pelo `_id` ou pelo `nome`.
    """
    pessoa = None

    try:
        pessoa = await Pessoa.get(PydanticObjectId(identificador))
    except:
        pessoa = await Pessoa.find_one(Pessoa.nome == identificador)

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    memorias_associadas = await Memoria.find_one({"pessoa": pessoa.id})
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

    memorias = await Memoria.find({"pessoa": pessoa.id}).to_list()

    if not memorias:
        raise HTTPException(status_code=404, detail="Nenhuma memória encontrada para esta pessoa")

    return memorias

# 🔹 FILTRO POR DATA DE NASCIMENTO OTIMIZADO
@router.get("/filtrar/data_nascimento", response_model=List[Pessoa])
async def filtrar_pessoas_por_data_nascimento(
    ano: Optional[int] = Query(None, description="Ano de nascimento da pessoa"),
    data_inicio: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)")
):
    """
    Filtra pessoas pelo ano de nascimento ou por um intervalo de datas.
    """
    filtro = {}

    if ano:
        filtro["data_nascimento"] = {"$gte": date(ano, 1, 1), "$lte": date(ano, 12, 31)}

    if data_inicio and data_fim:
        try:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()
            filtro["data_nascimento"] = {"$gte": data_inicio, "$lte": data_fim}
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

    pessoas = await Pessoa.find(filtro).to_list()

    if not pessoas:
        raise HTTPException(status_code=404, detail="Nenhuma pessoa encontrada com esse critério")

    return pessoas

# 🔹 ORDENAÇÃO POR DATA DE NASCIMENTO OTIMIZADA
@router.get("/ordenar/data_nascimento", response_model=List[Pessoa])
async def ordenar_pessoas_por_data_nascimento(
    ordem: str = Query("desc", description="Ordenação por data de nascimento: 'asc' para mais velhos, 'desc' para mais novos")
):
    """
    Ordena as pessoas pela data de nascimento (mais novas primeiro ou mais velhas primeiro).
    """
    ordem_mongo = DESCENDING if ordem == "desc" else ASCENDING

    pessoas = await Pessoa.find().sort([("data_nascimento", ordem_mongo)]).to_list()

    if not pessoas:
        raise HTTPException(status_code=404, detail="Nenhuma pessoa encontrada")

    for pessoa in pessoas:
        memorias_pessoa = await Memoria.find({"pessoa": pessoa.id}).to_list()
        pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return pessoas
