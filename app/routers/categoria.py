from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.categoria import Categoria, CategoriaResponse
from app.models.memoria import Memoria

router = APIRouter()

@router.post("/", response_model=CategoriaResponse)
async def criar_categoria(categoria: Categoria):
    """
    Cria uma nova categoria com um `categoria_id` definido pelo usuário.
    """
    # Verificação de ID único
    if await Categoria.find_one(Categoria.categoria_id == categoria.categoria_id):
        raise HTTPException(status_code=400, detail="Já existe uma categoria com este ID")

    # Verificação de nome único
    if await Categoria.find_one(Categoria.nome == categoria.nome):
        raise HTTPException(status_code=400, detail="Já existe uma categoria com este nome")

    # Validação do Nome
    if len(categoria.nome) < 3:
        raise HTTPException(status_code=422, detail="O nome da categoria deve ter pelo menos 3 caracteres")

    # Salvar no MongoDB usando Beanie
    await categoria.insert()
    return CategoriaResponse(categoria_id=categoria.categoria_id, nome=categoria.nome)

@router.get("/", response_model=List[CategoriaResponse])
async def listar_categorias(
    limit: int = Query(10, description="Número máximo de categorias a retornar"),
    skip: int = Query(0, description="Número de registros a pular")
):
    """
    Lista todas as categorias cadastradas.
    """
    categorias = await Categoria.find().skip(skip).limit(limit).to_list()

    # Se não encontrar nenhuma categoria, retorna erro
    if not categorias:
        raise HTTPException(status_code=404, detail="Nenhuma categoria encontrada")

    return [CategoriaResponse(categoria_id=c.categoria_id, nome=c.nome) for c in categorias]

@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def obter_categoria(categoria_id: int):
    """
    Obtém os dados de uma categoria específica pelo `categoria_id`.
    """
    categoria = await Categoria.find_one(Categoria.categoria_id == categoria_id)

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return CategoriaResponse(categoria_id=categoria.categoria_id, nome=categoria.nome)

@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def atualizar_categoria(categoria_id: int, categoria: Categoria):
    """
    Atualiza os dados de uma categoria existente pelo `categoria_id`.
    """
    # Validação do Nome
    if categoria.nome and len(categoria.nome) < 3:
        raise HTTPException(status_code=422, detail="O nome da categoria deve ter pelo menos 3 caracteres")

    # Buscar a categoria existente
    existing_categoria = await Categoria.find_one(Categoria.categoria_id == categoria_id)

    if not existing_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # Atualizar os campos
    existing_categoria.nome = categoria.nome
    await existing_categoria.save()

    return CategoriaResponse(categoria_id=existing_categoria.categoria_id, nome=existing_categoria.nome)

@router.delete("/{categoria_id}")
async def excluir_categoria(categoria_id: int):
    """
    Exclui uma categoria pelo `categoria_id`.
    """
    categoria = await Categoria.find_one(Categoria.categoria_id == categoria_id)

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # Verificar se há memórias associadas à categoria
    memorias_associadas = await Memoria.find_one(Memoria.categoria == categoria)
    if memorias_associadas:
        raise HTTPException(status_code=400, detail="Não é possível excluir. Esta categoria possui memórias associadas.")

    await categoria.delete()
    return {"message": "Categoria excluída com sucesso"}

@router.get("/{categoria_id}/memorias", response_model=List[Memoria])
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
