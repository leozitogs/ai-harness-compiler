# Sprint 2.6 — controlador global e pedido da campanha v4

Data: 2026-10-27. Implementação offline; pedido aguardando autorização específica.

## Incremento

Implementado o controle global previsto em C1–C4 do
[plano anterior](sprint-2-6-v4-development-approved.md). A fronteira opt-in
`semantic_campaign.py` compartilha prazo e teto entre casos, persiste débitos antes
das invocações, recusa reutilização e interrompe na primeira falha técnica.
Reutiliza o supervisor de processos existente e mantém os fluxos históricos intactos.
Os contratos, as invariantes e os limites estão na
[ADR-0033](../adr/0033-global-semantic-campaign.md).

O preparador `scripts/prepare_semantic_campaign.py` só verifica fontes públicas e
grava um pedido novo. Não recebe autorização nem contém caminho de execução.
O runner callable `run_campaign` exige autorização tipada vinculada ao hash exato.
Ele não é chamado pelo build ou pelos testes com provedores reais.

## Pedido concreto preparado — C5

[Pedido completo](../../evals/understanding/v4/development-campaign/request.json) ·
[protocolo e limites](../../evals/understanding/v4/development-campaign/protocol.json).

SHA256 canônico do pedido `SemanticCampaignRequest/v1`:

`a64cb6e7a779d4c5c201db9beb54238e793604fc564eb963b3987e37ffd88236`.

Vincula o corpus revisado `8f666df6`, os oito snapshots com expectativas
explicitamente aprovadas pelo PO, rubrica v2, programas de análise v4/auditoria v5,
103 arquivos de implementação/configuração, comando fixo e versão Python local.
A ordem é a do manifesto. Casos de desenvolvimento são expostos, sem alegação
de avaliação independente. O pedido registra o modelo solicitado, sem autenticar
a identidade imutável do serviço remoto.

| Limite | Valor proposto no pedido |
| --- | --- |
| Invocações controladas pelo harness | Até 16, sequenciais; duas por caso |
| Sessão global | Até 3.600 s, contados antes dos gates de entrada |
| Chamada | Até 180 s, reduzida conforme saldo global |
| Limpeza | Reserva de até 20 s por etapa dentro do prazo global |
| Entrada/saída de worker | 1 MiB / 4 MiB |
| Destino | Assinatura ChatGPT/Codex CLI, `gpt-6.1-sol` solicitado |
| Parada | Primeira falha técnica; sem retry, repair, fallback ou retomada |

Somente fontes públicas do projeto são enviadas à análise; sua auditoria também
recebe a análise gerada. Expectativas, rubrica, julgamentos, conteúdo de assets e
reservado não são enviados. Não habilitar ferramentas, web, API paga por chave,
treino ou mudanças de defaults. Dados retornados continuam não confiáveis.

Journals ficam em `.factory/semantic-v4-campaigns/dev-v4-20261027-01/`, com fluxos
aninhados privados em `.factory/semantic-v4-runs/dev-v4-20261027-01-01/` até `-08/`.
Nenhum desses runs foi criado por esta preparação. Cada invocação contabilizada
pode falhar antes de spawn; não equiparar o teto às requisições internas do CLI.
Falha estrutural encerra a campanha; disposição de negócio `blocked` válida não.

O pedido não contém `authorization.json` e não concede execução. O aceite das oito
expectativas e os orçamentos encerrados da compatibilidade não satisfazem
`SemanticCampaignAuthorization/v1`. C6 só pode começar após um novo aceite explícito
do conteúdo, destino, limites e hash acima, com CI e revisão do incremento concluídas.

## Verificação e limites de evidência

Testes sintéticos verificam oito casos/16 débitos sob o mesmo deadline; prazo
esgotado antes do primeiro caso e entre casos; falha na auditoria; interrupção;
overflow; fonte alterada entre etapas; hashes/corpus/autorização divergentes;
duplicatas e clones renomeados; contabilidade contraditória; artefatos extras;
e I/O incompleto sem retomada. Workers locais reais verificam integração,
contenção/reaping e interrupção com descendente comum. Sem chamadas ao modelo.

Replay anterior preservado em cópia privada com fontes originais: assessment
inicial not-run e PASS humano separado continuam verificáveis. A implementação
nova não altera pedidos históricos para fazê-los aceitar fontes diferentes.
Recibos e tempos não são atestados assinados; seguem os limites do supervisor
quanto a OS, contenção, bibliotecas instaladas e tempo real.

Uma execução técnica bem-sucedida produzirá assessments iniciais sem aceite
humano. As novas respostas ainda precisarão de julgamento por critério, seguido
da comparação nos escopos representáveis e dos gates independentes restantes.
Não houve nova inferência, qualificação, autorização de compilação ou encerramento
de AHC-021/022 ou da Sprint 2.6 neste incremento.
