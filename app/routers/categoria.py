from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Union
from app.models.categoria import Categoria
from app.models.memoria import Memoria

router = APIRouter()

@router.post("/", response_model=Categoria)
async def criar_categoria(categoria: Categoria):
    """
    Cria uma nova categoria com um `categoria_id` definido pelo usuário.
    """
    if await Categoria.find_one(Categoria.categoria_id == categoria.categoria_id):
        raise HTTPException(status_code=400, detail="Já existe uma categoria com este ID")

    if await Categoria.find_one({"nome": {"$regex": f"^{categoria.nome}$", "$options": "i"}}):
        raise HTTPException(status_code=400, detail="Já existe uma categoria com este nome")

    if len(categoria.nome) < 3:
        raise HTTPException(status_code=422, detail="O nome da categoria deve ter pelo menos 3 caracteres")

    await categoria.insert()
    return categoria

@router.get("/", response_model=List[Categoria])
async def listar_categorias(
    limit: int = Query(10, description="Número máximo de categorias a retornar"),
    skip: int = Query(0, description="Número de registros a pular"),
):
    """
    Lista todas as categorias cadastradas com paginação e ordenação.
    """
    query = Categoria.find()
    categorias = await query.skip(skip).limit(limit).to_list()

    if not categorias:
        raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")

    return categorias

@router.get("/{identificador}", response_model=Categoria)
async def obter_categoria(identificador: Union[int, str]):
    """
    Obtém os dados de uma categoria específica pelo `categoria_id` (inteiro) ou `nome` (string), de forma case insensitive.
    """
    if isinstance(identificador, int) or identificador.isdigit():
        categoria = await Categoria.find_one(Categoria.categoria_id == int(identificador))
    else:
        categoria = await Categoria.find_one({"nome": {"$regex": f"^{identificador}$", "$options": "i"}})

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return categoria

@router.put("/{categoria_id}", response_model=Categoria)
async def atualizar_categoria(categoria_id: int, categoria: Categoria):
    """
    Atualiza os dados de uma categoria existente pelo `categoria_id`.
    """
    if categoria.nome and len(categoria.nome) < 3:
        raise HTTPException(status_code=422, detail="O nome da categoria deve ter pelo menos 3 caracteres")

    existing_categoria = await Categoria.find_one(Categoria.categoria_id == categoria_id)

    if not existing_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    existing_categoria.nome = categoria.nome
    await existing_categoria.save()

    return existing_categoria

@router.delete("/{categoria_id}")
async def excluir_categoria(categoria_id: int):
    """
    Exclui uma categoria pelo `categoria_id`.
    """
    categoria = await Categoria.find_one(Categoria.categoria_id == categoria_id)

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    memorias_associadas = await Memoria.find_one(Memoria.categoria == categoria)
    if memorias_associadas:
        raise HTTPException(status_code=400, detail="Não é possível excluir. Esta categoria possui memórias associadas.")

    await categoria.delete()
    return {"message": "Categoria excluída com sucesso"}
