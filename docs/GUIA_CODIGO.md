# Guia simples para entender e apresentar o código

## O que estudar primeiro?

1. **`servidor/models.py` — Modelos:** classes `Aluno`, `Atividade` e `Nota` representam os dados. Cada um tem um identificador `id`.
2. **`servidor/repository.py` — Repository:** a classe `RepositorioJSON` faz `listar`, `buscar`, `adicionar`, `atualizar` e `excluir`. As outras partes não precisam saber como um JSON é salvo.
3. **`servidor/services.py` — Regras:** `GerenciadorService` valida os dados. Por exemplo, matrícula não pode repetir e nota não pode exceder a máxima.
4. **`servidor/app.py` — Servidor:** recebe as requisições HTTP, chama o service e devolve um JSON. Não faz a validação principal.
5. **`cliente/api_client.py` — Facade:** transforma operações como `criar_aluno()` em chamadas HTTP. O Controller não precisa montar URLs nem interpretar respostas.
6. **`cliente/janela.py` — View:** constrói telas, campos, botões e tabelas usando Qt. Não lê arquivos e não conhece as regras do sistema.
7. **`cliente/controlador.py` — Controller:** recebe o clique do botão, lê os valores da tela, chama `APIClient` e atualiza as tabelas.
8. **`cliente/main.py` — Inicialização:** abre o aplicativo e, se necessário, inicia o servidor local automaticamente.

## Como o fluxo funciona (exemplo real)

Você escreve **Ana** e **2026001** e clica em “Cadastrar” na aba Alunos.

- O Qt dispara o clique para `Controlador.criar_aluno()`.
- `APIClient.criar_aluno(...)` envia `POST /alunos`.
- A rota Flask chama `GerenciadorService.criar_aluno(dados)`.
- O service verifica nome, matrícula e duplicidade.
- `RepositorioJSON.adicionar(...)` salva os dados em `servidor/dados/alunos.json`.
- A API responde `201`, e a tela atualiza a tabela.

## Regras simples (para explicar na apresentação)

- **Aluno:** nome e matrícula obrigatórios; duas pessoas não podem ter a mesma matrícula.
- **Atividade:** título obrigatório e nota máxima maior que zero.
- **Nota:** aluno e atividade precisam existir; valor entre zero e a nota máxima; somente uma nota por aluno e atividade.
- **Média:** converte cada nota para a escala de dez, faz a média entre notas lançadas. Sem nota = “sem notas”.
- **Excluir aluno ou atividade:** suas notas relacionadas também são removidas.

## Onde modificar o programa?

| Se quiser... | Arquivo que você edita |
|---|---|
| Mudar textos, campos e botões | `cliente/janela.py` |
| Mudar o que acontece ao clicar | `cliente/controlador.py` |
| Mudar chamadas/endpoints do cliente | `cliente/api_client.py` |
| Adicionar um endpoint | `servidor/app.py` |
| Criar validação nova | `servidor/services.py` |
| Modificar onde os registros são gravados | `servidor/repository.py` |
| Alterar a estrutura de dados | `servidor/models.py` e validações correspondentes |

## Ordem recomendada para estudar e testar

1. Entenda uma classe de dados em `models.py`.
2. Acompanhe o método `criar_aluno()` no service.
3. Veja como o Repository grava o arquivo.
4. Encontre a rota `POST /alunos`.
5. Encontre `APIClient.criar_aluno` e `Controlador.criar_aluno`.
6. Repita o mesmo caminho para atividades e notas.
7. Execute o sistema, gere as falhas previstas e explique por que são rejeitadas.
8. Mostre os diagramas em `DIAGRAMAS.md`.

**Atenção:** os padrões foram aplicados no código e não apenas descritos no README. MVC aqui é uma divisão prática de responsabilidades, e a camada de regras (`services.py`) fica no servidor.
