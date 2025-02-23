## 📌 Diagrama de Classes

O diagrama abaixo representa a estrutura das entidades e seus relacionamentos na API.

```mermaid
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

    Pessoa "1" -- "0..*" Memoria : possui
    Categoria "1" -- "0..*" Memoria : classifica
