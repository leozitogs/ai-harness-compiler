# Sprint 2.6 — resultado da campanha de desenvolvimento v4

Data: 2026-10-27. Execução encerrada; revisão humana dos outputs pendente.

## Execução autorizada e verificada

O PO respondeu **“Autorizo esta única rodada nesses limites”** à pergunta
`call_bbe0268ecd30479b8bb260e889d999d8`, vinculada ao pedido
`a64cb6e7a779d4c5c201db9beb54238e793604fc564eb963b3987e37ffd88236`.
O [protocolo preparado](sprint-2-6-v4-development-campaign.md) e seus limites não
foram alterados para executar. A autorização recebida foi registrada separadamente.

A campanha `dev-v4-20261027-01` concluiu **16 invocações sequenciais e oito casos**
em **445,88 segundos (7min26s)**. Não houve retry, repair, fallback ou retomada.
Os 16 recibos registram sucesso de transporte, contenção Windows Job, solicitação
de encerramento da árvore e reaping observado da raiz. O worker mais demorado
levou 64,94 s, dentro da concessão de 180 s. Essas durações descrevem esta rodada
remota; não são benchmark de inferência local, VRAM ou eficiência de outro modelo.

O replay offline conferiu fonte congelada, corpus, autorização, claims, ordem,
débitos, payloads, recibos e respostas. O orçamento está **fechado**; não autoriza
mais chamadas, mesmo que parte do prazo global não tenha sido usada.

[Metadados públicos, recibos e hashes](../evidence/sprint-2-6-v4-development-20261027/execution.json).
Respostas integrais e journals permanecem privados. Nenhum asset ou reservado foi
aberto; não houve treino, mudança de defaults ou autorização de compilação.
O compilador, o candidato, os prompts e as expectativas não foram alterados.

## Resultado de avaliação inicial

As oito disposições coincidem com as expectativas (seis ready e dois blocked).
Isso não basta para aceitação: há **três falhas determinísticas de cobertura em
dois casos**. Os outros seis assessments permanecem `not-run`, não PASS.

| Caso | Assessment inicial preservado | Achado |
| --- | --- | --- |
| dev-adversarial-v4 | not-run | Rejeição explícita do fragmento malicioso; análise legítima ready. Revisão humana pendente. |
| dev-ambiguous-v4 | fail | `required-1` exige rule; confirmação do operador foi representada em requirement. |
| dev-branding-conflict-v4 | not-run | Conflito e pergunta de precedência preservados; revisão humana pendente. |
| dev-compatible-rules-v4 | fail | `required-2` (visibilidade exclusiva) e `required-4` (revisão/aprovação) exigem rule; foram representados em requirement. |
| dev-new-domain-v4 | not-run | Propósito de lanternas sensoriais preservado; revisão humana pendente. |
| dev-rules-a-v4 | not-run | Regra de aprovação necessária preservada; revisão humana pendente. |
| dev-rules-b-v4 | not-run | Permissão do autor sem terceiros preservada; revisão humana pendente. |
| dev-unread-assets-v4 | not-run | Obrigações e limitação do asset no artefato preservadas; revisão humana pendente. |

Nos casos com FAIL, os textos literais continuam presentes. A falha é sua
representação tipada: os vínculos de cobertura exigem o tipo aprovado, com a
relação de regra representada, não apenas uma frase em requisito. Não trocar
expectativas ou converter os outputs depois da observação para produzir PASS.

O auditor retornou suporte positivo para todos os 88 achados e 128 componentes,
sem omissões declaradas. Isso não eliminou as falhas do assessment. Tampouco
aprova a materialidade das perguntas: em `dev-ambiguous-v4`, `issue-2` pergunta
quem é o responsável com impacto `rule`. Recomendo reprovar sua materialidade
bloqueante nesta análise de intenção, preservando a obrigação de registrar
identidade e o bloqueio legítimo sobre condições de conclusão. Essa recomendação
ainda não é julgamento humano persistido.

## Revisão preparada e sequência

Pacote privado legível: `.factory/v4-development-campaign-po-review/po-review.md`,
com oito documentos, fontes, cobertura, achados, componentes e artefatos integrais.
Proposta pendente vinculada aos novos snapshots:

`03593bf1500e6a84cb88608523003734a3ade87be1970c4de2d2a3edf6cb2c1e`.

A proposta recomenda seis casos com seis critérios PASS; no ambíguo, FAIL de
cobertura e incerteza, demais quatro PASS; no compatível, FAIL de cobertura,
demais cinco PASS. Em regras B, “agente” é proposto como ator da ação, sem
alegar agente de IA ou equivalência com o responsável. O PO deve ler e julgar
estes novos outputs; aceites anteriores não são transferidos.

1. Registrar julgamento dos novos snapshots e vínculos após revisão do PO.
2. Refinar o incidente de representação tipada e de perguntas bloqueantes,
   preservando distinção entre obrigação normativa e relação de regra. A hipótese
   de causa no prompt/modelo ainda precisa de teste; esta rodada não a demonstra.
3. Preparar correção e verificações offline antes de qualquer novo pedido de
   inferência. Nenhum orçamento para correção ou nova rodada foi concedido aqui.
4. Comparar somente escopos representáveis e manter os gates independentes antes
   de qualificação, promoção ou treinamento. Desenvolvimento exposto não é holdout.

Sucesso de transporte não qualifica o modelo e não encerra AHC-021/022 ou Sprint 2.6.
