# Sprint 2.6 — Interrupção no preflight e correção proposta

O PO autorizou o pedido `a28e6065…` com até 16 invocações. O executor consumiu o
claim e parou no preflight, antes de construir o provider: **zero invocações,
zero recibos de chamada, nenhum retry**. O pedido ficou encerrado; orçamento não
utilizado não autoriza retomada. Fontes, autorização e saída privada originais
permanecem intactas.

## Diagnóstico sem conteúdo reservado

A rubrica confere. Os oito arquivos de caso têm os mesmos hashes brutos aprovados
e contratos válidos. Cada um diverge nos três hashes derivados: caso, input e
snapshot sem id/nome. A investigação processou arquivos autorizados em Python e
mostrou ao autor do candidato somente metadados, nunca regras ou respostas.

O campo público `Constraints.max_build_cost_usd` tem tipo `float` e default Python
`0` inteiro. Um objeto construído com esse default pode ter `model_dump()` com
inteiro; JSON salvo por `json_text(model_dump())` mantém essa representação.
Desserializar pelo contrato normaliza para `0.0`. Ambos são válidos, mas o hash
canônico distingue representações. Nos oito casos, repor somente essa diferença
no dump carregado recupera exatamente os três digests antigos. Validar um
roundtrip sem comparar seus hashes não detecta esse defeito.

Não alteramos defaults de domínio, função de hash, candidato, executor ou
validadores. Não afrouxamos comparação para fazer o reservado passar. O guard
funcionou: rejeitou metadados incompatíveis antes de enviar dados ao modelo.

## Correção revisável

`freeze_serialized_case` congela os **bytes existentes**, valida/desserializa e
confere estabilidade do snapshot após outro roundtrip antes de produzir binding.
O novo helper evita calcular digests sobre o objeto anterior à serialização.
Os testes reproduzem a falha com inputs sintéticos, preservam o pedido consumido
e exigem nova decisão para materializar uma correção.

Proposta: `evals/understanding/v2/reserved-correction/proposal.json`.
Novo corpus de metadados:
`e5cd1829bd1a74401a8240a3d6562df2f1d60bc72b88e0aaf82acb45cd519917`.
Pedido prospectivo:
`f5e410f3831c90615f7e7fc60b92c339b95f619db99685da2d06d7e259194c55`.

Somente os três digests derivados de cada caso mudam. Todos os hashes brutos,
ids, regras, expectativas, famílias, cenários, fontes, rubrica, candidato, executor,
perfil e limites permanecem iguais. Nova identidade/saída de execução termina em
`-02`, para não reutilizar o pedido consumido.

A proposta é **minuta pendente**, não um pedido aprovado: o protocolo corrigido
mantém `review: null`. Valores de revisor/comentário estão identificados como
planejados; nenhum `HumanDeclaration` real foi criado para eles. O digest
prospectivo é calculado a partir dos valores exatos que serão materializados
somente se o PO confirmar a correção de metadados e autorizar esse novo pedido.
Não há arquivo real de nova autorização nem nova execução.

Essa confirmação conjunta exige os mesmos limites: oito casos, até 16 invocações
sequenciais de análise v3.4/auditoria v4.1 pela assinatura Codex, 180s por chamada,
reserva de 20s de limpeza dentro de sessão de 3.600s, parada na primeira falha,
sem retry/repair/fallback/retomada, ferramentas, web, API por chave, assets,
treinamento ou promoção. A nova saída será privada em
`.factory/reserved-v2-executions/reserved-v2-20261021-02/`.

Sem aprovação das novas saídas, avaliação semântica continua pendente. Nenhum
modelo, história ou sprint foi aprovado. O resumo operacional público é redigido;
arquivos e evidências privadas não são publicados.
