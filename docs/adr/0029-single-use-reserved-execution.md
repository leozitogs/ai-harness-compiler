# ADR-0029 — Execução reservada com autorização de uso único

Estado: implementado para verificação offline em 21/10/2026; execução real ainda
depende de autorização específica. Complementa ADR-0028, sem mudar o candidato.

## Decisão

`ReservedRunRequest/v1` vincula protocolo revisado, orçamento, perfil solicitado,
fontes selecionadas do candidato, fontes do executor, rubrica e diretório privado
de resultados. O contrato rejeita perfis/fingerprints divergentes do congelamento,
caminhos não normalizados, fontes fora do pacote e saídas fora de `.factory/`.
Preparação lê somente metadados e fontes públicas; não abre casos reservados.

`ReservedRunAuthorization/v1` é uma declaração humana local vinculada ao digest
exato do pedido. Aprovação das expectativas não satisfaz essa autorização. Alterar
orçamento, perfil, código, casos ou saída altera o pedido e invalida a declaração.
O autor do candidato, curador e identificador do modelo solicitado não podem ser
o ator declarado da autorização. Identidade continua sem autenticação.

O executor confere autorização e fontes antes de abrir casos, incluindo os bytes
do pacote Python efetivamente importado. Um arquivo exclusivo por digest do pedido,
com flush/fsync, consome a autorização antes do preflight privado. Ele não é
removido nem após falha sem chamadas. A saída deve ser nova. Não há resume ou retry
automático: falha ou interrupção exige reconciliação e nova decisão do PO.

Após o claim, a fronteira verifica todos os casos, hashes de bytes/snapshot/input/
clone renomeado, ids e rubrica antes da primeira chamada. Não lê assets. Copia bytes
originais para resultados privados. O modelo recebe somente fontes do projeto;
expectativas e campos de aprovação não entram no payload. Cada caso/repetição tem
uma análise v3.4 e uma auditoria v4.1, sem promover defaults históricos.

Cada invocação é debitada no recibo persistido antes do provider, inclusive falhas.
Isso mede invocações cobradas pelo host; `provider_calls_observed` é desconhecido,
não zero nem uma medição de requests internos do serviço. Recibos conservam hashes
de prompt, schema lógico/efetivo e resposta final; raciocínio privado e prompts
brutos não são gravados. Resposta final inválida é preservada. A primeira falha
interrompe chamadas seguintes, que permanecem `not-run`.

O adapter congelado aplica o timeout do subprocesso e ferramentas desabilitadas.
O host verifica prazo antes da invocação e rejeita conclusão tardia. Há reserva de
20s de limpeza por chamada dentro do limite da sessão; não inicia nova chamada
sem margem para timeout + limpeza. Prazo é limite operacional, sem garantia de
tempo real do SO. Encerramento abrupto pode deixar operação remota incerta; o claim
continua consumido, e recibo incompleto não vira sucesso ou autorização de retry.

## Evidência e autoridade

`ReservedRunReport/v1` exige todos os slots planejados em ordem, contabilização
exata, dependência da auditoria no snapshot da análise, e estado compatível com
falhas/prazos. Conclusão estrutural continua com semântica/qualificação não
estabelecidas e compilação não autorizada. Replay offline verifica arquivos,
recibos, schema/prompt/programa e reconstrói artefatos das respostas salvas sem LLM.

`ReservedSemanticAssessment/v1` resolve explicitamente a aprovação externa das
expectativas, mantendo o `AssessmentCase/v2` original e seu hash. Encapsula a
avaliação v3 original, que pode continuar `not-run` por ter aprovação inline nula.
Somente nova revisão humana completa das saídas, com suporte por componente e
rubrica aprovada, pode produzir `pass` no wrapper reservado. Parecer do auditor
nunca se converte em revisão humana. O CLI mantém avaliações dentro da pasta
privada e não muda os formatos históricos ou suas regras de aceite.

O wrapper conserva também os bytes JSON da rubrica: recalcula o hash bruto e
confere igualdade com a rubrica interpretada no assessment original. Declarar um
hash correto junto de conteúdo alterado não satisfaz esse vínculo. Motivo de
parada deve coincidir com a primeira falha e os slots seguintes não executados.

## Limites

Implementação CLI atual usa o adapter opcional Codex via assinatura; contrato do
domínio e transformações continuam independentes de frameworks. Fonte congelada
é inventário selecionado, não todo o ambiente/CLI remoto. Modelo imutável, sampler,
custo e telemetria continuam desconhecidos; não completamos AHC-024 por inferência.
Não há autenticação criptográfica, isolamento por filesystem entre agentes ou
garantia contra proprietário do filesystem que fabrique todas as declarações.
Hashes/recibos demonstram consistência local, não observação independente do serviço.

O claim protege o pedido exato. Outro pedido não reutiliza sua autorização; o
operador humano pode autorizar novo escopo, cuja independência precisa de revisão.
Nenhum resultado reservado pode ser usado para ajustar o candidato e continuar
chamando o mesmo conjunto como se permanecesse não exposto.
