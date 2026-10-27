# ADR-0033 — Orçamento global para campanha semântica de desenvolvimento

Estado: implementação opt-in; validação local e CI registradas na entrega.

## Problema

O transporte da ADR-0032 limita um caso com duas etapas. O PO aprovou as novas
expectativas de oito casos, mas executar oito sessões isoladas não estabelece
um limite global de tempo e chamadas. O aceite das expectativas não autoriza
inferência. A compatibilidade anterior já foi demonstrada e julgada no seu escopo
isolado; a decisão de testar esse limite antes de ampliar a campanha foi cumprida.

## Decisão

Acrescentar uma fronteira opt-in de campanha, reutilizando extração, prompts,
fluxo v4 e supervisor de processos existentes. Não introduzir framework de agentes,
Temporal, concorrência ou novos defaults no compilador. O problema que exige
esta fronteira é a contabilidade global entre casos, ausente no runner unitário.

`SemanticCampaignRequest/v1` vincula de um a oito casos de desenvolvimento,
na ordem integral do manifesto revisado, uma rubrica/modelo, limites, programas,
fontes, comando fixo e versão Python. O teto é exatamente duas invocações por
caso, limitado a 16. Casos, runs e conteúdo dos projetos precisam ser distintos;
renomear um input não cria outro caso independente. O manifesto e os arquivos de
casos/rubrica são conferidos por conteúdo e hash. Dados não são instruções.

Uma nova `SemanticCampaignAuthorization/v1` precisa citar o hash exato desse
pedido. Sua declaração é projetada nos gates internos das etapas contidas no
pedido; não é um novo aceite humano nem reutilização do orçamento anterior.
Claims de campanha e de cada fluxo são exclusivos. Falha ou I/O incompleto
mantém o claim consumido, sem retomada automática.

O prazo monotônico começa antes dos gates de entrada e é compartilhado por todos
os workers. O supervisor recebe sempre o mesmo deadline; a concessão é o mínimo
entre limite por chamada e saldo global menos reserva de limpeza. Antes de outro
caso, saldo insuficiente interrompe a campanha. Antes de cada worker, conferir
novamente fontes e comando congelados. Cada tentativa tem débito global durável
antes da invocação, inclusive uma tentativa recusada pelo supervisor sem spawn.

Relatório global vincula a sequência de resultados, débitos, recibos e tempos.
Não continuar após falha técnica, interrupção ou resposta estruturalmente inválida.
Uma disposição de negócio `blocked` válida não é erro técnico. Semanticamente,
uma resposta ainda pode estar errada: sucesso de transporte não julga isso.
Todo assessment inicial permanece sem revisão humana; auditoria é consultiva.

Replay verifica pedido, autorização, claim, corpus, fontes efetivamente importadas,
ordem, payload por etapa, arquivos de débito/recibo e respostas privadas. Rejeita
arquivos extras de tentativa. O reporte não aceita ampliar prazo/chamadas,
reordenar casos ou apagar falhas para manter completed. Recibos não são assinados
e tempos declarados não constituem atestado independente de execução.

## Interrupção, histórico e limites

O supervisor existente usa `finally` para tentar encerrar seu grupo/job, inclusive
em `KeyboardInterrupt`. Se a interrupção não devolver recibo, a campanha registra
`cancelled`, sem inventar PID, reaping ou sucesso de limpeza. Testes de processos
locais verificam raiz e descendentes comuns; não cobrem todos os mecanismos do OS.
Interrupção fora da fronteira de transporte, kill do host ou falha de disco pode
deixar journal incompleto com claim consumido, sem relatório terminal. Não é uma
execução concluída ou recuperável automaticamente.

Mantêm-se os limites da ADR-0032: não é sandbox de segurança, ambiente hermético,
garantia de tempo real ou contabilização de requisições internas invisíveis do CLI.
I/O e escalonamento podem exceder o prazo; o resultado observado deve ser failed.
Fonte congelada não autentica dependências instaladas ou identidade remota.

Antes desta mudança, fontes e journals da compatibilidade 03 foram copiados para
replay privado congelado. Seu assessment inicial not-run e o PASS humano separado
continuam verificáveis com o pacote original. Pedidos históricos não recebem
hashes novos nem são reexecutados com a implementação atual.

O preparador offline `scripts/prepare_semantic_campaign.py` grava um pedido novo,
sem autorização, claims ou execução. O runner não é chamado pelos testes com
provedores reais nem pelo build padrão. Sem assets, reservado, treino ou promoção
de defaults. Julgar novas saídas, qualificar modelo e autorizar compilação são
gates separados. Esta implementação não encerra AHC-021/022 ou Sprint 2.6.
