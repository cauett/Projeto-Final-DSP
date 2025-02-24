from fastapi import APIRouter, HTTPException, Query
from typing import List, Union
from app.models.memoria import Memoria
from app.models.categoria import Categoria
from app.models.pessoa import Pessoa
from beanie import PydanticObjectId

router = APIRouter()


@router.post("/", response_model=Memoria)
async def criar_memoria(memoria: Memoria):
    """
    Cria uma nova memória no sistema.

    Verifica:
    - Existência da pessoa associada (se informada)
    - Existência da categoria associada (se informada)

    Raises:
        HTTPException 400: Se pessoa ou categoria não existirem
    """
    if memoria.pessoa and not await Pessoa.get(memoria.pessoa.id):
        raise HTTPException(status_code=400, detail="Pessoa não encontrada")

    if memoria.categoria and not await Categoria.get(memoria.categoria.id):
        raise HTTPException(status_code=400, detail="Categoria não encontrada")

    await memoria.insert()
    return memoria


@router.get("/", response_model=List[Memoria])
async def listar_memorias(
    limit: int = Query(10, description="Número máximo de memórias a retornar"),
    skip: int = Query(0, description="Número de registros a pular"),
):
    """
    Lista memórias com paginação.

    Features:
    - Paginação via limit/skip
    - Carrega títulos das memórias relacionadas à pessoa
    """
    query = Memoria.find()
    memorias = await query.skip(skip).limit(limit).to_list()

    for memoria in memorias:
        if memoria.pessoa:
            memorias_pessoa = await Memoria.find(
                Memoria.pessoa == memoria.pessoa
            ).to_list()
            memoria.pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return memorias


@router.get("/{id}", response_model=Memoria)
async def obter_memoria(id: str):
    """
    Obtém detalhes de uma memória específica pelo ID.

    Params:
        id (str): ObjectId da memória (24 caracteres hexadecimais)

    Raises:
        HTTPException 404: Se memória não for encontrada
    """
    memoria = await Memoria.get(PydanticObjectId(id))
    if not memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

    if memoria.pessoa:
        memorias_pessoa = await Memoria.find(Memoria.pessoa == memoria.pessoa).to_list()
        memoria.pessoa.memorias = [m.titulo for m in memorias_pessoa]

    return memoria


@router.put("/{id}", response_model=Memoria)
async def atualizar_memoria(id: str, memoria: Memoria):
    """
    Atualiza todos os campos de uma memória existente.

    Comportamento:
    - Substitui todos os campos pelos novos valores
    - Mantém o mesmo ID original
    """
    existing_memoria = await Memoria.get(PydanticObjectId(id))
    if not existing_memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

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
    Remove permanentemente uma memória do sistema.

    Raises:
        HTTPException 404: Se memória não existir
    """
    memoria = await Memoria.get(PydanticObjectId(id))
    if not memoria:
        raise HTTPException(status_code=404, detail="Memória não encontrada")

    await memoria.delete()
    return {"message": "Memória excluída com sucesso"}


@router.get("/categoria/{identificador}", response_model=List[Memoria])
async def listar_memorias_por_categoria(identificador: Union[int, str]):
    """
    Busca memórias por categoria usando ID ou nome.

    Params:
        identificador (int|str): categoria_id (número) ou nome (string)

    Features:
    - Busca case insensitive para nomes
    - Valida existência da categoria
    """
    if isinstance(identificador, int) or identificador.isdigit():
        categoria = await Categoria.find_one(
            Categoria.categoria_id == int(identificador)
        )
    else:
        categoria = await Categoria.find_one(
            {"nome": {"$regex": f"^{identificador}$", "$options": "i"}}
        )

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    memorias = await Memoria.find(Memoria.categoria == categoria).to_list()
    if not memorias:
        raise HTTPException(
            status_code=404, detail="Nenhuma memória encontrada para esta categoria"
        )

    return memorias


@router.get("/pessoa/{identificador}", response_model=List[Memoria])
async def listar_memorias_por_pessoa(identificador: Union[str, PydanticObjectId]):
    """
    Busca memórias associadas a uma pessoa usando ID ou nome.

    Params:
        identificador (str|ObjectId): ID da pessoa ou nome exato
    """
    if isinstance(identificador, PydanticObjectId) or len(identificador) == 24:
        pessoa = await Pessoa.get(PydanticObjectId(identificador))
    else:
        pessoa = await Pessoa.find_one(
            {"nome": {"$regex": f"^{identificador}$", "$options": "i"}}
        )

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    memorias = await Memoria.find(Memoria.pessoa == pessoa).to_list()
    if not memorias:
        raise HTTPException(
            status_code=404, detail="Nenhuma memória encontrada para esta pessoa"
        )

    return memorias


@router.get("/memorias/buscar", response_model=List[Memoria])
async def buscar_memorias(termo: str):
    """
    Busca textual em memórias usando índice full-text.

    Params:
        termo (str): Palavra ou frase para busca
    """
    if not termo:
        raise HTTPException(
            status_code=400, detail="O termo de busca não pode ser vazio."
        )

    memorias = await Memoria.find({"$text": {"$search": termo}}).to_list()
    if not memorias:
        raise HTTPException(
            status_code=404, detail="Nenhuma memória encontrada com o termo fornecido."
        )

    return memorias


@router.get("/estatisticas/quantidade")
async def contar_memorias():
    """
    Retorna estatísticas agregadas das memórias.

    Retorna:
        total_memorias (int): Contagem total
        quantidade_por_categoria (list): Agrupamento por categoria
    """
    total_memorias = await Memoria.find().count()
    contagem_por_categoria = await Memoria.aggregate(
        [{"$group": {"_id": "$categoria.nome", "quantidade": {"$sum": 1}}}]
    ).to_list()

    return {
        "total_memorias": total_memorias,
        "quantidade_por_categoria": contagem_por_categoria,
    }
