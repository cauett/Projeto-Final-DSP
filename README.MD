## 📌 Diagrama de Classes

O diagrama abaixo representa a estrutura das entidades e seus relacionamentos na API.

```mermaid
classDiagram
    class Categoria {
        +int categoria_id
        +String nome
    }

    class Memoria {
        +String titulo
        +String descricao
        +date data
        +String emocao
    }

    class Pessoa {
        +String nome
        +date data_nascimento
        +List~String~ memorias
    }

    class Grupo {
        +String nome
        +List~PessoaRef~ pessoas
    }

    class PessoaRef {
        +String id
        +String nome
        +List~String~ memorias
    }

    Memoria --> Categoria : pertence a
    Memoria --> Pessoa : associada a
    Grupo "1" --> "*" PessoaRef : contém
    PessoaRef --> "*" Memoria : referência a
