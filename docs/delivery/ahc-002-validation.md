# AHC-002 — Evidências locais

Execução em 2026-10-06, Windows/Python 3.13.7, com todos os extras instalados.
Suíte completa: **173 testes aprovados**, sem skips. A matriz remota Linux/Windows,
Python 3.12/3.13 é gate adicional antes da integração.

```sh
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp .factory/domain-full-2
```

| Critério | Evidência |
|---|---|
| Domínio, arquétipo, dados, risco e origem tipados | tests/test_domain.py preserva dimensões em roundtrip, JSON Schema e render offline |
| Declaração/hipótese/incerteza sem confiança fabricada | Invariantes de status/origem, referência, justificativa, primary e confidence; alternativas preservadas sem seleção automática |
| Compatibilidade e migração documentadas | Snapshots reais v1/v2 migram para v3 e compilam; confidence antiga, digest adulterado e fonte revisada não migram silenciosamente |

O teste bloqueia sockets; não houve inferência, pesquisa ou chamada de modelo.
Contratos e testes verificam estrutura/proveniência, sem provar a classificação
de negócio. Evals do produto gerado permanecem not-run.
