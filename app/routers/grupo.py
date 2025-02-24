from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId
from typing import List, Union
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


@router.get("/{grupo_identificador}", response_model=Grupo)
async def obter_grupo(grupo_identificador: Union[PydanticObjectId, str]):
    """
    Obtém um grupo pelo ID ou pelo nome.

    Args:
        grupo_identificador (Union[PydanticObjectId, str]): ID ou nome do grupo.

    Returns:
        Grupo: Informações detalhadas do grupo.
    """
    grupo = (
        await Grupo.get(grupo_identificador)
        if isinstance(grupo_identificador, PydanticObjectId)
        else await Grupo.find_one({"nome": grupo_identificador})
    )

    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    return grupo


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
                        memorias=[m.titulo for m in memorias_pessoa],
                    )
                )
            else:
                novas_pessoas.append(pessoa_ref)

        grupo.pessoas = novas_pessoas

    return grupos


@router.delete("/{grupo_identificador}")
async def deletar_grupo(grupo_identificador: Union[PydanticObjectId, str]):
    """
    Deleta um grupo específico pelo ID ou nome.

    Args:
        grupo_identificador (Union[PydanticObjectId, str]): ID ou nome do grupo.

    Returns:
        dict: Mensagem de sucesso.
    """
    grupo = (
        await Grupo.get(grupo_identificador)
        if isinstance(grupo_identificador, PydanticObjectId)
        else await Grupo.find_one({"nome": grupo_identificador})
    )

    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    await grupo.delete()
    return {"mensagem": f"Grupo '{grupo.nome}' deletado com sucesso!"}


@router.post("/{grupo_identificador}/pessoas/{pessoa_identificador}")
async def adicionar_pessoa(
    grupo_identificador: Union[PydanticObjectId, str],
    pessoa_identificador: Union[PydanticObjectId, str],
):
    """
    Adiciona uma pessoa a um grupo específico. Se a pessoa já estiver no grupo, não será adicionada novamente.

    Args:
        grupo_identificador (Union[PydanticObjectId, str]): ID ou nome do grupo.
        pessoa_identificador (Union[PydanticObjectId, str]): ID ou nome da pessoa.

    Raises:
        HTTPException: Se o grupo ou a pessoa não forem encontrados.

    Returns:
        dict: Mensagem de sucesso confirmando a adição.
    """
    grupo = (
        await Grupo.get(grupo_identificador)
        if isinstance(grupo_identificador, PydanticObjectId)
        else await Grupo.find_one({"nome": grupo_identificador})
    )
    pessoa = (
        await Pessoa.get(pessoa_identificador)
        if isinstance(pessoa_identificador, PydanticObjectId)
        else await Pessoa.find_one({"nome": pessoa_identificador})
    )

    if not grupo or not pessoa:
        raise HTTPException(status_code=404, detail="Grupo ou pessoa não encontrado")

    if not any(p.id == str(pessoa.id) for p in grupo.pessoas):
        memorias_da_pessoa = await Memoria.find(
            Memoria.pessoa.id == pessoa.id
        ).to_list()
        pessoa_ref = PessoaRef(
            id=str(pessoa.id),
            nome=pessoa.nome,
            memorias=[memoria.titulo for memoria in memorias_da_pessoa],
        )
        grupo.pessoas.append(pessoa_ref)
        await grupo.save()

    return {
        "mensagem": f"Pessoa '{pessoa.nome}' e suas memórias foram adicionadas ao grupo '{grupo.nome}'!"
    }


@router.delete("/{grupo_identificador}/pessoas/{pessoa_identificador}")
async def remover_pessoa(
    grupo_identificador: Union[PydanticObjectId, str],
    pessoa_identificador: Union[PydanticObjectId, str],
):
    """
    Remove uma pessoa de um grupo específico.

    Args:
        grupo_identificador (Union[PydanticObjectId, str]): ID ou nome do grupo.
        pessoa_identificador (Union[PydanticObjectId, str]): ID ou nome da pessoa.

    Raises:
        HTTPException: Se o grupo ou a pessoa não forem encontrados.

    Returns:
        dict: Mensagem de sucesso confirmando a remoção.
    """
    grupo = (
        await Grupo.get(grupo_identificador)
        if isinstance(grupo_identificador, PydanticObjectId)
        else await Grupo.find_one({"nome": grupo_identificador})
    )
    pessoa = (
        await Pessoa.get(pessoa_identificador)
        if isinstance(pessoa_identificador, PydanticObjectId)
        else await Pessoa.find_one({"nome": pessoa_identificador})
    )

    if not grupo or not pessoa:
        raise HTTPException(status_code=404, detail="Grupo ou pessoa não encontrado")

    grupo.pessoas = [p for p in grupo.pessoas if p.id != str(pessoa.id)]
    await grupo.save()

    return {"mensagem": f"Pessoa '{pessoa.nome}' removida do grupo '{grupo.nome}'"}


@router.get("/{grupo_identificador}/pessoas/memorias", response_model=List[dict])
async def listar_pessoas_e_memorias(grupo_identificador: Union[PydanticObjectId, str]):
    """
    Retorna todas as pessoas de um grupo e suas memórias associadas.

    Args:
        grupo_identificador (Union[PydanticObjectId, str]): ID ou nome do grupo.

    Returns:
        List[dict]: Lista de pessoas no grupo com suas respectivas memórias.
    """
    grupo = (
        await Grupo.get(grupo_identificador)
        if isinstance(grupo_identificador, PydanticObjectId)
        else await Grupo.find_one({"nome": grupo_identificador})
    )

    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")

    resultado = []
    for pessoa_ref in grupo.pessoas:
        pessoa = await Pessoa.get(PydanticObjectId(pessoa_ref.id))
        if pessoa:
            memorias = await Memoria.find(Memoria.pessoa == pessoa).to_list()
            resultado.append(
                {
                    "id": str(pessoa.id),
                    "nome": pessoa.nome,
                    "memorias": [
                        {"titulo": memoria.titulo, "descricao": memoria.descricao}
                        for memoria in memorias
                    ],
                }
            )

    # **Correção principal: garantir que sempre retorna uma lista**
    return resultado if resultado else []


@router.get("/pessoas/{pessoa_identificador}/grupos", response_model=List[dict])
async def listar_grupos_de_pessoa(pessoa_identificador: Union[PydanticObjectId, str]):
    """
    Retorna todos os grupos em que uma pessoa específica está presente,
    junto com as memórias associadas a essa pessoa dentro de cada grupo.

    Args:
        pessoa_identificador (Union[PydanticObjectId, str]): ID ou nome da pessoa.

    Returns:
        List[dict]: Lista de grupos onde a pessoa está, incluindo suas memórias associadas.
    """
    pessoa = (
        await Pessoa.get(pessoa_identificador)
        if isinstance(pessoa_identificador, PydanticObjectId)
        else await Pessoa.find_one({"nome": pessoa_identificador})
    )

    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    grupos = await Grupo.find({"pessoas.id": str(pessoa.id)}).to_list()

    if not grupos:
        raise HTTPException(status_code=404, detail="A pessoa não está em nenhum grupo")

    resultado = []
    for grupo in grupos:
        resultado.append({"id": str(grupo.id), "nome": grupo.nome})

    return resultado

    return resultado
