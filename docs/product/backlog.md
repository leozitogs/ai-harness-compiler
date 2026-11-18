# Product Backlog

Fonte canônica de histórias, dependências e critérios de aceitação:
[`project-definition/project.yaml`](../../project-definition/project.yaml).
Este documento acrescenta prioridade e contexto de entrega. IDs `AHC-NNN` na
documentação correspondem a `ahc-nnn` no manifesto. São IDs locais, não números
de issues já criadas no GitHub.

Ordenação inicial proposta por valor, risco e dependências; revisar com o Product
Owner no refinamento. Estimativas são hipóteses de discussão, não compromisso de prazo.

| ID | Épico / história | Prioridade | Dependências | Situação |
|---|---|---|---|---|
| AHC-001 | E1 / Intake canônico e limites | P0 | — | Done — PR #6 integrado com CI verde |
| AHC-002 | E1 / Perfil multidimensional de domínio | P0 | 001 | Done — PR #8 integrado com CI verde |
| AHC-003 | E1 / Evidence Pack com proveniência | P0 | 001 | Done — PR #7 integrado com CI verde |
| AHC-004 | E1 / Confiabilidade e benchmark offline | P0 | 001 | Done — PR #9 corrigido integrado |
| AHC-005 | E2 / PromptSpec e SkillSpec | P1 | 002, 003, 019, 020 | A refinar após entendimento/blueprint |
| AHC-007 | E3 / Tools e Policy Engine | P1 | 005 | A refinar |
| AHC-008 | E3 / Eval runner e Simulation Lab | P1 | 004, 005 | A refinar |
| AHC-006 | E2 / Context Engine | P1 | 003, 005 | A refinar |
| AHC-009 | E3 / Adapter de LLM e pesquisa | P1 | 003, 007 | A refinar |
| AHC-010 | E4 / Execução durável e observabilidade | P2 | 008, 009 | A refinar |
| AHC-012 | E4 / Instalação e rollback | P2 | 004, 008 | A refinar |
| AHC-011 | E5 / Busca de arquiteturas | P2 | 006, 010 | A refinar |
| AHC-014 | E4 / API e operação multi-projeto | P2 | 010, 012 | A refinar |
| AHC-013 | E5 / Evolução e Experience Store | P3 | 010, 011, 012, 018 | A refinar |
| AHC-015 | E2 / DocumentationLearningSpec por projeto | P1 | 003, 005 | A refinar após entendimento/blueprint |
| AHC-016 | E2 / Compilador de documentação e memória | P1 | 004, 015 | A refinar |
| AHC-017 | E3 / Agent Factory com especialização | P1 | 005, 007, 009, 015 | A refinar |
| AHC-018 | E5 / Aprendizagem por experiências do projeto | P2 | 008, 010, 016, 017 | A refinar |
| AHC-019 | E1 / Entendimento generalista e regras de negócio | P0 | 002, 003 | In progress — contratos/adapter integrados; qualificação semântica pendente |
| AHC-020 | E2 / Blueprint e packs opcionais | P0 | 019 | Sprint 2 aprovada; depende da entrega 019 |
| AHC-021 | E1 / Rubrica e evals semânticos do entendimento | P0 | 002, 003, 004 | Sprint 2.6 — carryover; auditoria de entrada executada, revisão humana pendente |
| AHC-022 | E1 / Grounding e cobertura de regras | P0 | 021 | Sprint 2.6 — carryover; comparação completa e revisão pendentes |
| AHC-023 | E1 / Qualificação do modelo e perfil local | P0 | 022 | Sprint 2.6 — carryover; nenhum modelo qualificado |
| AHC-024 | E1 / Perfis de inferência por provider | P1 | 021, 022 | Sprint 2.6 — bloqueada pelos pré-requisitos |
| AHC-025 | E1 / Experimentos controlados | P1 | 024 | Sprint 2.6 — bloqueada; orçamento antes das chamadas |
| AHC-026 | E1 / Viabilidade de fine-tuning | P2 | 025 | Sprint 2.6 — condicional; treino não iniciado |

O [pipeline por projeto](project-generation-pipeline.md)
define o caminho dos novos itens e as diferenças entre capacidade interna e produto gerado.

## Esteira de engenharia — refinamento de 16/11/2026

