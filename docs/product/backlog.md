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
| AHC-001 | E1 / Intake canônico e limites | P0 | — | Candidata Sprint 1 |
| AHC-002 | E1 / Perfil multidimensional de domínio | P0 | 001 | Candidata Sprint 1 |
| AHC-003 | E1 / Evidence Pack com proveniência | P0 | 001 | Candidata Sprint 1 |
| AHC-004 | E1 / Confiabilidade e benchmark offline | P0 | 001 | Candidata Sprint 1 |
| AHC-005 | E2 / PromptSpec e SkillSpec | P1 | 002, 003 | A refinar |
| AHC-007 | E3 / Tools e Policy Engine | P1 | 005 | A refinar |
| AHC-008 | E3 / Eval runner e Simulation Lab | P1 | 004, 005 | A refinar |
| AHC-006 | E2 / Context Engine | P1 | 003, 005 | A refinar |
| AHC-009 | E3 / Adapter de LLM e pesquisa | P1 | 003, 007 | A refinar |
| AHC-010 | E4 / Execução durável e observabilidade | P2 | 008, 009 | A refinar |
| AHC-012 | E4 / Instalação e rollback | P2 | 004, 008 | A refinar |
| AHC-011 | E5 / Busca de arquiteturas | P2 | 006, 010 | A refinar |
| AHC-014 | E4 / API e operação multi-projeto | P2 | 010, 012 | A refinar |
| AHC-013 | E5 / Evolução e Experience Store | P3 | 010, 011, 012 | A refinar |

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
explicar impedimento e ação necessária. Por enquanto, o estado de sprint é proposto.
Sem velocity histórica, não usar soma de pontos como previsão de entrega.
