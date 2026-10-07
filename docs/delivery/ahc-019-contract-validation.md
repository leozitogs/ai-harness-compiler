# AHC-019 / 019-01 — Evidências do primeiro incremento

Execução em 2026-10-06, Windows/Python 3.13.7, todos os extras instalados:
**237 testes aprovados**, sem skips. Lint/formatação, mypy e schemas aprovados.

```sh
pytest -q -p no:cacheprovider --basetemp .factory/understanding-full-4
factory validate-understanding examples/understanding/understanding.json
```

tests/test_understanding.py acrescenta 30 casos para preparação offline/snapshot
independente, refs/ponteiros/citações, regras extraídas vs hipóteses, unicidade,
confiança inventada, JSON roundtrip/schema, review antiga, resolução de perguntas/
conflitos, limite de arquivo e privacidade dos erros. O exemplo manual valida como
proposed; nenhuma chamada de modelo foi realizada ou registrada como aprovada.

Este incremento entrega contratos e CLI, sem concluir AHC-019 ou aplicar a proposta
ao compilador. Adapter, rubrica/dataset reservado, auth/workflow de revisão,
estudo e demonstração real permanecem nas subtarefas seguintes. Metadata de review
não autentica uma pessoa; validação estrutural não prova entailment de texto.

PR #9 corrigido foi integrado após resolução dos conflitos e revalidação da CI.
Sprint 2 começou por pedido explícito do PO; Review/Retro da Sprint 1 não foram
declaradas realizadas e modelo/capacidade continuam pendentes.