Por solicitação do PO, foram acrescentadas AHC-031 a AHC-042 ao manifesto canônico.
A [estratégia de evolução](engineering-evolution.md) detalha adaptações, exclusões,
primeiras fatias e verificações; a fila está em
[`planning/engineering-evolution.json`](../../planning/engineering-evolution.json).
Todos os itens abaixo estão **propostos**, sem seleção de sprint ou execução.

Esse é o registro da proposta de 16/11. Em 18/11 o PO autorizou isoladamente a
[primeira fatia offline de AHC-031](../delivery/ahc-031-functional-change-slice-1.md),
com progresso em `planning/ahc-031.slice-1.json`; isso não conclui a história
nem seleciona os demais itens para uma sprint.

| ID | História | Prioridade proposta | Dependências |
|---|---|---|---|
| AHC-031 | Especificação funcional e exemplos | P1 | 019, 021, 022 |
| AHC-032 | Grafo de rastreabilidade e autoridade | P1 | 003, 015, 031 |
| AHC-033 | Contexto por etapa e busca avaliada | P1 | 006, 032 |
| AHC-034 | Delegação com privilégios atenuados | P1 | 007, 017, 033 |
| AHC-035 | Execução isolada e cotas globais | P2 | 008, 010, 034 |
| AHC-036 | Evidência de CI e checks por impacto | P1 | 004, 030, 032 |
| AHC-037 | Doctor e onboarding por papel | P2 | 004, 024 |
| AHC-038 | Intake de branding e design | P2 | 001, 003, 020, 032 |
| AHC-039 | Regressões derivadas de experiências | P2 | 008, 018, 036 |
| AHC-040 | Aprendizado operacional em sombra | P3 | 023, 025, 035, 039 |
| AHC-041 | Visão de fluxo e dossiê de decisões | P2 | 027, 028, 032, 036 |
| AHC-042 | Knowledge packs e documentação enxuta | P2 | 005, 015, 020, 033 |

O primeiro corte sugerido é uma fatia de AHC-031, quando seus pré-requisitos
forem satisfeitos. A Sprint 2.6 e suas pendências permanecem em seu escopo atual.

## Incremento já existente

A fundação de contratos, compilador, CLI, políticas de repositório e TaskGraph
está implementada antes da Sprint 1. Não contabilizar essa fundação novamente
como conclusão de AHC-001 a AHC-004: os critérios dessas histórias ampliam o comportamento atual.

## Regras de refinamento

Uma história deve descrever resultado observável, dados e restrições, critérios
testáveis, dependências e riscos. Dividir histórias grandes em fatias verticais
antes da seleção; os quatro estágios técnicos do TaskGraph não substituem esse refinamento.
Prioridade não libera dependências: um P0 bloqueado exige resolver seu pré-requisito.

Usar estados Proposed → Ready → In progress → In review → Done; Blocked deve
explicar impedimento e ação necessária. A Sprint 1 iniciou em 2026-10-06 por pedido
do PO; a capacidade total ainda não foi quantificada, sem compromisso de prazo.
O [plano detalhado](../delivery/sprint-1.md) registra tarefas e sequência de entrega.
Sem velocity histórica, não usar soma de pontos como previsão de entrega.

A [Sprint 2 replanejada](../delivery/sprint-2.md) propõe AHC-019 e AHC-020.
O plano anterior foi rejeitado pelo PO; o novo escopo foi aprovado em 2026-10-06,
com início autorizado separadamente. PR #9 e #14 integrados; Review/Retrospective
anteriores e capacidade continuam sem confirmação. Por pedido do PO, a
[Sprint 2.5](../delivery/sprint-2-5.md) concentra o foco em qualidade semântica e
qualificação do modelo antes de avançar no blueprint. Não declara Sprint 2 concluída.


AHC-030 foi incluída pelo PO na Sprint 2.5.5 antes da review: evolução funcional
da Vera para QA aprofundado, achados reproduzíveis e apoio ao Nexo no encerramento.
[Escopo e critérios](../delivery/ahc-030-reviewer-scope.md). Incremento funcional integrado
com correções; a [timebox 2.5.5 foi fechada por decisão explícita do PO](../delivery/sprint-2-5-5-review.md),
preservando revisões por critério e confirmação específica do achado.
A [Sprint 2.6 está em execução](../delivery/sprint-2-6-kickoff.md) na fase de
auditoria e revisão dos pré-requisitos, antes de perfis, experimentos e treinamento.
