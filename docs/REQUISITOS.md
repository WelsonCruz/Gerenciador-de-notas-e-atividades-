# Requisitos e condições de aceitação

## Requisitos funcionais

| ID | Requisito | Critério de aceite verificável |
|---|---|---|
| RF01 | Cadastrar aluno | Nome e matrícula válidos criam registro e retornam HTTP 201. |
| RF02 | Listar, editar e excluir aluno | Alterações aparecem na interface e na API; exclusão remove suas notas. |
| RF03 | Impedir matrícula duplicada | POST/PUT com matrícula já utilizada por outro aluno retorna HTTP 409. |
| RF04 | Cadastrar, listar, editar e excluir atividade | Cada atividade tem título e nota máxima positiva. |
| RF05 | Registrar, editar, listar e excluir nota | Nota pertence a aluno/atividade existentes e fica entre 0 e valor máximo. |
| RF06 | Impedir nota duplicada por atividade/aluno | Segundo cadastro retorna HTTP 409. |
| RF07 | Consultar notas por aluno | Lista contém atividade, valor, máximo e nota normalizada. |
| RF08 | Consultar média | Cálculo na escala de 0 a 10; sem notas retorna `null`. |
| RF09 | Persistir registros | Reinício da aplicação mantém os dados nos três JSON. |
| RF10 | Usar cliente gráfico Qt | A interface faz as operações via HTTP, sem ler arquivos JSON diretamente. |

## Requisitos não funcionais

| ID | Requisito | Critério de aceite |
|---|---|---|
| RNF01 | Servidor Flask e cliente Qt em módulos separados | Pastas `servidor/` e `cliente/` presentes. |
| RNF02 | Armazenamento local JSON, sem banco, nuvem e APIs externas | Somente arquivos `dados/*.json` armazenam registros. |
| RNF03 | Erros compreensíveis | API retorna JSON com `erro`; a tela apresenta uma caixa de aviso. |
| RNF04 | Código com Design Patterns demonstráveis | Repository, Facade e organização MVC apontam a classes concretas. |
| RNF05 | Documentação pública | README, diagramas e testes incluídos no repositório GitHub público. |
| RNF06 | Execução sem instalar softwares no computador de apresentação | Build portátil Windows executado e validado sem Python instalado (necessita compilar antes). |
| RNF07 | Servidor local | API escuta apenas em `127.0.0.1:8765`; sem exposição externa. |

## Testes da disciplina

- **Validação do código:** executar `python -m compileall -q cliente servidor testes`.
- **Comportamento:** `python -m unittest discover -s testes -v`.
- **Integração visual:** cadastrar aluno → atividade → nota → consulta → fechar/reabrir.
- **Falhas:** matrícula repetida, nota maior que máxima, item inexistente, servidor desligado.
- **Entrega pública:** colocar todo o conteúdo da pasta principal em um repositório GitHub público.

## Limites conhecidos

O roteiro da disciplina não fixa como calcular médias com atividades de pesos diferentes. Esta implementação usa **média aritmética das notas normalizadas para 0–10**. O professor deve aprovar a regra se pretender outro critério. A exigência de “sem instalação de softwares” só é verificada depois que o grupo compilar e testar os executáveis Windows, pois o ZIP de fontes por si só não elimina dependências.
