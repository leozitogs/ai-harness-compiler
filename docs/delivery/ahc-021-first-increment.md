# AHC-021 — Primeiro incremento executado

Sprint 2.5 começou por pedido do PO. Este incremento entrega contratos, corpus
congelado e avaliador offline de um artefato; não conclui a história ou a sprint.

Em Windows/Python 3.13.7, 321 testes passaram sem skips. Lint, formatação, mypy,
schemas, AGENTS, planos Sprint 1/2/2.5, memória e wheel/sdist passaram.
40 novos testes cobrem estados, revisão/cobertura/suporte, hashes, quotes, versões,
leakage por IDs e clones renomeados, erro de artefato/revisão, holdout e saída exclusiva.
Fixtures de revisão são declarações de protocolo, não revisão semântica de produto.

Corpus: 8 casos development e 8 holdout, expectativas/rubrica propostas, hashes
congelados antes de tuning. Nenhum prompt otimizado ou geração de holdout executada.
O corpus sintético da mesma sessão não é um benchmark independente ou cegado.

Três artefatos existentes foram reavaliados, sem nova chamada de modelo:

| Artefato | Resultado frente à rubrica proposta | Revisão humana |
|---|---|---|
| Qwen3.5 do estudo inicial | fail: nenhuma BusinessRule; conflito formal inesperado | pendente |
| Qwen3 cold em CA | fail: nenhuma BusinessRule | pendente |
| Qwen3 warm em CA | fail: nenhuma BusinessRule | pendente |

`validate-eval-report` confirmou o vínculo dos três relatórios ao corpus; isso não
transforma fail em pass. Outros critérios continuam not-run. Modelo/execução não
são estabelecidos pelo avaliador offline e qualificação permanece not-established.

Limites: revisão/rubrica são metadata declarada sem auth. Faltam aprovação das
expectativas pelo PO, batch runner de geração real, budgets/metadata de sessão,
pipeline revisado e qualificação final. INC-0007 continua aberto, sem LES criada.
