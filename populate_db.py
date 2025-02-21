import asyncio
from datetime import date
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.categoria import Categoria
from app.models.pessoa import Pessoa
from app.models.memoria import Memoria
from app.config import MONGO_URL

DB_NAME = "banco-memorias"

async def init_db():
    """Inicializa o banco de dados com Beanie"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await init_beanie(database=db, document_models=[Categoria, Pessoa, Memoria])

async def popular_banco():
    """Popula o banco de dados com dados realistas"""

    print("Populando banco de dados com dados realistas...")

    # Criar categorias realistas
    categorias = [
        Categoria(categoria_id=1, nome="Viagens"),
        Categoria(categoria_id=2, nome="Família"),
        Categoria(categoria_id=3, nome="Trabalho"),
        Categoria(categoria_id=4, nome="Educação"),
        Categoria(categoria_id=5, nome="Esportes"),
        Categoria(categoria_id=6, nome="Amizades"),
        Categoria(categoria_id=7, nome="Eventos"),
        Categoria(categoria_id=8, nome="Hobbies"),
        Categoria(categoria_id=9, nome="Música"),
        Categoria(categoria_id=10, nome="Tecnologia"),
    ]
    await Categoria.insert_many(categorias)

    # Criar pessoas realistas
    pessoas = [
        Pessoa(nome="João Silva", data_nascimento=date(1990, 5, 14)),
        Pessoa(nome="Maria Oliveira", data_nascimento=date(1985, 8, 22)),
        Pessoa(nome="Carlos Souza", data_nascimento=date(2000, 3, 11)),
        Pessoa(nome="Ana Pereira", data_nascimento=date(1995, 12, 30)),
        Pessoa(nome="Lucas Almeida", data_nascimento=date(1998, 7, 19)),
        Pessoa(nome="Fernanda Costa", data_nascimento=date(1989, 11, 5)),
        Pessoa(nome="Roberto Lima", data_nascimento=date(1975, 6, 8)),
        Pessoa(nome="Camila Mendes", data_nascimento=date(1992, 9, 27)),
        Pessoa(nome="Bruno Martins", data_nascimento=date(1997, 2, 14)),
        Pessoa(nome="Juliana Castro", data_nascimento=date(1993, 4, 21)),
    ]
    await Pessoa.insert_many(pessoas)

    # Buscar categorias e pessoas criadas
    categorias_db = await Categoria.find().to_list()
    pessoas_db = await Pessoa.find().to_list()

    # Criar memórias realistas associadas a categorias e pessoas
    memorias = [
        Memoria(
            titulo="Viagem para Paris",
            descricao="Uma viagem inesquecível para Paris com minha família.",
            data=date(2018, 6, 10),
            emocao="Feliz",
            categoria=categorias_db[0],  # Viagens
            pessoa=pessoas_db[1],  # Maria Oliveira
        ),
        Memoria(
            titulo="Aniversário da minha mãe",
            descricao="Comemoração do aniversário da minha mãe com toda a família reunida.",
            data=date(2022, 10, 5),
            emocao="Feliz",
            categoria=categorias_db[1],  # Família
            pessoa=pessoas_db[5],  # Fernanda Costa
        ),
        Memoria(
            titulo="Primeiro emprego",
            descricao="Meu primeiro dia de trabalho como engenheiro de software.",
            data=date(2020, 2, 3),
            emocao="Empolgado",
            categoria=categorias_db[2],  # Trabalho
            pessoa=pessoas_db[2],  # Carlos Souza
        ),
        Memoria(
            titulo="Formatura na faculdade",
            descricao="O dia em que me formei na faculdade de Engenharia Civil.",
            data=date(2017, 12, 15),
            emocao="Orgulho",
            categoria=categorias_db[3],  # Educação
            pessoa=pessoas_db[0],  # João Silva
        ),
        Memoria(
            titulo="Maratona de São Paulo",
            descricao="Completei minha primeira maratona em São Paulo.",
            data=date(2021, 4, 25),
            emocao="Euforia",
            categoria=categorias_db[4],  # Esportes
            pessoa=pessoas_db[4],  # Lucas Almeida
        ),
        Memoria(
            titulo="Acampamento com amigos",
            descricao="Um final de semana incrível de acampamento com amigos.",
            data=date(2019, 9, 14),
            emocao="Aventura",
            categoria=categorias_db[5],  # Amizades
            pessoa=pessoas_db[3],  # Ana Pereira
        ),
        Memoria(
            titulo="Casamento do meu irmão",
            descricao="Dia emocionante no casamento do meu irmão mais velho.",
            data=date(2023, 5, 20),
            emocao="Emocionado",
            categoria=categorias_db[6],  # Eventos
            pessoa=pessoas_db[6],  # Roberto Lima
        ),
        Memoria(
            titulo="Primeiro violão",
            descricao="O dia em que comprei meu primeiro violão e comecei a aprender música.",
            data=date(2015, 11, 8),
            emocao="Nostálgico",
            categoria=categorias_db[8],  # Música
            pessoa=pessoas_db[7],  # Camila Mendes
        ),
        Memoria(
            titulo="Hackathon de programação",
            descricao="Participei do meu primeiro hackathon e aprendi muito.",
            data=date(2022, 3, 12),
            emocao="Animado",
            categoria=categorias_db[9],  # Tecnologia
            pessoa=pessoas_db[8],  # Bruno Martins
        ),
        Memoria(
            titulo="Primeiro jogo de xadrez",
            descricao="Joguei xadrez pela primeira vez e adorei a experiência.",
            data=date(2014, 7, 22),
            emocao="Curioso",
            categoria=categorias_db[7],  # Hobbies
            pessoa=pessoas_db[9],  # Juliana Castro
        ),
    ]
    await Memoria.insert_many(memorias)

    print("Banco de dados populado com sucesso!")

async def main():
    await init_db()
    await popular_banco()

if __name__ == "__main__":
    asyncio.run(main())
