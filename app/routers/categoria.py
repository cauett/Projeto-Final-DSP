from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from typing import List, Optional
from app.models.categoria import Categoria
from app.database import get_database

router = APIRouter()

@router.post("/", response_model=Categoria)
async def criar_categoria(categoria: Categoria, db=Depends(get_database)):
    """
    Cria uma nova categoria com um `id` numérico definido pelo usuário e um `_id` automático.

    - Se o `id` já existir, retorna erro 400.
    - Se o nome tiver menos de 3 caracteres, retorna erro 422.
    """
    categoria_dict = categoria.model_dump()

    # Verificação de ID único
    if await db.categorias.find_one({"id": categoria_dict["id"]}):
        raise HTTPException(status_code=400, detail="Já existe uma categoria com este ID")

    # Validação do Nome
    if len(categoria_dict["nome"]) < 3:
        raise HTTPException(status_code=422, detail="O nome da categoria deve ter pelo menos 3 caracteres")

    # Inserir no MongoDB
    result = await db.categorias.insert_one(categoria_dict)

    # Retornar a categoria com `_id` convertido para string
    categoria_dict["_id"] = str(result.inserted_id)
    return categoria_dict

@router.get("/", response_model=List[Categoria])
async def listar_categorias(
    db=Depends(get_database),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de categorias a retornar (1-100)"),
    skip: int = Query(0, ge=0, description="Número de registros a pular")
):
    """
    Lista todas as categorias com paginação.

    - `limit`: Número máximo de categorias retornadas (padrão: 10, máximo: 100).
    - `skip`: Número de registros a ignorar na busca (padrão: 0).
    - Inclui a contagem de memórias associadas a cada categoria.
    """
    categorias_cursor = db.categorias.find().skip(skip).limit(limit)
    categorias = await categorias_cursor.to_list(length=limit)
    
    for categoria in categorias:
        categoria["_id"] = str(categoria["_id"])  # Converter ObjectId para string

        # Contar memórias associadas a esta categoria
        memoria_count = await db.memorias.count_documents({"categoria_id": categoria["id"]})
        categoria["quantidade_memorias"] = memoria_count

    return categorias

@router.get("/{identificador}", response_model=Categoria)
async def obter_categoria(identificador: str, db=Depends(get_database)):
    """
    Obtém os dados de uma categoria específica pelo `_id` (ObjectId) ou `id` numérico.

    - Se o identificador for um ObjectId válido, busca pelo `_id`.
    - Se for um número, busca pelo `id` numérico.
    - Também exibe as memórias associadas à categoria.
    """
    categoria = None
    if ObjectId.is_valid(identificador):
        categoria = await db.categorias.find_one({"_id": ObjectId(identificador)})
    elif identificador.isdigit():
        categoria = await db.categorias.find_one({"id": int(identificador)})

    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    categoria["_id"] = str(categoria["_id"])  # Converter ObjectId para string

    # Buscar memórias associadas à categoria
    memorias_cursor = db.memorias.find({"categoria_id": categoria["id"]})
    categoria["memorias"] = [str(memoria["_id"]) async for memoria in memorias_cursor]

    return categoria

@router.put("/{identificador}", response_model=Categoria)
async def atualizar_categoria(identificador: str, categoria: Categoria, db=Depends(get_database)):
    """
    Atualiza os dados de uma categoria existente.

    - Se o identificador for um ObjectId válido, busca pelo `_id`.
    - Se for um número, busca pelo `id` numérico.
    - Se a categoria não existir, retorna erro 404.
    """
    categoria_dict = categoria.model_dump(exclude_unset=True)

    # Validação do Nome
    if "nome" in categoria_dict and len(categoria_dict["nome"]) < 3:
        raise HTTPException(status_code=422, detail="O nome da categoria deve ter pelo menos 3 caracteres")

    filtro = {}
    if ObjectId.is_valid(identificador):
        filtro["_id"] = ObjectId(identificador)
    elif identificador.isdigit():
        filtro["id"] = int(identificador)
    else:
        raise HTTPException(status_code=400, detail="Identificador inválido")

    result = await db.categorias.update_one(filtro, {"$set": categoria_dict})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    categoria_dict["_id"] = identificador
    return categoria_dict

@router.delete("/{identificador}")
async def excluir_categoria(identificador: str, db=Depends(get_database)):
    """
    Exclui uma categoria pelo `_id` (ObjectId) ou `id` numérico.

    - Se a categoria não existir, retorna erro 404.
    - Se houver memórias associadas a essa categoria, retorna erro 400.
    """
    filtro = {}
    if ObjectId.is_valid(identificador):
        filtro["_id"] = ObjectId(identificador)
    elif identificador.isdigit():
        filtro["id"] = int(identificador)
    else:
        raise HTTPException(status_code=400, detail="Identificador inválido")

    # Verificar se há memórias associadas à categoria
    categoria = await db.categorias.find_one(filtro)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    memorias_associadas = await db.memorias.find_one({"categoria_id": categoria["id"]})
    if memorias_associadas:
        raise HTTPException(status_code=400, detail="Não é possível excluir. Esta categoria possui memórias associadas.")

    result = await db.categorias.delete_one(filtro)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    return {"message": "Categoria excluída com sucesso"}
