# AHC-028 — Incremento de propostas do Nexo

2026-10-19. Execução autorizada pelo PO após o observador AHC-027. Contratos e
ferramenta procedural produzem refinamento, planejamento e review com objetivo,
critérios, dependências, alternativas, destinatários e evidências preservados.
O estado da história permanece em revisão, sem aceite humano presumido.

LangGraph reutiliza Nexo e suas três ferramentas permitidas. O gate persistente
continua exigindo decisão humana e passa a rejeitar fontes dinâmicas da sprint
alteradas ou vencidas. A aprovação de relatório não inicia sprint nem aceita
histórias. AHC-029 continua planejada para operações autorizadas e journal.

Regressões cobrem adulteração de critérios/objetivo/dependências/referências,
tentativa de autoaprovação no input, manifesto normalizado forjado, mudança nos
cinco arquivos locais, TTL, cache, execução dedicada ao Nexo e retomada do gate.
Testes permanecem offline, sem credenciais ou chamadas de modelo.

O cache evita reconstrução idêntica dentro da sessão, com invalidação completa.
Não há cache persistente nem invalidação parcial por história. Não afirmamos
eficiência de inferência, qualificação de modelo ou ganho de qualidade semântica.
Capacidade e previsão continuam desconhecidas. A revisão semântica da Sprint 2.5
permanece pendente, mesmo com PR integrado e CI verde.

## Demonstração observada

[Captura e inventário](../evidence/ahc-028-nexo-20261019/inventory.json): uma sessão
local executou somente Nexo, três ferramentas e cinco propostas (três refinamentos,
planning e review). A coleta explícita anterior fez quatro leituras GitHub para
issues 15/16/17 e PR 40 compartilhado. Zero chamadas de modelo e zero escritas remotas.
O relatório ficou `awaiting_po`, com `approval=null`, objetivo declarado
`not-achieved`, carryover e aceite `not-established` preservados.

O artefato é histórico: atualizar o índice de memória para documentá-lo invalida
sua revisão futura, como deve ocorrer. Recoletar fontes antes de outra sessão.
A métrica ML embutida é o pequeno holdout legado do roteador, sem validade como
performance de produção ou qualidade do planejamento Scrum.

O cache tem regressão com contador real: duas leituras idênticas geram uma proposta;
mudar o digest causa a segunda geração. A resposta devolvida não pode alterar o
JSON interno do cache. Não medimos ganho de latência ou tokens nesta demonstração.


## Verificação final

857 testes passaram, sem skips, com todos os extras: 26 regressões novas da AHC-028.
Lint, formatação, mypy, schemas e quatro planos gerados passaram. O gate também
rejeita substituição do snapshot no run.json: o digest da observação está vinculado
separadamente ao checkpoint. Erros de TeamRun omitem conteúdo capturado dos inputs.
A revisão e CI do PR completam o fluxo de integração; não equivalem a aceite do PO.
