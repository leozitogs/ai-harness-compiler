# Sprint 2.6 — Rodada reservada corrigida

O PO confirmou a correção dos metadados e autorizou uma única rodada do pedido
`f5e410f3831c90615f7e7fc60b92c339b95f619db99685da2d06d7e259194c55`,
corpus `e5cd1829bd1a74401a8240a3d6562df2f1d60bc72b88e0aaf82acb45cd519917`.
Sua resposta foi “Confirmo a correção e autorizo a rodada nesses limites”.
O pedido materializado está em
`evals/understanding/v2/reserved-execution-corrected/request.json`.
A proposta anterior permanece como registro histórico pendente naquele momento;
este aceite posterior é a autoridade da materialização, sem alterar o histórico.

## Execução e integridade

Foram debitadas 16 invocações sequenciais pela assinatura ChatGPT/Codex CLI:
oito análises v3.4 e oito auditorias v4.1, todas concluídas tecnicamente em
476,681 segundos (aproximadamente 7min57s). Modelo solicitado: `gpt-6.1-sol`.
Cada chamada permaneceu no limite de 180s e a sessão no limite de 3.600s,
com reserva de limpeza de até 20s. Não houve retry, repair, fallback ou retomada.
Foram enviados apenas fontes e, nas auditorias, análises geradas; expectativas,
assets e ferramentas não foram enviados ao modelo. Nenhuma API por chave,
treinamento ou alteração de defaults foi utilizada.

O replay offline `factory validate-reserved-run` passou. Confere bytes,
recibos, fontes congeladas e reconstrução dos artefatos das respostas finais.
Não realiza nova chamada nem prova suporte semântico. Invocações debitadas não
são contagem observada de requests remotos; identidade imutável do modelo,
sampler, recursos e custo continuam desconhecidos. Os dois claims permanecem
consumidos: o anterior falhou com zero invocações e este terminou com 16.

## Resultado da avaliação offline

**O conjunto não passou.** Os oito assessments sem julgamento humano têm status
`fail`, por ausência de finding obrigatório com as fontes exigidas no check de
cobertura de regras. Há também um caso com disposição diferente da expectativa e
um caso sem a recusa exigida. Esses dois contadores podem se sobrepor; não são
casos adicionais nem scores de qualidade. Checks ainda não julgados continuam
`not-run`, sem compensar as falhas determinísticas.

Esses achados descrevem o contrato executado; a causa de cada ausência — omissão,
representação incompatível ou outro problema — ainda requer revisão específica.
Não atribuímos diagnóstico de negócio ou eficácia geral ao modelo. Pareceres do
auditor permanecem consultivos, mesmo quando estruturalmente válidos. Nenhum
aceite de desenvolvimento foi transferido para essas novas respostas.

## Revisão e próximos gates

O pacote privado
`.factory/reserved-v2-executions/reserved-v2-20261021-02/po-review/INDEX.md`
reúne os oito casos, expectativas originais, análises, auditorias, assessments
sem revisão humana e seus vínculos. Foi gerado offline, sem preencher julgamentos.
A revisão deve examinar critérios, obrigações, findings e componentes vinculados
às novas análises; aprovação humana não apaga uma falha determinística.

Preservar este reservado e seus resultados. Não ajustar prompts/candidato para
esses casos nem usá-los em treino, repair ou nova rodada sob a autorização atual.
Uma correção futura deve ser sustentada por reprodução independente em dados de
desenvolvimento e protocolo separado, preservando a contaminação potencial e a
necessidade de novo reservado independente para alegações de generalização.

A qualificação não foi estabelecida, a compilação não foi autorizada e AHC-021,
AHC-022 e Sprint 2.6 não foram concluídos. AHC-024/025/026 continuam sob seus
critérios próprios. Registro público contém somente metadados operacionais;
casos, respostas, autorização completa e documentos de revisão ficam privados.
