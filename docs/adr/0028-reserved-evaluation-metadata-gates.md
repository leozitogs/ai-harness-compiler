# ADR-0028 — Preparação reservada por metadados e curadoria separada

Estado: implementado em 21/10/2026 no escopo autorizado de preparação. A escolha
do PO foi curadoria por agente independente em contexto isolado, seguida de sua
revisão; essa escolha não aprova expectativas ou execução.

## Contexto e decisão

O desenvolvimento v2 tem expectativas aprovadas, mas o reservado v1 não foi
migrado nem revisado sob os contratos atuais. Reutilizar falhas de desenvolvimento
como reservado comprometeria a separação. Antes da curadoria, congelamos commit,
fontes selecionadas, composição v3.4, auditoria v4.1 e configuração solicitada do
provedor. O congelamento é parcial: alias solicitado não é digest imutável do
modelo e não completa AHC-024.

`ReservedEvaluationProtocol/v1` representa identidades, famílias declaradas,
cenários e fingerprints dos dois conjuntos, rubrica, candidato, revisão e proposta
de orçamento. `ReservedPreparationReport/v1` recalcula hash, gates e estado na
desserialização. Contratos puros não abrem arquivos nem importam provedores.
O CLI lê somente um protocolo de até 2 MiB, cria relatório novo e nunca segue os
caminhos dos casos. Não altera comandos existentes de execução.

A curadoria recebe contexto novo, sem histórico da conversa, exemplos, respostas
ou reservado anterior. Os inputs e expectativas ficam em `.factory/`, fora do
Git; o autor do candidato recebe somente metadados e proveniência declarada. O
PO recebe o documento completo para revisão. A tarefa do agente é geração de
casos autorizada, não avaliação do candidato, nem aprovação humana simulada.

Os gates verificam declaração de curadoria cega distinta do autor do candidato,
vínculo ao candidato congelado, presença do desenvolvimento, pelo menos oito
reservados cobrindo sete cenários (dois de regras contrastantes), duplicação e
sobreposição de identidades/famílias/fingerprints, revisão humana vinculada ao
corpus e orçamento exato de geração + auditoria por caso/repetição. Orçamento
permite apenas execução sequencial, sem retry ou repair. Todos os seis critérios
continuam exigidos; nenhuma média compensa falha crítica.

## Limites e consequências

`reviewable` significa apenas metadados preparados. `payload_validation` permanece
`not-performed`, `identity_authentication` permanece `not-established`,
`execution_authorized` é sempre falso e `model_calls` é zero. Esses campos não
resumem a chamada do agente curador; referem-se ao preparo e à avaliação runtime.
Um arquivo pode declarar digests falsos; este comando não verifica payloads.
Famílias e identidade são declarações, e o digest sem id/nome detecta clones
renomeados, não paráfrases ou vazamento semântico. Isolamento de contexto e
allowlist são instruções operacionais, sem sandbox independente por agente ou
garantia sobre dados de pré-treinamento.

A revisão humana é uma declaração local vinculada ao corpus, sem autenticação.
Mudanças nos casos, rubrica ou vínculo do candidato exigem nova revisão. Mudanças
na receita exigem novo congelamento e conferência do vínculo, sem reutilizar o
reservado para ajuste. Nenhum leitor/runner reservado foi acrescentado: acesso,
verificação de bytes/contratos na fronteira, autorização concreta de conteúdo,
destino e orçamento, execução e julgamento de saídas são etapas posteriores.

## Compatibilidade e validação

Dois novos contratos e um comando aditivos; defaults de composição/auditoria e
formatos históricos permanecem iguais. Testes sintéticos exercitam contradições,
gates, alteração de candidato, clones declarados, relatórios adulterados, limite
de leitura e proteção contra sobrescrita. São testes do compilador, não resultados
do modelo ou aceite de AHC-021/022.
