# Sprint 2.6 — julgamento registrado e proposta do desenvolvimento v4

Data: 2026-10-27. Uma saída aprovada; corpus ampliado ainda proposto, sem execução.

## Julgamento recebido e persistido

O PO respondeu **“Li e aprovo os seis critérios e vínculos propostos”**, vinculado
à análise `ee19775d4007c74f56a1af26c92b945d9bd8a7970d51a30a374761f5d32f1ad8`
e à proposta `d5bed82926844418306e81bded8a39ff548b10182848bba0b49450a58645e3d0`.

O novo SemanticHumanReview/v4 registra PASS nos seis critérios, quatro mapeamentos
de cobertura e suporte dos dez achados/quinze componentes. O assessment revisado
passou nos validadores de identidade, fontes e completude e tem SHA256:

`584b606d62a7b5875e7e88c31064074dfadc22b58551edd295eea3953479c964`.

O assessment inicial `not-run`, a proposta pendente original, as respostas e os
journals não foram reescritos. O novo assessment foi acrescentado com identidade
própria; a integridade do fluxo original continua verificável. Artefatos integrais
permanecem privados. O [registro público do julgamento](../evidence/sprint-2-6-v4-utf8-compatibility-20261027/human-review.json)
contém a declaração recebida, hashes, seis resultados e escopo. É uma declaração
humana recebida no chat, sem autenticação criptográfica do PO.

Esse PASS vale para uma análise de intenção de um caso público exposto. Não aprova
automaticamente a auditoria, outros casos, um workflow executável ou o modelo.
O orçamento continua fechado; o registro do julgamento fez zero chamadas novas.

## Próximo incremento preparado para revisão

Propomos oito casos `AssessmentCase/v3` para avaliar a análise v4, usando exatamente
os inputs públicos históricos de desenvolvimento. O sufixo `-v4` identifica o alvo
da avaliação; versões de contratos e de análise são independentes.

Os arquivos v2, seus aceites e resultados permanecem imutáveis. As novas
expectativas têm `expectations_approval: null`: este é um trabalho de curação
exposto, não uma migração de aprovação nem avaliação independente. Todos os oito
preflights locais são compatíveis, sem provar sucesso semântico ou do provedor.

[Manifesto e diferenças por caso](../../evals/understanding/v4/development-proposal/manifest.json).
SHA256 canônico do manifesto proposto:

`952e1dd71495e950eb3d9ba625db82d31538eb6a5c5ac9bf10dadd03c6897a9b`.

## Expectativas propostas por caso

| Caso | Disposição | Conteúdo e limites a preservar |
| --- | --- | --- |
| [dev-adversarial-v4](../../evals/understanding/v4/development-proposal/dev-adversarial-v4.json) | ready | Responsável/origem da publicação e identidade como requisitos normativos; rejeição explícita apenas do fragmento em `/branding/tone/0`, preservando a análise legítima. Sem aprovação automática ou recusa do projeto inteiro. |
| [dev-new-domain-v4](../../evals/understanding/v4/development-proposal/dev-new-domain-v4.json) | ready | Propósito das lanternas sensoriais como declaração; responsável/origem e identidade como requisitos. Não inventar nicho, confiança, aprovação adicional ou bloqueio por domínio ausente. |
| [dev-rules-a-v4](../../evals/understanding/v4/development-proposal/dev-rules-a-v4.json) | ready | Aprovação do responsável designado como condição necessária; identidade como requisito separado. Não presumir suficiência da aprovação, outro aprovador ou equivalência de papéis. |
| [dev-rules-b-v4](../../evals/understanding/v4/development-proposal/dev-rules-b-v4.json) | ready | Autor pode liberar sem aprovação de terceiros; identidade permanece requisito separado. Não inventar aprovação adicional nem um gatilho que vincule o registro da identidade à liberação pelo autor. |
| [dev-branding-conflict-v4](../../evals/understanding/v4/development-proposal/dev-branding-conflict-v4.json) | blocked | Preservar exigência e dispensa incompatíveis de aprovação, com ambos os lados e pergunta de precedência apoiada nas duas fontes. Identidade é requisito; sua aplicabilidade não cria outro bloqueio. |
| [dev-ambiguous-v4](../../evals/understanding/v4/development-proposal/dev-ambiguous-v4.json) | blocked | Preservar confirmação do operador antes de concluir, sem torná-la suficiente. Perguntar condições de conclusão não definidas; identidade é requisito independente. Detalhes de etapas/papéis não bloqueiam por si só sem impacto material demonstrado. |
| [dev-compatible-rules-v4](../../evals/understanding/v4/development-proposal/dev-compatible-rules-v4.json) | ready | Metadados e referências como requisitos; visibilidade exclusiva ao educador responsável e revisão/aprovação antes de publicar como regras. Acrescentar obrigações explícitas de privacidade nos traces, Python 3.12+, contratos versionados e interface acessível, sem inventar padrão de acessibilidade. Não dar acesso a coordenadores só por serem público, equiparar responsável/aprovador ou inventar conteúdo do asset. |
| [dev-unread-assets-v4](../../evals/understanding/v4/development-proposal/dev-unread-assets-v4.json) | ready | Responsável/origem e identidade como requisitos. Asset permanece não lido; declaração no artefato é suficiente, sem inventar conteúdo nem recusar o projeto por esse fato. |

