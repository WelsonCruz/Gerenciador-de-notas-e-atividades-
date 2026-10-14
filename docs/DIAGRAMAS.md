# Diagramas de classes — estrutura implementada

Os diagramas usam a sintaxe **Mermaid** e aparecem automaticamente no GitHub.

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
    +RepositorioJSON alunos
    +RepositorioJSON atividades
    +RepositorioJSON notas
    +criar_aluno(dados)
    +criar_atividade(dados)
    +criar_nota(dados)
    +notas_do_aluno(id)
    +media_do_aluno(id)
  }
  GerenciadorService --> RepositorioJSON : usa 3 repositórios
  GerenciadorService ..> Aluno : cria
  GerenciadorService ..> Atividade : cria
  GerenciadorService ..> Nota : cria
```

`create_app()` em `app.py` é uma **função-fábrica Flask**, não uma classe. As rotas chamam `GerenciadorService`; este utiliza `RepositorioJSON` para persistência.

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
