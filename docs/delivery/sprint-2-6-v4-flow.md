# Sprint 2.6 — integração offline do fluxo v4

Incremento: AHC-021, continuidade do diagnóstico e da ADR-0030.
Estado: implementação opt-in; Sprint e história continuam abertas.

O gerador v4 preserva requisitos normativos explícitos e rejeições de conteúdo.
A auditoria v5 verifica componentes e fontes exatas com autoridade consultiva.
A revisão humana v4 vincula os seis critérios ao snapshot, sem transportar
aprovações anteriores. O assessment conserva todas as falhas concorrentes.

O runner injetado valida pedido/autorização, expectativas e preflight antes da
fábrica; consome claim único e debita até duas invocações antes de chamar o gerador.
Para no primeiro erro e preserva análise válida quando a auditoria falha. Replay
offline verifica o journal; julgamento humano gera outro arquivo, sem alterar
resultado inicial. Falhas de I/O/interrupção podem deixar journal incompleto e
claim consumido: não existe retomada ou promessa de supervisor de produção.

Foram adicionadas 44 regressões sintéticas. Os testes verificam integridade,
isolamento dos payloads, limites e gates; não medem eficácia de um LLM. Os schemas
históricos, fontes congeladas, resultados reservados e defaults são preservados.
Não houve chamadas reais, reavaliação reservada, treinamento ou qualificação.

Próximos passos, em ordem de dependência:

1. Projetar e testar transporte supervisionado, incluindo deadline, limpeza e
   contagem observável de invocações. O limite injetado não controla requisições
   internas ou uma chamada bloqueada.
2. Congelar candidato/runner novos e preparar protocolo concreto de desenvolvimento,
   com conteúdo, destino, limites e nova autorização de orçamento.
3. Julgar novas respostas por snapshot; somente depois preparar outro reservado
   independente, com expectativas revisadas pelo PO antes da execução.
4. Consolidar evidências e submeter critérios/DoD à revisão de AHC-021/Sprint 2.6.

Não usar o corpus já exposto para alegar eficácia cega. Nenhum aceite de expectativa,
execução ou caso anterior aprova este candidato. A compilação permanece não autorizada.

Detalhes: [operação](../engineering/semantic-v4-flow.md) e
[ADR-0031](../adr/0031-semantic-v4-injected-flow.md).
