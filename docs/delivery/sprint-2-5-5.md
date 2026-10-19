# Sprint 2.5.5 — Nexo: operações Scrum com evidências

Planejada em 2026-10-19 por pedido explícito do PO. Escopo autorizado para
estruturação; execução ainda não iniciada. Capacidade, datas e duração não foram
confirmadas. Proposta inicial de cinco dias úteis, sujeita a ajuste de escopo.

## Sprint Goal

Evoluir o Nexo existente para observar o estado de entrega, preparar decisões Scrum
e aplicar operações autorizadas com rastreabilidade. Reduzir trabalho administrativo
sem confundir relatório, atividade, incremento Done e aceite humano.

O PO ordena valor e backlog; Developers selecionam e adaptam o plano de execução.
O agente facilita e prepara evidências, sem assumir automaticamente responsabilidades
humanas. Referências: [acordo local](scrum.md) e [Scrum Guide](https://scrumguides.org/scrum-guide.html).

## Posição na esteira

Sprint 2.5 encerrada com carryover → **2.5.5 planejada** → 2.6 planejada.
AHC-021/022/023 continuam abertas e seus gates de semântica/qualificação permanecem.
A 2.5.5 inspeciona essas pendências; não as conclui por produzir um relatório.
AHC-024/025/026 continuam na 2.6. Não há capacidade paralela ou início automático.

## Backlog selecionado

| História | Entrega | Dependência |
|---|---|---|
| AHC-027 | Observador: contratos, coletores somente leitura, reconciliação e impedimentos | AHC-003/004 integradas |
| AHC-028 | Planejador: refinamento, planning, acompanhamento, review e propostas de retrospectiva | AHC-027 revisada |
| AHC-029 | Operador: autorização, journal, recibos e reconciliação de escritas limitadas | AHC-028 revisada |

Ordem obrigatória: observador → planejador → operador. Se capacidade não comportar
os três, renegociar com PO; não reduzir evidências ou segurança para aparentar entrega.
Não inclui fine-tuning, previsões com ML, dashboard, notificações contínuas ou geração
de times Scrum nos projetos alvo. Aproveita o adapter `team` sem acoplar o core a ele.

## Tarefas e verificação

1. **027-design:** definir `SprintSnapshot`, `DeliveryEvidence` e `Impediment`,
   identidade por projeto, freshness, estados desconhecidos e precedência por campo.
2. **027-implement:** coletar planejamento/DoD/memória local e snapshots GitHub por
   adapter substituível. Reconciliar sem apagar fontes divergentes.
3. **027-verify:** testar CI verde sem aceite semântico, PR merged com critério
   pendente, fonte stale, dependência aberta e acesso a projeto incorreto.
4. **027-review:** demo do estado da Sprint 2.5; cada conclusão aponta a evidência
   ou explicita que não foi possível verificá-la.
5. **028-design:** definir `ScrumActionProposal`, contexto requerido, alternativas,
   destinatário da decisão, budgets e separação entre regra e interpretação LLM.
6. **028-implement:** evoluir persona/ferramentas do Nexo; preparar refinamento,
   opções de escopo, resumo de impedimentos e review. Cache por hashes evita trabalho
   repetido; mudanças relevantes invalidam apenas contexto afetado.
7. **028-verify:** testar injeção, contexto insuficiente, memória superseded, falta
   de capacidade e tentativas de aprovar Done/iniciar sprint por relatório.
8. **028-review:** PO inspeciona propostas e fronteiras; nenhum aceite é inferido
   da simples execução do agente ou aprovação de seu relatório.
9. **029-design:** especificar operações permitidas, autorização por ação, revisão
   esperada, chave idempotente e estados prepared/authorized/attempted/observed/uncertain.
10. **029-implement:** journal transacional, recibos e aplicação pelo adapter GitHub;
    reconciliar antes de repetir uma ação cujo resultado remoto é incerto.
11. **029-verify:** simular crash antes/depois da escrita, replay, timeout, autorização
    stale, alteração concorrente, cancelamento e tentativa fora da allowlist.
12. **029-review:** conferir diff proposto e recibos; operação remota real somente
    com autorização específica e conferência do resultado. Fake não prova integração real.

TaskGraph gerado contém design → implement → verify → review de cada história,
com dependências entre histórias. Ele é plano observável, não executor, prazo ou
declaração de que as tarefas foram realizadas.

## Critérios de qualidade e eficiência

- Nenhum Done, aceite, cerimônia ou aprovação sem fonte verificável e escopo correto.
- Divergência ou dado ausente fica explícito; não inventar precedência ou conclusão.
- Proposta usa exatamente a revisão/snapshot inspecionados; mudança invalida sua base.
- Replay conserva recibo e não duplica efeitos; resultado remoto incerto requer
  reconciliação, sem promessa de exactly-once de uma API externa.
- Testes padrão offline; chamadas reais, secrets e rede ficam fora da suíte padrão.
- Contar chamadas, tokens quando observáveis, tempo e cache hit/miss; registrar
  desconhecido quando não medido. Comparar execução completa e incremental sob o
  mesmo fixture, sem prometer SLA ou economia antes da medição.
- Usar um agente e ferramentas determinísticas; LLM opcional para interpretação.
  Sem previsão de velocity, desempenho individual ou prazo a partir de poucos dados.

## Demo e Definition of Done

Input: snapshots da Sprint 2.5 com um PR integrado, CI verde e avaliação semântica
pendente. Saída esperada: fechamento parcial, histórias abertas, evidências citadas
e próxima decisão humana; nenhuma qualificação ou reunião fictícia. Depois simular
uma alteração autorizada e seu replay, preservando um único efeito e recibo.

Aplicar DoD local: critérios evidenciados, regressões, schemas quando houver novos
contratos, docs/memória, revisão, CI e PR integrado. Sprint Review reúne resultados
e pendências; retrospectiva propõe uma melhoria verificável. Nenhuma cerimônia está
agendada ou declarada realizada por este plano.
