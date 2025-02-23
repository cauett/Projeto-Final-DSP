## 📌 Diagrama de Classes

O diagrama abaixo representa a estrutura das entidades e seus relacionamentos na API.

```mermaid
classDiagram
    class Categoria {
        +int categoria_id
        +string nome
    }

    class Pessoa {
        +string id
        +string nome
        +date data_nascimento
        +List~string~ memorias
    }

    class Memoria {
        +string id
        +string titulo
        +string descricao
        +date data
        +string emocao
        +Categoria categoria
        +Pessoa pessoa
    }

    class Grupo {
        +string id
        +string nome
        +List~PessoaRef~ pessoas
    }

    class PessoaRef {
        +string id
        +string nome
        +List~string~ memorias
    }

    %% RELACIONAMENTOS
    Categoria <-- Memoria : "1" contém "0..*" 
    Pessoa <-- Memoria : "1" contém "0..*"
    Grupo "1" --> "*" PessoaRef : contém
