# routers/grupo.py
from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from typing import List
from app.models.grupo import Grupo, PessoaRef
from app.models.pessoa import Pessoa
from app.models.memoria import Memoria

router = APIRouter(prefix="/grupos", tags=["Grupos"])

@router.post("/")
async def criar_grupo(nome: str):
    """
    Cria um novo grupo com o nome especificado.
    
    Args:
        nome (str): Nome do grupo a ser criado.
    
    Returns:
        dict: Mensagem de confirmação e ID do grupo criado.
    """
    grupo = Grupo(nome=nome)
    await grupo.create()
    return {"mensagem": f"Grupo '{nome}' criado!", "id": str(grupo.id)}

@router.get("/", response_model=List[Grupo])
async def listar_grupos():
    """
    Lista todos os grupos cadastrados, incluindo as pessoas e suas memórias associadas.
    
    Returns:
        List[Grupo]: Lista de grupos com informações atualizadas das pessoas e memórias.
    """
    grupos = await Grupo.find_all().to_list()

    for grupo in grupos:
        novas_pessoas = []
        for pessoa_ref in grupo.pessoas:
            pessoa = await Pessoa.get(PydanticObjectId(pessoa_ref.id))
            if pessoa:
                memorias_pessoa = await Memoria.find(Memoria.pessoa == pessoa).to_list()
                novas_pessoas.append(
                    PessoaRef(
                        id=str(pessoa.id),
                        nome=pessoa.nome,
                        memorias=[m.titulo for m in memorias_pessoa]
                    )
                )
            else:
                novas_pessoas.append(pessoa_ref)
        
        grupo.pessoas = novas_pessoas

    return grupos

@router.post("/{grupo_id}/pessoas/{pessoa_id}")
async def adicionar_pessoa(grupo_id: PydanticObjectId, pessoa_id: PydanticObjectId):
    """
    Adiciona uma pessoa a um grupo específico, incluindo suas memórias associadas.
    
    Args:
        grupo_id (PydanticObjectId): ID do grupo.
        pessoa_id (PydanticObjectId): ID da pessoa a ser adicionada.
    
    Returns:
        dict: Mensagem de confirmação.
    """
    grupo = await Grupo.get(grupo_id)
    pessoa = await Pessoa.get(pessoa_id)
    
    if not grupo or not pessoa:
        raise HTTPException(status_code=404, detail="Grupo ou pessoa não encontrado")
    
    if not any(p.id == str(pessoa.id) for p in grupo.pessoas):
        memorias_da_pessoa = await Memoria.find(Memoria.pessoa.id == pessoa.id).to_list()
        
        pessoa_ref = PessoaRef(
            id=str(pessoa.id),
            nome=pessoa.nome,
            memorias=[memoria.titulo for memoria in memorias_da_pessoa]
        )
        
        grupo.pessoas.append(pessoa_ref)
        await grupo.save()
    
    return {"mensagem": f"Pessoa '{pessoa.nome}' e suas memórias foram adicionadas ao grupo!"}

@router.delete("/{grupo_id}/pessoas/{pessoa_id}")
async def remover_pessoa(grupo_id: PydanticObjectId, pessoa_id: PydanticObjectId):
    """
    Remove uma pessoa de um grupo específico.
    
    Args:
        grupo_id (PydanticObjectId): ID do grupo.
        pessoa_id (PydanticObjectId): ID da pessoa a ser removida.
    
    Returns:
        dict: Mensagem de confirmação.
    """
    grupo = await Grupo.get(grupo_id)
    pessoa = await Pessoa.get(pessoa_id)
    
    if not grupo or not pessoa:
        raise HTTPException(status_code=404, detail="Grupo ou pessoa não encontrado")
    
    grupo.pessoas = [p for p in grupo.pessoas if p.id != str(pessoa.id)]
    await grupo.save()
    
    return {"mensagem": f"Pessoa '{pessoa.nome}' removida do grupo '{grupo.nome}'"}
