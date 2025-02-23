classDiagram
    class Pessoa {
        +String id
        +String nome
        +Date data_nascimento
        +List~String~ memorias
    }

    class Categoria {
        +Int categoria_id
        +String nome
    }

    class Memoria {
        +String id
        +String titulo
        +String descricao
        +Date data
        +String emocao
        +List~Categoria~ categorias
        +List~Pessoa~ pessoas
    }

    class Grupo {
        +String id
        +String nome
        +List~PessoaRef~ pessoas
    }

    class PessoaRef {
        +String id
        +String nome
        +List~String~ memorias
    }

    Pessoa "1" -- "0..*" Memoria : possui
    Categoria "1" -- "0..*" Memoria : classifica
    Grupo "1" -- "0..*" PessoaRef : contém
    PessoaRef "1" -- "1" Pessoa : referencia
