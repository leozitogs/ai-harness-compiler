# AHC-022 — Análise com cobertura estrutural explícita

O modo grounded usa os átomos de GroundingExtraction/v1 para produzir uma proposta
e uma disposição rastreável para cada critério. O compilador continua generalista;
as três disposições são tipos de achados, não nichos de produto.

```sh
factory run-understanding-evals --corpus evals/understanding/v1 \
  --analysis-mode grounded --model ahc-qwen3:4b-instruct-8k \
  --case dev-compatible-rules dev-new-domain --max-attempts 1 \
  --session-seconds 300 --timeout-seconds 180 --context-tokens 8192 \
  --max-output-tokens 4096 --output output/new-grounded-session
factory validate-model-session output/new-grounded-session --corpus evals/understanding/v1
factory schema grounded-analysis
factory schema grounded-analysis-proposal
```

Sem a opção, o modo continua baseline. Modelo/hash devem ser explícitos na
qualificação; --expected-model-sha256 fixa a identidade esperada. Em grounded,
o SHA do programa também inclui os schemas. Não usar apenas o SHA do texto como
identidade do programa. Cada tentativa tem uma chamada, sem retries ou repair.

## Etapas executáveis

1. Preparar o snapshot canônico e extrair átomos determinísticos sem abrir assets.
2. Enviar extração ao adapter opcional; expectativas, evals e rubrica ficam fora da chamada.
3. Receber GroundedAnalysisProposal/v1 e validar referências, inventário e disposições.
4. Projetar a mesma proposta para ProjectUnderstanding/v1 e executar o eval existente.
5. Registrar análise, observações, estados e casos não executados no journal.

Core: GroundedAnalysisModel é um Protocol; analyze_project faz uma chamada sobre
cópia independente e revalida o resultado contra o input original. HTTP/subprocessos
permanecem nas fronteiras existentes. Geração supervisionada verifica a identidade
observada do modelo, hash do programa e budgets antes de aceitar o resultado.

## O que os checks estabelecem

Uma regra vinculada preserva a citação e a fonte. Um requisito vinculado aponta
statement declarado de capacidade/restrição. Uma dúvida aponta pergunta bloqueante.
Inventários omitidos, referências trocadas, achados incompatíveis e alegações de
execução grounded sem análise válida são rejeitados.

Os checks não estabelecem que a condição/resultado estejam corretos, que um
requisito seja de fato uma regra, ou que uma pergunta seja necessária. Isso exige
julgamento semântico separado. semantic_status/model_qualification não mudam para
pass. O modelo não aprova sua saída, o harness ou a rubrica.

## Diagnósticos e evidências reais

Erros de inventário/vínculo são códigos fixos: criterion-inventory-invalid,
criterion-rule-link-invalid, criterion-requirement-link-invalid,
criterion-question-link-invalid e excluded-source-used. Erros de schema/suporte
geral usam grounded-output-invalid/grounded-analysis-invalid; limites e falhas do
adapter têm códigos de fase. Nunca registrar texto livre do erro/provider.

Dois smokes preservados em docs/evidence/ahc-022-grounded-*-20261008 selecionaram
dev-compatible-rules e dev-new-domain, max_attempts=1, timeout=180 s, sessão=300 s,
8k de contexto e saída de até 4096 tokens, com SHA esperado do Qwen3 Instruct fixo.

O primeiro terminou em 23,603 s com provider-or-metadata-error. Esse código genérico
não permite determinar a causa específica. Depois da inclusão dos diagnósticos,
o segundo terminou em 14,665 s com criterion-rule-link-invalid: uma disposição
de regra não satisfez o vínculo com regra extraída/citação/fonte daquele critério.
O código não identifica qual componente do vínculo falhou.

Ambos têm geração inválida, evaluation=null, avaliação da sessão error e segundo
caso not-run por budget. Os journals passaram na validação. Não há proposta aceita
ou conteúdo privado do provider persistido. Uma falha no contrato não equivale a
uma revisão semântica executada. Tempos são de tentativas únicas com estado de
cache não controlado, sem ranking ou inferência causal sobre desempenho.

Alimentação observada antes do primeiro smoke: PowerOnline=true, Charging=true,
Discharging=false. Sem alteração de plano de energia. Modelo esperado:
59d7f50962ef280aacad2867d041c13e22ad2d08827df5ec407ff75d348f8c90.

## Próximos incrementos

Revisão semântica da rubrica/expectativas, comparação do development e repair
limitado com diagnóstico tipado. Depois, congelar candidato antes do holdout e
qualificar com repetições, energia e recursos. O smoke deste incremento verifica
somente o caminho de execução; não mede superioridade do modelo ou do programa.
