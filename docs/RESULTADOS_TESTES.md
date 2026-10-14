# Relatório de verificação (ambiente de geração)

**Comando:** `python -m unittest discover -s testes -v`

- **17 testes descobertos**.
- **14 testes aprovados:** 12 testes de regras e persistência, 2 testes do cliente HTTP usando um servidor local de teste.
- **3 testes ignorados:** 2 testes de endpoints Flask e 1 teste de interface PySide6, porque estas bibliotecas não estavam disponíveis no ambiente de geração e a instalação online falhou.
- **Verificação de sintaxe concluída:** `python -m compileall -q cliente servidor testes`.
- **Documento Word renderizado e verificado visualmente** (3 páginas).

**Pendências antes da entrega acadêmica:** em um computador Windows com Flask e PySide6 instalados, execute todos os testes; abra a interface e faça a demonstração completa; gere o pacote portátil e execute-o em outro computador sem Python. O projeto **não foi executado graficamente nem validado como executável Windows** neste ambiente.
