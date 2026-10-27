# Sprint 2.6 — pedido final de compatibilidade v4/v5

Data: 2026-10-27. Expectativas aprovadas pelo PO; execução ainda não autorizada.

O PO respondeu **“Aprovo as cinco expectativas deste caso”** à revisão do caso
`compat-catalog-v4-01`, vinculada ao snapshot original
`a58d18d54a4deb13dec413223541e723794134e151d88d4c253f60abbd5aa0ca`.
O aceite cobre análise ready, identidade e origem como obrigações, aprovação do
revisor como condição necessária para publicar e rejeição explícita apenas do
fragmento malicioso. Preserva os limites de papéis, condições e domínio descritos
na [proposta original](sprint-2-6-v4-compatibility-proposal.md).

Preservamos os arquivos da proposta sem alterações. O novo
[caso revisado](../../evals/understanding/v4/compatibility-reviewed/case.json)
difere do original exclusivamente pelo campo `expectations_approval`.
O [registro da decisão](../../evals/understanding/v4/compatibility-reviewed/expectations-decision.json)
vincula pergunta, resposta, documento e ambos os snapshots. A declaração humana
registra o aceite recebido no chat; não é autenticação criptográfica do PO.

Novo snapshot do caso:
`46d173dc08b91833cb7cc9488bffee354e9f3dc7fb4bee885e80a920f98adb65`.

## Pedido sujeito a autorização específica

O [request final](../../evals/understanding/v4/compatibility-reviewed/request.json)
tem SHA256 canônico:

`2e8963f18cb88f2dc7d70e737a0bafe8872b822a149c6f1985c66e48ae2f60cd`.

| Campo | Escopo exato |
| --- | --- |
| Objetivo | Observar compatibilidade dos schemas de análise v4 e auditoria v5 no provedor |
| Caso | Um caso público sintético, com as cinco expectativas aprovadas |
| Etapas | Uma análise; depois uma auditoria da análise válida |
| Destino | Assinatura ChatGPT por Codex CLI, sem API paga por chave |
| Modelo solicitado | `gpt-6.1-sol`, sem fallback ou mudança de default |
| Máximo | Duas invocações sequenciais do adapter/worker |
| Chamada | Até 180 segundos, também limitada pelo saldo da sessão |
| Limpeza | Reserva de até 20 segundos por etapa, dentro da sessão |
| Sessão | Até 400 segundos, sem garantia de tempo real do sistema operacional |
| Entrada/saída por worker | Até 1 MiB / 4 MiB |
| Parada | Primeira falha técnica; sem retry, repair, fallback ou retomada |
| Envio | Somente fontes públicas do caso; para auditoria, também a análise gerada |
| Excluído do envio | Expectativas, rubrica, julgamentos, assets e corpus reservado |
| Outras exclusões | Ferramentas, web, treinamento, API por chave e alteração de defaults |
| Identidade da rodada | `compat-v4-catalog-20261027-02` |
| Saída privada externa | `.factory/supervised-v4-runs/compat-v4-catalog-20261027-02/` |

O journal privado interno continua separado em
`.factory/semantic-v4-runs/compat-v4-catalog-20261027-02/`.
O runner exige autorização nova do hash exato antes de criar claims ou workers.
Não existe arquivo de autorização de execução neste incremento. O hash da
proposta anterior não serve para autorizar este request.

O request mantém os mesmos programas, rubrica, limites, 101 fontes congeladas,
runtime Python e comando fixo da proposta; muda o caso revisado e a identidade da
rodada. Base do preparo: `086ae26be76b0380dfe0a543e3e1d21c08ae6d9b`.
Conferimos as fontes e o pacote importado localmente. Nenhum schema ou código de
produção mudou. O preflight do novo snapshot permanece compatível.

O freeze não torna o ambiente hermético nem autentica o modelo remoto. O limite
de duas invocações não conta eventuais requisições internas da CLI. O programa
lógico da auditoria está vinculado; prompt/schema dinâmicos dependem da análise
que ainda não existe e terão seus hashes preservados na execução.

## Dependências e verificação

| Trabalho | Dependência | Verificação |
| --- | --- | --- |
| Registrar aceite | Resposta explícita do PO | Nova declaração vinculada ao snapshot original; inputs/expectativas idênticos |
| Congelar pedido | Caso revisado | Programas/fontes/runtime/comando/limites conferidos; nenhuma chamada |
| Autorizar execução | Pedido final revisável | Aceite específico deste hash, conteúdo, destino e limites; ainda pendente |
| Executar | Autorização exata e gates locais | Débitos antes das etapas, contenção, recibos, uso único e parada na falha |
| Revisar | Rodada encerrada | Replay offline e julgamento humano novo dos seis critérios |
| Planejar avaliação maior | Evidência revisada | Protocolo e orçamento próprios; não ampliar esta rodada |

Compatibilidade técnica não estabelece qualidade semântica. O aceite recebido não
aprova outputs inexistentes, qualifica o modelo, permite compilação ou encerra a
Sprint 2.6. Falhas e pareceres negativos serão preservados, sem tentativa automática
de obter um resultado positivo. Os
[metadados revisados](../../evals/understanding/v4/compatibility-reviewed/protocol.json)
registram expectativas aprovadas, execução não autorizada e zero chamadas.
