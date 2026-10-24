# Gerenciador de Notas e Atividades de Alunos

**Disciplina:** Paradigmas de Programação  
**Turma:** CC5AN  
**Professor:** Alex Carneiro  
**Tecnologias:** Python, Flask, PySide6 (Qt) e JSON local

Integrantes do Projeto:
Ana Carolina Gonçalves de Melo

Daniel Fernandes Santos 

Daniel Rodrigues da Costa

Davi Patricio Gimenes 

Ramon Barbosa de Sousa

Welson Ferreira da Cruz 

## 1. Visão geral

Aplicação desktop para administrar **alunos, atividades e notas**. A tela Qt (cliente) envia requisições HTTP para um servidor Flask, que valida os dados e os grava em arquivos JSON locais. Não utiliza banco de dados, nuvem, IA ou APIs de terceiros.

**O que pode fazer:**

- Cadastrar, listar, editar e excluir alunos; impedir matrículas duplicadas.
- Cadastrar, listar, editar e excluir atividades, informando a nota máxima.
- Registrar, listar, alterar e excluir notas; impedir duas notas do mesmo aluno para a mesma atividade.
- Consultar notas e calcular média de um aluno.
- Manter os dados nos arquivos JSON após fechar e abrir novamente.

**Regra da média:** para permitir atividades com notas máximas diferentes, cada nota é convertida para a escala de 0 a 10 (`nota / valor_maximo * 10`). A média é a soma dos valores convertidos dividida pelo número de atividades **com nota cadastrada**. Atividades não avaliadas não contam. Se não houver notas, retorna `null`/“sem notas”. Exemplo: 8/10 e 3/5 resultam em média **7,00/10**. Uma nota 8,5 em uma atividade que vale 8,5 equivale a 10/10.

## 2. Estrutura de pastas

```text
gerenciador-notas/
├── cliente/
│   ├── main.py          # inicia Qt e servidor local automaticamente
│   ├── janela.py        # View: componentes de interface
│   ├── controlador.py   # Controller: ações dos botões
│   └── api_client.py    # Facade: requisições HTTP
├── servidor/
│   ├── app.py           # endpoints Flask
│   ├── models.py        # classes Aluno, Atividade, Nota
│   ├── services.py      # validações e regras do sistema
│   ├── repository.py    # Repository para arquivos JSON
│   └── dados/
│       ├── alunos.json
│       ├── atividades.json
│       └── notas.json
├── testes/               # testes de regras, API e cliente HTTP
├── docs/                 # requisitos, diagramas e guia de código
├── scripts/              # empacotamento para Windows
├── requirements.txt
└── README.md
```

## 3. Como executar

### Desenvolvimento (Python instalado)

Recomendado: Python 3.11 ou superior, no Windows.

```powershell
# Abra um terminal na pasta raiz do projeto
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python cliente/main.py
```

O cliente **inicia automaticamente o servidor Flask** em `http://127.0.0.1:8765` se ainda não estiver ativo. Se preferir ver as requisições, execute manualmente em dois terminais:

```powershell
python servidor/app.py
python cliente/main.py
```

No Linux/macOS, ative o ambiente com `source .venv/bin/activate`. Sistemas com interface Qt precisam de suporte gráfico.

### Distribuição sem instalar Python no computador de apresentação

O código-fonte requer Python e bibliotecas no computador de desenvolvimento. **Para cumprir a regra de uso sem instalar outros softwares no computador de apresentação**, gere a pasta portátil **em um computador Windows**:

