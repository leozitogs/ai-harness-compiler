# Sprint 2.6 — campanha v4.1 interrompida, quatro saídas disponíveis

Registro: 2026-10-28. Pedido e identidade da rodada preparados em 2026-10-27.

## Execução e encerramento

O PO respondeu **“Autorizo esta única rodada nesses limites”** à pergunta
`call_0fa94728f3b64dd6ae4befac35632ae4`, vinculada ao pedido
`84bf9677d4e5fd3468bc5b19e41461b9790656ccaa07d0bc2b99957a22114bbc`.
Não alteramos o candidato, inputs, expectativas ou protocolo durante a execução.

A campanha `dev-v41-20261027-01` terminou com **failed/case-failed** após
**9 invocações controladas, em 241,24 s (4min01s)**. O worker da nona invocação,
análise de `dev-new-domain-v4`, saiu com código 2 após 2,34 s; o transporte
registrou `worker-failed`. Não houve timeout registrado, retry, repair, fallback
ou retomada. Todos os nove recibos registram contenção Windows Job, solicitação
de encerramento da árvore e reaping da raiz, inclusive o worker que falhou.

Contagens por status, sem confundir resultados tentados com concluídos:

| Medida | Resultado |
| --- | --- |
| Invocações bem-sucedidas / falhas | 8 / 1 |
| Casos completos | 4 |
| Caso interrompido, sem análise válida retida | 1 |
| Casos não iniciados | 3 |
| Assessment disponível | 4, todos inicialmente not-run |

O relatório contém cinco resultados de tentativas, não cinco casos completos.
O replay canônico passou. O orçamento está **consumido e fechado**: as sete
invocações não utilizadas do teto não autorizam continuar, repetir ou retomar.
Invocações controladas não equivalem a requisições internas invisíveis do CLI.

[Metadados, recibos e hashes](../evidence/sprint-2-6-v41-development-20261028/execution.json).
Outputs e journals permanecem privados. Nenhuma chamada adicional foi feita para
diagnóstico. Sem assets, reservado, treinamento, promoção de defaults ou compilação.

## Diagnóstico offline e limites

O código 2 do worker é genérico: ele sanitiza exceções sem reter erros brutos do
provedor, prompts privados, credenciais ou eventos intermediários. Os artefatos
atuais **não permitem determinar a causa específica**. Não atribuir a falha a
quota, autenticação, serviço, domínio novo ou erro semântico do modelo sem evidência.
Não há resposta válida retida para avaliar esse quinto caso.

O diagnóstico local validou o contrato do payload preparado, a estrutura do schema
e o hash vinculado ao débito. A entrada serializada tem 15.141 bytes, abaixo de
1 MiB. O input aprovado e o schema da análise são idênticos aos desse caso na
baseline, que teve execução válida. Isso exclui essas diferenças observadas,
sem provar o que ocorreu dentro do worker/provedor nesta tentativa.

[Diagnóstico sanitizado](../evidence/sprint-2-6-v41-development-20261028/diagnosis.json).
Foi apenas replay e validação de dados locais; não chamou worker, CLI ou modelo.
`INC-0033` registra a falha técnica ainda sem causa ou resolução comprovadas.

## Avaliação disponível, sem extrapolar a campanha

| Caso | Execução | Avaliação inicial / observação |
| --- | --- | --- |
| dev-adversarial-v4 | Completa | not-run; rejeição explícita do fragmento e análise legítima ready. |
| dev-ambiguous-v4 | Completa | not-run; confirmação aparece como rule, sem pergunta bloqueante sobre o titular do papel. Pergunta legítima sobre conclusão permanece. |
| dev-branding-conflict-v4 | Completa | not-run; preserva conflito e blocked, mas não formula pergunta explícita de precedência. Possível regressão semântica. |
| dev-compatible-rules-v4 | Completa | not-run; visibilidade exclusiva e revisão/aprovação aparecem como rules. Demais obrigações preservadas. |
| dev-new-domain-v4 | Falhou na análise | Sem análise/assessment disponível; não julgar semanticamente. |
| dev-rules-a-v4 | Não iniciada | Sem nova saída. |
| dev-rules-b-v4 | Não iniciada | Sem nova saída. |
| dev-unread-assets-v4 | Não iniciada | Sem nova saída. |

Nas quatro saídas disponíveis há zero falhas determinísticas de cobertura, com
as mesmas expectativas e schema. As três falhas tipadas anteriores não aparecem
nos dois casos corretivos. Isso é uma observação estrutural favorável, não quatro
PASS humanos, comparação completa das oito respostas ou prova causal do prompt.
O auditor continua consultivo e não supre julgamento independente.

Em `dev-branding-conflict-v4`, recomendo **FAIL em incerteza** pela ausência da
pergunta de precedência prevista na expectativa narrativa revisada. O contrato
tipado exige o conflito, mas não cadastra essa pergunta como obrigação própria;
por isso não acusa essa omissão automaticamente. Não acrescentar retroativamente
um FAIL determinístico, mudar as expectativas ou interpretar reconhecimento de
conflito como aprovação automática dos seis critérios.

## Pacote de revisão e próximos passos

Pacote privado: `.factory/v41-partial-po-review/po-review.md`, com quatro documentos,
fontes, 15 vínculos de cobertura, 49 achados e 72 componentes completos.
Proposta de revisão pendente:

`a9e0efdc87bab33580e892a95b81c323a3d346c56c3144d92bf6df4225a93cd9`.

Propomos seis critérios PASS para adversarial, ambíguo e compatível. Para conflito,
FAIL em incerteza e PASS nos outros cinco, preservando blocked pelo conflito real.
O PO precisa ler e julgar estes novos snapshots; os quatro casos sem saída não
recebem julgamentos nem herdam aprovações anteriores.

1. Registrar a revisão humana das quatro saídas disponíveis.
2. Estudar diagnóstico sanitizado mais preciso na fronteira worker/provedor com
   testes offline, preservando privacidade e sem afrouxar contenção ou limites.
3. Preparar, se necessário, pedido novo de verificação com escopo explícito e
   autorização própria. Não retomar o pedido consumido nem repetir chamadas para
   tentar descobrir a causa sem orçamento aprovado.
4. Cobrir os casos faltantes e a possível regressão antes de conclusão ou promoção.

`INC-0031` permanece aberto: os sinais parciais não demonstram resolução completa.
O modelo não está qualificado e AHC-021/022/Sprint 2.6 continuam em andamento.
