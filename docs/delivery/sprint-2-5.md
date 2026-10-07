# Sprint 2.5 — Qualidade semântica e modelo adequado

Aberta por pedido explícito do PO em 2026-10-07. Foco autorizado: tornar o estudo
de projetos útil e confiável com o modelo/perfil adequado. Implementação das três
histórias ainda não entregue; abertura e plano não são evidência de conclusão.

## Sprint Goal

Produzir propostas de entendimento que extraiam regras de negócio, sustentem
conclusões nas fontes e preservem incerteza; qualificar modelo/perfil local por
evidência semântica e desempenho reproduzível. Se todos falharem, entregar uma
rejeição fundamentada e próximas mudanças, sem declarar um vencedor artificial.

AHC-019 continua em andamento. AHC-020 aguarda sua qualificação; Sprint 2 não foi
declarada concluída, cancelada ou revisada. Sprint 2.5 é a convenção local para um
foco intermediário no mesmo Product Goal; uma implementação ativa por executor.
Timebox proposto: cinco dias úteis, sem data de término ou capacidade prometida.
Datas/eventos/capacidade ainda precisam de alinhamento com o PO.

## Sprint Backlog

| História | Entrega | Dependência |
|---|---|---|
| AHC-021 | Rubrica, corpus versionado e runner de eval específico de entendimento | 002, 003, 004 integradas |
| AHC-022 | Pipeline/prompt com extração, grounding, cobertura e regressões | 021 |
| AHC-023 | Comparação e perfil qualificado por qualidade, energia e recursos | 022 |

Não antecipa o Simulation Lab completo de AHC-008 nem o Agent Factory. Core segue
generalista e provider-independent; datasets de categorias diferentes não criam
enum, switch ou catálogo de nichos suportados.

## Ordem e tarefas verificáveis

1. **021-01:** definir rubrica e expectativas revisáveis; manter critérios semânticos
   separados de checks de schema, integridade e testes do compilador.
2. **021-02:** preparar pelo menos 8 casos de desenvolvimento e 8 de holdout,
   incluindo novo domínio, regras A/B, conflito real, compatibilidade, ambiguidade,
   asset não lido e instruções adversariais. Congelar hashes/splits antes do tuning.
3. **021-03:** evoluir contratos de execução/julgamento, referências e budgets;
   erros e revisão pendente nunca viram pass. Regenerar schemas quando necessário.
4. **021-04:** implementar runner limitado e relatório; determinístico quando
   possível, revisão humana nos critérios de suporte semântico. Candidate-as-judge proibido.
5. **022-01:** reproduzir INC-0007 e analisar onde a extração e a análise se confundem.
6. **022-02:** desenhar extração → análise → verificação com outputs tipados e
   cobertura explícita; considerar cadeia de prompts somente se os evals justificarem.
7. **022-03:** implementar prompt versionado, verificação de regras/citações/assets
   e reparo limitado com stop conditions; manter original e hipóteses separados.
8. **022-04:** comparar baseline/candidato no desenvolvimento, congelar candidato
   antes de holdout e verificar regressões do compilador/contratos.
9. **023-01:** registrar energia, modelo, configuração, contexto e recursos; iniciar
   com os dois modelos 4B instalados, execução sequencial e contexto 8k.
10. **023-02:** comparar matriz modelo × prompt/estratégia × perfil; ao menos três
    repetições por caso/configuração de qualificação, com carga cold separada de warm.
    Configurações ajustadas são avaliadas no desenvolvimento; holdout só após congelamento.
11. **023-03:** executar holdout, revisar suporte/regras/conflitos e escolher perfil
    por qualidade primeiro. Expansão para modelos maiores exige justificativa de
    memória, licença e orçamento; não instalar catálogo indiscriminadamente.
12. **023-04:** relatório final, runbook, modelo/perfil ou rejeição e review com PO;
    resolver INC com evidência ou mantê-lo aberto, sem fabricar LES.

O TaskGraph gerado tem estágios design → implement → verify → review por história;
esta lista detalha ações, não resultados executados. PO aceita regras e significado;
colaborador/Codex implementa e coleta evidências. Personas internas apoiam sem
representar capacidade de developers nem delegação efetivamente executada.

## Gates de qualidade propostos

Antes de otimizar, revisar rubrica e expectativas. Para qualificação: 100% dos
contratos/referências estruturais válidos; nenhuma falha crítica de suporte, conflito
inventado, conteúdo de asset não lido ou aprovação indevida nos casos reservados;
100% das regras marcadas obrigatórias cobertas por saída rastreável e revisada.
Também revisar hipóteses e perguntas: uma citação existente não prova suporte.
Critérios ainda são proposta de refinamento, não thresholds já aprovados/executados.

Latência é critério secundário. Reportar mediana/dispersão e cold/warm, sem SLA
arbitrário ou comparação causal com ensaios anteriores de energia desconhecida.
Orçamento inicial proposto: uma chamada ativa, timeout máximo 180 s/chamada,
4096 tokens de saída e 8k de contexto. Ajustes de até 300 s e contextos maiores
exigem registrar motivo e consumo; nenhuma tentativa ou repair loop ilimitado.
Limitar cada sessão de avaliação a 30 chamadas ou 60 minutos; interromper e registrar
error/not-run ao atingir orçamento, sem fingir que a matriz inteira foi executada.

## Energia e piloto inicial

Leitura de abertura: PowerOnline=true, Charging=true, Discharging=false; Windows
no plano Desempenho Máximo. RTX 4050 6 GB, i7-13620H, RAM física 15,71 GiB.
Não alteramos power plan, overclock ou configurações globais. Limite de potência
da GPU foi reportado como N/A; não inventar TGP. Alimentação dos ensaios anteriores
não foi registrada, portanto não atribuir diferença de tempos exclusivamente à CA.

Piloto de três chamadas com Qwen3 Instruct e o prompt atual, mesmo input público,
uma cold e duas warm. Registrar energia/cache/RAM e resultados; piloto é preparação,
não corpus reservado nem prova de qualidade. Artefatos e resultados serão vinculados
sem modificar os ensaios anteriores. Desempenho maior não corrige falhas semânticas.

## Review e Done

Demo: input novo e regras divergentes → proposta fundamentada → findings → revisão
→ resultado de qualificação. Exibir também um caso rejeitado. PO confirma valor,
reordena backlog e decide retomada do blueprint; retrospectiva registra uma melhoria
verificável. Sem eventos agendados ou cerimônias anteriores declaradas realizadas.

Aplicar DoD de docs/delivery/scrum.md: critérios evidenciados, CI, revisão e PR
integrado, docs/schemas/memória atuais e análise de segurança/licença. Testes e
relatórios do próprio modelo não substituem aceite semântico. AHC-019 não vira
Done só porque Sprint 2.5 foi aberta ou um modelo foi instalado.