1. No Windows com Python instalado, dê dois cliques em `scripts\gerar_executavel_windows.bat` (ou execute pelo terminal).
2. O script instala as dependências **somente no computador usado para compilar** e empacota servidor e cliente com PyInstaller.
3. Copie a pasta `dist\GerenciadorNotas\` inteira para o computador de apresentação.
4. Abra `GerenciadorNotas.exe`. Ele inicia `ServidorNotas.exe` automaticamente em segundo plano.

**Importante:** esta entrega contém o **código e o script de build**, não contém os executáveis Windows já compilados. Faça o build e teste em um segundo Windows, sem Python, antes da apresentação. Mantenha a pasta portátil em um local gravável (por exemplo, Documentos), para salvar `dados/*.json`. Não copie apenas o `.exe`: toda a pasta é necessária.

## 4. Design Patterns implementados

| Padrão | Categoria | Onde está | Problema resolvido |
|---|---|---|---|
| **Factory Method** | Criacional | `servidor/factories.py` (`FabricaRegistros` / `FabricaRegistrosPadrao`) | Centraliza a criação de `Aluno`, `Atividade` e `Nota`, desacoplando os modelos do serviço. |
| **Facade** | Estrutural | `servidor/services.py` (`GerenciadorService`) e `cliente/api_client.py` (`APIClient`) | **No servidor:** reúne operações de alunos, atividades e boletim ocultando múltiplos repositórios e regras de concorrência.<br>**No cliente:** simplifica chamadas HTTP em métodos orientados a domínio. |
| **Strategy** | Comportamental | `servidor/strategies.py` (`EstrategiaMedia`, `MediaNormalizada`, `MediaPonderadaPorValorMaximo`, `MediaAritmeticaDireta`) | Permite substituir ou configurar dinamicamente o algoritmo de cálculo de médias na API e na interface Qt. |
| **Repository** | Estrutural / Arquitetural | `servidor/repository.py` (`RepositorioJSON`) | Esconde leitura e gravação atômica de arquivos JSON do restante do servidor. |
| **MVC** | Arquitetural | `servidor/models.py`, `cliente/janela.py`, `cliente/controlador.py` | Separa dados, interface gráfica e lógica de controle dos eventos. |

Fluxo de exemplo: **Cadastrar aluno** → `Controlador.criar_aluno` → `APIClient.criar_aluno` → `POST /alunos` → `GerenciadorService.criar_aluno` → `RepositorioJSON.adicionar` → `FabricaRegistrosPadrao.criar_aluno` → `alunos.json`.

- Diagramas de classes em [docs/DIAGRAMAS.md](docs/DIAGRAMAS.md).
- Cenários oficiais de teste T8.1 a T8.4 em [docs/PLANO_DE_TESTES.md](docs/PLANO_DE_TESTES.md).

## 5. Endpoints

| Método | Rota | Ação |
|---|---|---|
| GET | `/saude` | Verificar conexão |
| GET / POST | `/alunos` | Listar / criar alunos |
| GET / PUT / DELETE | `/alunos/<id>` | Consultar / editar / excluir aluno |
| GET / POST | `/atividades` | Listar / criar atividades |
| GET / PUT / DELETE | `/atividades/<id>` | Consultar / editar / excluir atividade |
| GET / POST | `/notas` | Listar / registrar notas |
| GET / PUT / DELETE | `/notas/<id>` | Consultar / editar / excluir nota |
| GET | `/alunos/<id>/notas` | Consultar notas do aluno |
| GET | `/alunos/<id>/media` | Consultar média do aluno (aceita `?criterio=normalizada\|ponderada\|direta`) |
| GET | `/estrategias-media` | Listar estratégias de cálculo disponíveis |

**Exemplo — cadastrar aluno:**

```http
POST /alunos
Content-Type: application/json

{"nome":"Ana Silva","matricula":"2026001"}
```

Resposta `201`: `{"id":1,"nome":"Ana Silva","matricula":"2026001"}`.

Respostas de erro: `400` para informação inválida; `404` para registro inexistente; `409` para matrícula ou nota duplicada; `500` para erro de arquivo. Erros são retornados como `{"erro":"mensagem"}`.

## 6. Testes e demonstração

Execute na raiz do projeto:

```powershell
python -m unittest discover -s testes -v
```

Os testes verificam validação dos dados, regras de cálculo, persistência JSON, operações CRUD, cliente HTTP, endpoints Flask e um botão Qt com Facade simulada. Os testes que exigem Flask ou PySide6 são ignorados quando essas bibliotecas não estão instaladas. Consulte o relatório em `docs/RESULTADOS_TESTES.md`. Para testar o comportamento visual da interface, realize a sequência:

1. Abra o programa; cadastre Ana (matrícula 2026001).
2. Tente outra Ana com a mesma matrícula: o sistema deverá rejeitar.
3. Cadastre “Prova de Python”, valendo 10 pontos.
4. Na aba Notas, atribua 8.5 à Ana nessa atividade.
5. Em Consulta e média, selecione Ana e confirme **8,50 / 10**.
6. Altere a nota para 9, consulte novamente e confirme **9,00 / 10**.
7. Feche/reabra o aplicativo e confira que os registros continuam salvos.
8. Desligue o servidor e tente usar a interface para observar a mensagem de erro (quando iniciada separadamente).

Requisitos e condições de aceitação: [docs/REQUISITOS.md](docs/REQUISITOS.md). Orientação dos arquivos: [docs/GUIA_CODIGO.md](docs/GUIA_CODIGO.md).

## 7. Limitações importantes

- O programa é um **protótipo acadêmico local**, não um servidor público de produção. Usa Flask somente no endereço `127.0.0.1`.
- Arquivos JSON são adequados para demonstração de pequena escala. Não há transação entre arquivos em caso de falha durante uma exclusão em cascata; não use em produção multiusuário.
- Em edição de nota é possível mudar o valor, mas **não** alterar aluno/atividade da nota; para isso, exclua e recrie.
- Alterar a nota máxima de uma atividade recalcula proporcionalmente as médias existentes; não é permitido defini-la abaixo de uma nota já atribuída.
- A interface usa chamadas HTTP síncronas com timeout: para este projeto local, é uma simplificação intencional.
- A organização foi baseada no guia fornecido. O repositório de referência indicado não estava acessível para confirmar os nomes e o estilo exato de suas pastas.

## 8. Documentação do Projeto

A documentação completa do projeto está disponível na pasta **`docs/`** deste repositório.

Nela, estão disponíveis:

- **Diagramas de Classes:** representação da estrutura e dos relacionamentos entre as classes do cliente e do servidor.
- **Requisitos Funcionais:** descrição das funcionalidades que o sistema deve oferecer.
- **Requisitos Não Funcionais:** definição dos critérios de qualidade, desempenho e segurança do sistema.
- **Condições de Aceitação:** critérios que devem ser atendidos para considerar as funcionalidades implementadas corretamente.

📂 **Localização:** [`docs/`](./docs/)