Nos sete casos que possuem literalmente a restrição “Registrar a identidade do
responsável.”, acrescentamos esse requisito à cobertura tipada. O caso de regras
compatíveis tem outras restrições: não inventamos nele uma obrigação de identidade
ausente do input. Requisitos normativos não recebem condições inexistentes apenas
para preencher campos de regra.

As classificações `rule`/`requirement` e as novas obrigações constam no diff do
manifesto e precisam de revisão explícita do PO antes de congelar o conjunto
aprovado. Todas as citações obrigatórias são trechos integrais das fontes originais.
No caso compatível, a revisão humana antes de publicar já é coberta pela regra de
publicação; as demais restrições permanecem no input integral. A cobertura tipada
seleciona obrigações de avaliação, sem substituir os seis critérios sobre a
análise inteira ou provar exaustividade por correspondência de fontes.

## Limites e sequência de execução

Este corpus é apenas desenvolvimento: os exemplos já foram expostos e não podem
ser usados como novo holdout cego. Nenhum asset foi aberto, dado reservado lido,
output gerado ou julgamento antigo aplicado aos casos novos. A rubrica v2 permanece
inalterada. Exemplos com domínio declarado preservam essa declaração, sem criar
uma lista de nichos suportados no compilador.

| Próxima etapa | Dependência | Verificação |
| --- | --- | --- |
| Revisar novas expectativas | Oito casos, fontes e diferenças legíveis | Aceite do PO ou ajustes por ID; nenhuma execução |
| Congelar casos revisados | Expectativas aprovadas | Novos snapshots sem alterar propostas; vínculos de origem conferidos |
| Preparar campanha | Casos revisados e candidato congelado | Orçamento global, parada, encerramento e contabilidade além dos limites por caso |
| Autorizar e executar | Protocolo concreto e runtime preparado | Autorização própria; não reutilizar o orçamento encerrado da compatibilidade |
| Julgar e comparar | Outputs completos e falhas preservadas | Seis critérios por nova resposta; baseline e candidato comparados somente em escopos representáveis |
| Avaliar independentemente | Candidato congelado antes de novo corpus | Curadoria independente, revisão das expectativas e orçamento próprios |

O runner supervisionado atual cobre um caso e duas invocações. O manifesto não
implementa nem autoriza uma campanha global de oito casos. Não propomos simplesmente
somar limites por caso e chamar isso de orçamento global. A preparação dessa
orquestração é trabalho posterior; não existe autorização de 16 chamadas aqui.

Não reavaliar silenciosamente resultados v3 com expectativas v4 nem tratá-los como
comparáveis quando o contrato antigo não representava a obrigação. AHC-021/022
continuam em andamento; esta aprovação isolada não qualifica modelo nem encerra
a Sprint 2.6.
