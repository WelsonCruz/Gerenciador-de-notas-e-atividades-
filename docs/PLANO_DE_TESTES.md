# Plano de Testes de Qualidade — Projeto 8 (Gerenciador de Notas e Atividades)

Referência oficial: **Plano de Testes de Qualidade — Aplicações desktop QT + servidor Flask (Prof. Alex Carneiro, Turma CC5AN)**.

---

## 1. Critérios de Arquitetura e Design Patterns adotados

Conforme especificado no documento da disciplina:
> *"Cada aplicação deve demonstrar, por comportamento observável e não apenas por presença de classes, pelo menos um padrão criacional, um estrutural e um comportamental."*

O plano recomenda Factory Method, Facade e Strategy para o projeto 8. Estes foram os padrões escolhidos pelo grupo para atender às três categorias.

| Categoria | Padrão no Projeto 8 | Onde está implementado | Comportamento Observável |
|---|---|---|---|
| **Criacional** | **Factory Method** | `servidor/factories.py` (`FabricaRegistros` / `FabricaRegistrosPadrao`) | Centraliza e padroniza a instanciação dos modelos de domínio (`Aluno`, `Atividade`, `Nota`). Permite trocar a criação sem alterar o serviço nem os repositórios. |
| **Estrutural** | **Facade** | `servidor/services.py` (`GerenciadorService`) e `cliente/api_client.py` (`APIClient`) | **No servidor:** `GerenciadorService` reúne e orquestra alunos, atividades e boletim, ocultando múltiplos repositórios e regras de concorrência.<br>**No cliente:** `APIClient` simplifica toda comunicação HTTP em métodos orientados a domínio para a interface Qt. |
| **Comportamental** | **Strategy** | `servidor/strategies.py` (`EstrategiaMedia`, `MediaNormalizada`, `MediaPonderadaPorValorMaximo`, `MediaAritmeticaDireta`) | Permite alternar dinamicamente o critério de cálculo de média tanto via API (`?criterio=`) quanto na interface gráfica (seletor de critério na aba de consulta). |

---

## 2. Cenários de Teste Oficiais (Seção 8 do Documento)

### T8.1 — Registrar nota e atualizar boletim
- **Objetivo:** Validar o fluxo de registro de notas e atualização imediata do boletim do aluno.
- **Pré-condições:** Aluno cadastrado e pelo menos duas atividades avaliativas cadastradas.
- **Ações:**
  1. Cadastrar aluno ("Lucas Ferreira", matrícula "2026001");
  2. Cadastrar atividade "Prova Oficial" (nota máxima 10,0);
  3. Cadastrar atividade "Trabalho Prático" (nota máxima 10,0);
  4. Lançar nota 10,0 na primeira atividade;
  5. Lançar nota 8,5 na segunda atividade;
  6. Consultar o boletim do aluno.
- **Resultado Esperado:** Ambas as notas aparecem listadas na tabela do boletim com suas notas máximas e equivalentes na escala de 0 a 10; a média final é calculada e exibida como **9,25 / 10** com **2 notas consideradas**.
- **Resultado Observado:** **PASSOU** no teste automatizado `test_T8_1_registrar_nota_e_atualizar_boletim`. A demonstração visual permanece uma etapa manual de entrega.

---

### T8.2 — Validar nota, peso e vínculo
- **Objetivo:** Garantir a consistência dos dados, limites de notas, pesos e regras de integridade referencial.
- **Pré-condições:** Aluno e atividade cadastrados.
- **Ações:**
  1. Tentar lançar nota negativa (`-1,0`) ou nota superior à máxima (`11,0`);
  2. Tentar cadastrar valores não numéricos (`NaN`, `inf`, `True`, textos);
  3. Tentar cadastrar atividade com peso / valor máximo menor ou igual a zero;
  4. Tentar lançar nota vinculada a aluno inexistente (`id=9999`) ou atividade inexistente (`id=9999`);
  5. Tentar lançar uma segunda nota para a mesma atividade no mesmo aluno;
  6. Tentar reduzir a nota máxima de uma atividade para valor inferior a uma nota já lançada;
  7. Excluir um aluno e verificar a remoção das notas associadas.
