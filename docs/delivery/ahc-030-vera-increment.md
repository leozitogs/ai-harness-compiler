# AHC-030 — Incremento funcional da Vera

2026-10-19. Implementação autorizada pelo PO após a emenda de escopo. Entregues
captura Git limitada, contratos QA v1, runner de checks por revisão confiável,
inspeção opcional em uma tentativa e integração Vera/Nexo no LangGraph existente.
A história permanece em revisão; não há aceite ou encerramento automático.

## Comportamento

Vera recebe fontes e diff por base/head, critérios preservados e evidências de
checks. Achados têm severidade, impacto, recomendação, regra e citações verificadas
por linha. Reprodução proposta pelo modelo é sempre `not-executed`; check real
é produzido pelo runner. Cobertura declarada não certifica semântica ou completude.

Nexo deriva objetivo, bloqueios, checks falhos, matriz de critérios e carryover.
P0/P1 ou falha de execução impedem recomendar entrega plena. Parecer disponível
ao PO não estabelece critério atendido, qualificação de modelo ou cerimônia feita.
Mudanças de snapshot, commit, arquivos, diff ou memória invalidam o gate persistente.

Comparação preserva achados anteriores como pendentes de verificação semântica;
somente falhas de checks passam a superadas após resultado aprovado em novo head
sob os mesmos critérios. Falhas reais geram candidatos de INC, sem inventar causa
ou solução e sem promover LES ou modificar automaticamente a memória.

## Verificação

Regressões cobrem adulteração de conclusões, check/revisão divergentes, citações
inexistentes, injection, falso sucesso por CI verde, evidência não executada, budget,
timeout/saída, falha de provider sem fallback e retomada do gate Vera/Nexo. Os testes
de modelo são fakes offline; não são benchmark semântico de um provider.

Checks finais e demonstração serão acrescentados após executar a revisão capturada.
Ver [operação](../engineering/vera-review.md) e [ADR-0026](../adr/0026-vera-evidence-bound-review.md).
