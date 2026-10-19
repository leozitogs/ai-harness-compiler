# Sprint 2.6 — Kickoff e primeira execução

2026-10-19. Início explicitamente autorizado pelo PO ao encerrar a Sprint 2.5.5.
Estado: `in_progress`, fase `prerequisite-review-and-baseline-audit`.
Sem prazo/capacidade prometidos e sem treinamento iniciado.

## Objetivo e escopo adaptado

Comparar perfis por qualidade e recursos e decidir por evidência se fine-tuning
generalista se justifica. O plano anterior selecionava somente AHC-024/025/026,
mas AHC-024 depende de AHC-021/022 ainda abertas. A seleção agora incorpora
AHC-021/022/023 como trabalho remanescente; as dependências do produto não mudaram.

TaskGraph: 24 etapas técnicas, 20 ondas de precedência. Não representa 24 novas
implementações: reutilizar incrementos existentes, revisar o que falta e não marcar
histórias como Done por gerar o grafo. Ondas não prometem paralelismo ou capacidade.
`declared_completed_capabilities` continua somente AHC-001/002/003/004.

## Sequência e gates

| Ordem | Trabalho | Próxima evidência necessária |
| --- | --- | --- |
| 1 — AHC-021 | Revisar rubrica, corpus e outputs de desenvolvimento | Julgamento humano por critério, adjudicação dos diagnósticos e protocolo reservado revisável. |
| 2 — AHC-022 | Consolidar baseline/candidato e corrigir falhas confirmadas | Matriz completa do candidato sob o desenvolvimento congelado; manter tentativas/falhas. |
| 3 — AHC-023 | Decidir qualificação ou rejeição com evidência | Candidato congelado antes de avaliação separada; recursos e cold/warm medidos. |
| 4 — AHC-024 | Contrato de perfis por provider, compatibilidade e fingerprints | AHC-021/022 revisadas conforme dependências; contratos antes de alterar adapters. |
| 5 — AHC-025 | Experimentos controlados | Budget e permissões concretos, baseline julgável, repetições, variáveis controladas. |
| 6 — AHC-026 | Go/no-go de treinamento, piloto condicionado | Erro aprendível, dados/licenças, recursos e comparação sem treino; no-go é resultado válido. |

A ordem é foco operacional de um executor. O grafo técnico admite disponibilidades
conforme dependências reais; não adiciona uma dependência fictícia de 024 em 023.
Promoção, avaliação reservada e treino conservam seus gates próprios.

## Primeira tarefa executada — auditoria de entrada

Auditoria offline sobre fontes de desenvolvimento explicitamente selecionadas:

- **8 casos aprovados** e rubrica conferidos contra os hashes do manifesto congelado.
- **62 artefatos históricos** da rodada final da 2.5 conferidos contra o inventário.
- Baseline original: 7 gerações válidas e 1 erro estrutural; disposições esperadas
  nas válidas não representam aprovação semântica.
- Recuperação v3.1: um caso válido; não equivale a rodada completa/repetida.
- **8 assessments `not-run`**, por ausência de revisão humana, preservados como tal.
- Taxonomia inicial: erro de campos/tipo observado, possíveis omissões e possível
  suporte insuficiente; os dois últimos continuam diagnósticos consultivos sujeitos
  a falso positivo e julgamento humano.

Saída: [auditoria com hashes e pendências](../evidence/sprint-2-6-entry-20261019/audit.json).
Zero chamadas de modelo; holdout não aberto; nenhuma configuração, perfil ou dataset
de treino alterado. Inspeção de integridade não completa as histórias AHC-021/022/023.

## Próximo passo de execução

Preparar e julgar a revisão das oito respostas completas pelos seis critérios
aprovados. Priorizar erro estrutural e sua recuperação, ambiguidade com possível
suporte negativo e casos com possíveis omissões. Usar análises/fontes/diagnósticos
do desenvolvimento, preservando o parecer LLM como consultivo. Não preencher
`SemanticHumanReview` em nome do PO nem aprovar respostas em lote por CI verde.

Depois desse gate, definir orçamento concreto e congelar o programa/perfil antes
de nova comparação. A autorização desta sprint permite avançar no trabalho;
não substitui licença/consentimento de dados, contratação de serviços externos,
revisão humana de outputs ou autorização específica do protocolo reservado.

## Organização

- Plano: `planning/sprint-2-6.json`.
- Backlog da sprint: `planning/sprint-2-6.work-items.json`.
- Dependências verificáveis: `planning/sprint-2-6.tasks.json`, também conferido na CI.
- As revisões remanescentes da 2.5.5 ficam no seu registro fechado e issues abertas;
  não são disfarçadas como experimentos da 2.6.
