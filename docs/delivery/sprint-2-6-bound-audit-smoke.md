# Smoke autorizado da auditoria com vínculos — 21/10/2026

## Execução observada

O PO autorizou “Autorizo a única chamada com esses limites”, vinculada ao protocolo
`8b3adf3a5e68ba7b417e398d6e03382e3de302724d9ea143c6a09b38bbd88799`.
O [protocolo original](../evidence/sprint-2-6-bound-audit-smoke-20261021/protocol.json)
e o [evento de autorização](../evidence/sprint-2-6-bound-audit-smoke-20261021/authorization.json)
permanecem separados. O campo de espera no protocolo é histórico, anterior ao aceite.

Foi realizada **uma chamada** pela assinatura ChatGPT/Codex CLI, modelo solicitado
`gpt-6.1-sol`, usando somente a análise pública já aprovada `dev-new-domain` e suas
fontes literais. Não foram enviados reviews humanos ou expectativas do corpus.
Receita explícita: `component-audit/v4.1`; código de origem integrado pelo PR #61.

Resultado: **relatório estruturalmente válido**, em **35,763719 segundos**. O
provider aceitou o schema submetido nesta execução; o host validou sete achados,
dois componentes e oito fontes, incluindo o digest exato de `context-4`. A resposta
final, recibos e relatório tipado estão no
[inventário](../evidence/sprint-2-6-bound-audit-smoke-20261021/artifact-inventory.json).

Limites cumpridos: uma chamada serial, até 180 segundos por chamada e 240 por
sessão, zero retries/repair, ferramentas, assets, holdout, treinamento, API paga
ou fallback. O orçamento está **consumido e encerrado**, separado das rodadas de
16 chamadas anteriores. Não há repetição automática.

## O que isso verifica

O teste exercitou no provider o schema candidato verificado anteriormente apenas
offline. O novo retorno passou pelos mesmos checks estritos do relatório v4,
sem corrigir hashes ou reclassificar julgamentos no host. A resposta inválida
original continua intacta e rejeitada nas regressões. O runner foi arquivado em
base64 para preservar exatamente seus bytes autorizados, incluindo BOM/CRLF;
não é código gerado para execução em um projeto alvo.

INC-0025 tem resolução verificada **somente nesse escopo**: restrições estruturais
testadas offline e compatibilidade exercitada com um relatório real válido para
o snapshot original. Isso não demonstra ganho causal, estabilidade ou redução de
taxa de falhas. Não certifica todos os tamanhos de schema, modelos ou providers,
nem que uma implementação remota sempre respeitará as restrições. O host continua
rejeitando divergências e a receita permanece opcional.

## O que permanece separado

O parecer contém uma sugestão consultiva de pergunta sobre aplicabilidade da
identidade. Ela não é convertida em impedimento ou aceite: o PO já aprovou a
análise original no escopo de intenção. A validação estrutural deste parecer não
aprova sua interpretação de negócio. Não houve novo julgamento humano semântico.

`semantic_status` e `model_qualification` continuam `not-established`;
`compilation_eligibility` continua `not-authorized`. Default/CLI permanecem v4.0
para auditoria, sem promoção automática. Digest imutável do modelo, parâmetros
efetivamente observados, custo e recursos permanecem desconhecidos; o modelo
registrado é o solicitado, não uma identidade imutável observada.

As pendências de AHC-021/022 estão na
[matriz de revisão](sprint-2-6-prerequisites-review.md): reservado v2 ainda não
migrado/revisado, metadados incompletos e revisão de entrega. A sprint não foi
encerrada por esse smoke. Nenhum holdout foi aberto ou parâmetro otimizado.
