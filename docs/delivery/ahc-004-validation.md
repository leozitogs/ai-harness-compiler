# AHC-004 — Evidências locais

Execução em 2026-10-06, Windows/Python 3.13.7, todos os extras instalados.
Suíte completa: **190 testes aprovados**, sem skips. Lint/formatação, mypy,
schemas e TaskGraph verificados. Matriz remota Linux/Windows 3.12/3.13 é gate
adicional antes da integração.

```sh
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp .factory/reliability-full-3
```

| Critério | Evidência |
|---|---|
| Fixtures educação/comércio/dev-tools com critérios rastreáveis | Três manifestos + suite; testes comparam critérios de backlog/evals, builds, bytes e hashes |
| Falhas de escrita diagnosticadas sem alterar projeto existente | Injeção de ENOSPC na abertura e write do stream, permissão na reserva, recusa de destino existente antes de abrir artefatos |
| Benchmark offline com duração/tamanho/versão sem SLO fictício | 15 builds medidos, relatório versionado, dados brutos e método documentado; testes conferem bytes/arquivos contra filesystem real |

Testes também rejeitam adulteração de artefatos, caminhos de fixture fora da suíte,
reuso de sessão/relatório, repetições insuficientes e divergência dos critérios.
Nenhum código gerado foi executado pelo benchmark. Evals dos projetos fictícios
permanecem not-run. Resultado local não substitui CI em outros ambientes.
