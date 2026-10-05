# Decomposição verificável de tarefas

O pedido de “CoT de quebra de tasks” é implementado como um **plano observável**:
objetivos, fontes, dependências, deliverables, critérios e verificação. Não depende
de registrar raciocínio interno privado de um modelo.

## O que está implementado

`factory tasks` transforma CapabilityGraph em TaskGraph/v1. Cada capacidade
selecionada recebe design → implement → verify → review, com critérios de aceitação
copiados da fonte. O design espera a revisão das capacidades pré-requisito.
IDs são estáveis em relação à posição das capacidades no manifesto.

O validador rejeita ciclos, dependências ausentes, etapas removidas, critérios
alterados, seleções inválidas e gates ignorados. A saída informa `not-run`.
`ready_batches()` calcula ondas de precedência assumindo sucesso das anteriores.

```sh
uv run factory tasks project-definition --select ahc-001 ahc-002 ahc-003 ahc-004
uv run factory schema task-graph
uv run python scripts/generate_sprint_plan.py --check
uv run pytest tests/test_planning.py
```

O build também emite `.ai/workflows/task-graph.json`. A seleção de Sprint 1 é um
plano separado do grafo completo de funcionalidades futuras.

## Gates e limites

Selecionar apenas AHC-002 falha porque depende de AHC-001. Após conclusão real,
um operador pode informar `--completed ahc-001`; isso é uma declaração explícita,
não evidência validada automaticamente. Não usar essa opção apenas para contornar bloqueios.

Este planner é determinístico e usa quatro etapas fixas. Ele não descobre todas
as subtarefas de implementação, não executa comandos, não faz design semântico
via LLM e não mantém estado de execução. Refinamento humano pode subdividir
histórias e tarefas; futuras heurísticas/LLMs deverão produzir a mesma IR validável.

Os testes comprovam regras estruturais e rastreabilidade, não que qualquer
decomposição é completa ou ótima. No Planning, os Developers revisam escopo,
estimativas, dependências e critérios antes de selecionar o trabalho.
