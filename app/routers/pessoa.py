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
    Cria nova pessoa com nome único.
    
    Validações:
    - Nome deve ser único no sistema
    - Data de nascimento obrigatória e válida
    """
    if await Pessoa.find_one(Pessoa.nome == pessoa.nome):
        raise HTTPException(status_code=400, detail="Já existe uma pessoa com este nome")

    # Valida formato da data de nascimento
    if isinstance(pessoa.data_nascimento, str):
        try:
            pessoa.data_nascimento = datetime.strptime(pessoa.data_nascimento, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato inválido para data de nascimento. Use YYYY-MM-DD.")

    await pessoa.insert()
    return pessoa

@router.get("/", response_model=List[Pessoa])
async def listar_pessoas(
    limit: int = Query(10, description="Número máximo de pessoas a retornar"),
    skip: int = Query(0, description="Número de registros a pular"),
):
    """
    Lista pessoas com paginação básica.
    
    Adicional:
    - Inclui títulos das memórias relacionadas
    """
    pessoas = await Pessoa.find().skip(skip).limit(limit).to_list()

    for pessoa in pessoas:
        memorias_pessoa = await Memoria.find(Memoria.pessoa == pessoa).to_list()
        pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return pessoas

@router.get("/{identificador}", response_model=Pessoa)
async def obter_pessoa(identificador: str):
    """
    Obtém pessoa por ID ou nome exato.
    
    Features:
    - Busca flexível por diferentes identificadores
    - Carrega memórias associadas automaticamente
    """
    pessoa = None
    try:
        pessoa = await Pessoa.get(PydanticObjectId(identificador))
    except:
        pessoa = await Pessoa.find_one(Pessoa.nome == identificador)

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    memorias_pessoa = await Memoria.find(Memoria.pessoa == pessoa).to_list()
    pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return pessoa

@router.put("/{identificador}", response_model=Pessoa)
async def atualizar_pessoa(identificador: str, pessoa: Pessoa):
    """
    Atualiza dados básicos de uma pessoa.
    
    Permite:
    - Alteração de nome (mantendo unicidade)
    - Atualização de data de nascimento
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
    Exclui uma pessoa e suas memórias associadas.
    
    Validações:
    - Exclui todas as memórias vinculadas automaticamente
    - Permite exclusão por ID ou nome
    """
    pessoa = None

    try:
        pessoa = await Pessoa.get(PydanticObjectId(identificador))
    except:
        pessoa = await Pessoa.find_one(Pessoa.nome == identificador)

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    # Exclui todas as memórias associadas
    await Memoria.find(Memoria.pessoa == pessoa).delete()

    await pessoa.delete()
    return {"message": "Pessoa e suas memórias associadas foram excluídas com sucesso"}

@router.get("/filtrar/data_nascimento", response_model=List[Pessoa])
async def filtrar_pessoas_por_data_nascimento(
    ano: Optional[int] = Query(None, description="Ano de nascimento da pessoa"),
    data_inicio: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)")
):
    """
    Filtra pessoas por intervalo de datas de nascimento.
    
    Params:
        ano: Filtro por ano específico
        data_inicio/data_fim: Range temporal
    
    Valida:
    - Formato correto das datas (YYYY-MM-DD)
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

@router.get("/ordenar/data_nascimento", response_model=List[Pessoa])
async def ordenar_pessoas_por_data_nascimento(
    ordem: str = Query("desc", description="Ordenação por data de nascimento: 'asc' para mais velhos, 'desc' para mais novos")
):
    """
    Ordena pessoas por data de nascimento.
    
    Opções:
    - asc: Mais antigas primeiro
    - desc: Mais novas primeiro (padrão)
    """
    ordem_mongo = DESCENDING if ordem == "desc" else ASCENDING

    pessoas = await Pessoa.find().sort([("data_nascimento", ordem_mongo)]).to_list()
    if not pessoas:
        raise HTTPException(status_code=404, detail="Nenhuma pessoa encontrada")

    for pessoa in pessoas:
        memorias_pessoa = await Memoria.find(Memoria.pessoa == pessoa).to_list()
        pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return pessoas