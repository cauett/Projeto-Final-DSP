## 📌 Diagrama de Classes

O diagrama abaixo representa a estrutura das entidades e seus relacionamentos na API.

```mermaid
classDiagram
    class Categoria {
        +int categoria_id
        +str nome
    }

    class Memoria {
        +str titulo
        +str descricao
        +date data
        +str emocao
        +Optional[Categoria] categoria
        +Optional[Pessoa] pessoa
    }

    class Pessoa {
        +str nome
        +date data_nascimento
        +Optional[List[str]] memorias
    }

    class Grupo {
        +str nome
        +List[PessoaRef] pessoas
    }

    class PessoaRef {
        +str id
        +str nome
        +List[str] memorias
    }

    Categoria "1" --o "0..*" Memoria : classifica
    Pessoa "1" --o "0..*" Memoria : possui
    Grupo "1" *-- "0..*" PessoaRef : contém
    PessoaRef ..> Pessoa : referencia
