# Diagramas de classes — estrutura implementada

Os diagramas usam a sintaxe **Mermaid** e aparecem automaticamente no GitHub. Mermaid é uma boa escolha para este projeto porque o diagrama fica versionado como texto junto ao código, pode ser revisado por diff e é renderizado pelo GitHub. A documentação oficial suporta classes, interfaces, herança, dependências e cardinalidades.

Para visualizar ou editar fora do GitHub, use o [Mermaid Live Editor](https://mermaid.live/). Não é necessário instalar uma biblioteca no projeto: os blocos Mermaid já são suficientes para a documentação.

## Servidor

```mermaid
classDiagram
  class Aluno {
    +int id
    +str nome
    +str matricula
  }
  class Atividade {
    +int id
    +str titulo
    +str descricao
    +float valor_maximo
  }
  class Nota {
    +int id
    +int aluno_id
    +int atividade_id
    +float valor
  }
  class FabricaRegistros {
    <<abstract>>
    +criar_aluno(registro)
    +criar_atividade(registro)
    +criar_nota(registro)
    +criar(tipo, registro)
  }
  class FabricaRegistrosPadrao
  class EstrategiaMedia {
    <<abstract>>
    +calcular(notas)
  }
  class MediaNormalizada
  class MediaPonderadaPorValorMaximo
  class MediaAritmeticaDireta
  class RepositorioJSON {
    +Path caminho
    +listar()
    +buscar(codigo)
    +adicionar(dados)
    +atualizar(codigo, dados)
    +excluir(codigo)
    +excluir_se(predicado)
  }
  class GerenciadorService {
    <<Facade>>
    +RepositorioJSON alunos
    +RepositorioJSON atividades
    +RepositorioJSON notas
    +FabricaRegistros fabrica
    +EstrategiaMedia estrategia_media
    +definir_estrategia_media(estrategia)
    +criar_aluno(dados)
    +criar_atividade(dados)
    +criar_nota(dados)
    +notas_do_aluno(id)
    +media_do_aluno(id, estrategia)
  }
  GerenciadorService --> RepositorioJSON : usa 3 repositórios
  GerenciadorService --> FabricaRegistros : usa Factory Method
  FabricaRegistros <|-- FabricaRegistrosPadrao
  FabricaRegistrosPadrao ..> Aluno : cria
  FabricaRegistrosPadrao ..> Atividade : cria
  FabricaRegistrosPadrao ..> Nota : cria
  GerenciadorService --> EstrategiaMedia : atua como Contexto do Strategy
  EstrategiaMedia <|-- MediaNormalizada
  EstrategiaMedia <|-- MediaPonderadaPorValorMaximo
  EstrategiaMedia <|-- MediaAritmeticaDireta
```

`create_app()` em `app.py` é uma **função-fábrica Flask**, não uma classe. As rotas chamam `GerenciadorService`; este utiliza `RepositorioJSON` para persistência.

O projeto 8 também demonstra o Factory Method para criar os modelos de domínio e o Strategy para permitir critérios diferentes de cálculo de média.

## Cliente

```mermaid
classDiagram
  class JanelaPrincipal {
    +QMainWindow
    +preencher_tabela(tabela, linhas)
    +preencher_combo(combo, opcoes, chave)
  }
  class Controlador {
    +JanelaPrincipal janela
    +APIClient api
    +criar_aluno()
    +editar_aluno()
    +criar_atividade()
    +criar_nota()
    +consultar()
    +atualizar_listagens()
  }
  class APIClient {
    +str endereco
    +listar_alunos()
    +criar_aluno(nome, matricula)
    +listar_atividades()
    +criar_nota(aluno_id, atividade_id, valor)
    +media_do_aluno(aluno_id)
    -_requisitar(metodo, caminho, dados)
  }
  Controlador --> JanelaPrincipal : lê eventos e atualiza
  Controlador --> APIClient : utiliza Facade
```

## Fluxo da requisição

```mermaid
sequenceDiagram
  actor Usuario
  participant Tela as JanelaPrincipal (Qt)
  participant Controle as Controlador
  participant Facade as APIClient
  participant Flask as app.py (Flask)
  participant Regras as GerenciadorService
  participant Dados as RepositorioJSON
  Usuario->>Tela: Clica "Cadastrar"
  Tela->>Controle: Evento clicked
  Controle->>Facade: criar_aluno(nome, matricula)
  Facade->>Flask: POST /alunos (JSON)
  Flask->>Regras: criar_aluno(dados)
  Regras->>Dados: adicionar(dados)
  Dados-->>Regras: Registro salvo no JSON
  Regras-->>Flask: Aluno
  Flask-->>Facade: HTTP 201 + JSON
  Facade-->>Controle: Dados retornados
  Controle->>Tela: Atualiza tabela
```
