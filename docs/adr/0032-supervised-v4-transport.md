# ADR-0032 — Transporte supervisionado para o fluxo v4

Estado: implementado e testado com workers locais sintéticos; inferência real pendente.

## Problema

ADR-0031 limitava invocações de um gerador injetado, mas não interrompia uma chamada
bloqueada nem vinculava prazo/limpeza a uma autorização nova. Threads isoladas não
permitem encerrar com segurança um gerador arbitrário bloqueado.

## Decisão

Manter o core de domínio e o fluxo injetado v4 intactos. Acrescentar contratos de
limites, pedido, autorização, recibo e relatório supervisionados, com fronteiras
de subprocessos e integração opt-in separadas. O worker padrão é código fixo do
repositório, executado por Python isolado (`-I`), e aceita uma única mensagem JSON.
Somente após recebê-la e validá-la importa o adapter Codex existente, sem alterar
seus controles de assinatura, tools, configuração, retries ou limites internos.

O supervisor estabelece a contenção antes de enviar o trabalho: Job Object no
Windows, sem breakaway e com encerramento ao fechar o handle; sessão/grupo próprio
em POSIX. Stdin/stdout têm limites; stderr é descartado. Prazo usa relógio monotônico,
com reserva de limpeza dentro da sessão. Não iniciar outro worker se a sessão já
não comporta essa reserva. Encerrar o grupo/job também após resposta válida evita
deixar descendentes cooperativos do worker rodando após sua saída.

Pedido novo vincula fluxo v4, limites, destino, comando do worker, versão Python e
snapshot de todos os `.py` do pacote, pyproject.toml e uv.lock. Validar também os
bytes do pacote efetivamente importado antes da construção do worker. Autorização
do pedido externo cobre explicitamente o fluxo aninhado e gera uma projeção técnica
para seu gate existente, preservando a mesma declaração humana. Uma autorização v4
anterior não autoriza esses novos limites/fontes/destino.

Claims externo e interno são exclusivos e consumidos antes da execução, sem retry,
fallback, repair ou retomada. Tentativa é persistida antes de lançar; recibo contém
hashes de comando/payload/resposta, prazo concedido, duração, PID, código de saída,
contenção, solicitação de encerramento e observação de reaping do processo raiz.
Rejeições antes do spawn têm PID ausente. Erro de transporte interrompe o fluxo.
Recibos preservam o erro primário e fatos de limpeza, sem mensagens privadas de OS/SDK.

Completed externo exige fluxo interno completo, todos os recibos bem-sucedidos e
prazo total observado dentro da sessão. Caso o prazo externo seja excedido depois
das etapas internas, preservar seu resultado técnico e registrar failed externo.
Replay verifica fontes, snapshots, autorização projetada, claims, tentativas,
recibos e respostas por hashes. Não chama provider nem julga significado.

## Limites

Este mecanismo supervisiona código de worker confiável; não é sandbox de segurança
ou garantia de tempo real. Criação de processo, I/O e escalonamento do OS não são
interrompíveis em todos os casos. Em POSIX, um descendente que abandona o grupo não
é coberto; a observação de reaping é da raiz, não de todos os descendentes. No
Windows, a contenção precisa ser estabelecida; falha de atribuição recusa o trabalho.
Os testes verificam descendentes comuns, não todos os mecanismos de criação do OS.

O snapshot não é ambiente hermético: não autentica o binário CLI, bibliotecas
instaladas ou identidade imutável do modelo remoto. Versão Python é declarada e
comparada, não hash completo do interpretador. Recibos não são atestado assinado.
Dois workers/invocações não equivalem ao número de requisições internas do provedor.
Crash/I/O pode deixar journal incompleto com claim consumido, sem recuperação
automática. Declarações humanas continuam não autenticadas.

Não houve inferência real nesta implementação, migração de casos, qualificação,
promoção de defaults ou encerramento de história/sprint. Próximo gate: protocolo
concreto e novo orçamento aprovado; compatibilidade real e eficácia continuam
desconhecidas. O reservado exposto não volta a ser evidência cega.

## Referências primárias consultadas

- [Microsoft: Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects): associação, descendentes e encerramento do job.
- [Python 3.12: subprocess](https://docs.python.org/3.12/library/subprocess.html): sessões, pipes, timeout e limites da criação de processos.
