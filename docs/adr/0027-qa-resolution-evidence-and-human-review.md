# ADR-0027 — Resolução de achados com evidência e decisão humana

Estado: aceito para implementação em 2026-10-19 por autorização do PO para corrigir
as pendências da review da Sprint 2.5.5. Complementa ADR-0026.

## Problema

A captura importada podia omitir `excluded_paths` sem rejeição pelo guard Git,
permitindo recomendar `ready-for-po` com arquivos alterados não inspecionados.
Além disso, a comparação conservava achados anteriores indefinidamente, sem fluxo
de confirmação de resolução. Omitir o achado da resposta atual não prova correção.

## Decisão

Captura e revalidação usam `git diff --name-only -z` sobre base/head completos.
A lista de exclusões deve corresponder exatamente às alterações menos as fontes
selecionadas, incluindo deleções e nomes com espaços/caracteres não ASCII.
Divergência invalida o pedido antes de execução e recomendação.

`QAFindingResolutionProposal/v1` contém os dois relatórios completos, o achado
anterior, citações atuais, checks aprovados e justificativa. Exige outro head,
mesma matriz de critérios, inspeção atual concluída da faceta e localização literal
das evidências. Não pode propor resolver um id ainda aberto na inspeção atual.
Checks comprovam execução, citações comprovam localização; a suficiência semântica
continua exigindo revisão humana.

`QAFindingResolutionReview/v1` registra confirmação/rejeição explícita, ator,
horário e comentário. Vera, Nexo e autores dos dois relatórios não podem ser o ator.
O CLI revalida a revisão atual antes de propor, decidir e comparar. Saídas são
novas, sem sobrescrever artefatos anteriores. Importação de decisões futuras,
repetidas ou de outro par de relatórios é rejeitada.

Comparações recebem decisões opcionais: somente confirmações vinculadas removem
o achado da lista pendente e o incluem em `resolved_previous_findings`.
Rejeição ou ausência de decisão mantém o achado pendente. `semantic_resolution`
global permanece `not-established`; resolver um achado não aceita critérios,
qualifica modelos, inicia ou encerra sprints.

Nexo recebe a comparação tipada, vinculada por digest ao checkpoint. Seu parecer
combinado inclui achados anteriores pendentes; P0/P1 mantêm `changes-required`,
mesmo com inspeção atual limpa. O `closure_assessment` continua identificado como
escopo da inspeção atual; recomendação e bloqueios combinados são explícitos.

## Compatibilidade e limites

Campos opcionais aditivos em `QAReviewComparison/v1` e `TeamRun/v1`; formatos sem
resoluções conservam o comportamento anterior. Novos schemas exportados. Capturas
antigas adulteradas deixam de ser aceitas; não há migração que presuma cobertura.

Ator é declaração no CLI local confiável, não identidade autenticada ou assinatura.
Uma pessoa com capacidade de alterar todos os artefatos pode fabricar declarações;
hashes garantem consistência, não identidade. O modelo não recebe ferramentas de
confirmação. Fixtures podem simular uma decisão para testar a função, identificadas
como simulação; isso nunca representa a decisão do PO sobre o repositório real.

Não exigir ancestralidade para comparação: um rollback explícito pode ser válido.
Isso não autoriza resolver achados sem a decisão e evidências previstas acima.