- **Resultado Esperado:**
  - Notas fora da faixa [0, valor_maximo] são rejeitadas com HTTP 400 / mensagem explicativa;
  - IDs inexistentes retornam HTTP 404;
  - Duplicidade de vínculo retorna HTTP 409;
  - Exclusão em cascata limpa as notas vinculadas sem deixar registros órfãos.
- **Resultado Observado:** **PASSOU** (validado no teste automatizado `test_T8_2_validar_nota_peso_e_vinculo`).

---

### T8.3 — Persistência e integridade dos dados
- **Objetivo:** Verificar a persistência atômica em arquivos JSON locais, integridade contra corrupção e restrições de concorrência / formato de matrícula. Como o enunciado não prevê autenticação, este cenário não representa login ou autorização de usuários.
- **Pré-condições:** Aplicação em execução.
- **Ações:**
  1. Cadastrar aluno com zeros à esquerda (ex.: matrícula `"00789"`);
  2. Cadastrar atividade e lançar nota;
  3. Fechar a aplicação e recriar o serviço a partir do mesmo diretório de dados;
  4. Tentar cadastrar matrícula com letras/símbolos (`"A-100"`);
  5. Tentar cadastrar matrícula duplicada;
  6. Simular falha de leitura em arquivo corrompido.
- **Resultado Esperado:**
  - Dados são recuperados integralmente com zeros à esquerda preservados;
  - Matrícula aceita estritamente números;
  - Matrícula duplicada é barrada com HTTP 409;
  - A escrita atômica (`.tmp` + `replace`) impede gravações parciais; arquivos inválidos geram `ErroRepositorio` sem destruição dos dados prévios.
- **Resultado Observado:** **PASSOU** (validado no teste automatizado `test_T8_3_persistencia_e_controle_de_acesso`).

---

### T8.4 — Facade e Strategy de média
- **Objetivo:** Demonstrar o funcionamento desacoplado da Facade (`GerenciadorService`) e a substituição comportamental de critérios de média via Strategy (`EstrategiaMedia`).
- **Pré-condições:** Aluno cadastrado com atividades de pesos diferentes:
  - Atividade 1: valor máximo 5,0 | Nota: 5,0 (100% de aproveitamento);
  - Atividade 2: valor máximo 10,0 | Nota: 5,0 (50% de aproveitamento).
- **Ações:**
  1. Calcular média com `MediaNormalizada` (padrão): $(10 + 5) / 2$;
  2. Calcular média com `MediaPonderadaPorValorMaximo`: $(5 + 5) / (5 + 10) \times 10$;
  3. Calcular média com `MediaAritmeticaDireta`: $(5 + 5) / 2$;
  4. Alternar a estratégia dinamicamente pelo método `definir_estrategia_media()`.
- **Resultado Esperado:**
  - `MediaNormalizada` resulta em **7,50 / 10**;
  - `MediaPonderadaPorValorMaximo` resulta em **6,67 / 10**;
  - `MediaAritmeticaDireta` resulta em **5,00 pontos**;
  - O resultado observável se altera comprovando o isolamento do padrão comportamental.
- **Resultado Observado:** **PASSOU** no teste automatizado `test_T8_4_facade_e_strategy_de_media`. O seletor da interface permite demonstrar a troca do critério manualmente.

---

## 3. Resumo da Execução de Todos os Testes

Comando executado:
```bash
python -m unittest discover testes -v
```

**Resultado:**
- Total de testes descobertos: **27**
- Testes aprovados: **27** (100%)
- Falhas / Erros: **0**
- Tempo de execução: ~1,9 segundos
