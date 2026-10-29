# Sprint 2.6 — aceite humano do desenvolvimento v4.2

Em 28/10/2026, o PO declarou ter lido e aprovou os seis critérios e os vínculos
das seis novas respostas ready e das duas blocked. Decisões específicas:
`call_dbd920ce0de347a6a3d2bd9eaac05981`, itens 0 e 1. Proposta exata:

`1b816c0c34a382527f615e57483d0a74a849a1b1926e09c56ae6a1df46a64052`.

Os oito novos assessments são **PASS**: **48 critérios PASS, zero FAIL e zero
pendentes** nesta rodada. Foram confirmados 24 vínculos de cobertura, 77 achados
e 110 componentes. As seis análises ready e duas blocked preservam a disposição
legítima; aprovar uma análise blocked não libera o projeto para compilar.

Metadados públicos e digests dos reviews/assessments separados:
`docs/evidence/sprint-2-6-v42-development-20261028/human-review.json`.
Os reviews completos permanecem privados em `.factory/v42-development-po-review/`.
Respostas, expectativas, proposta, relatório da campanha e assessments iniciais
not-run não foram sobrescritos. A declaração humana não é autenticação técnica
do revisor, conforme a autoridade registrada pelo contrato.

## Comparação dos julgamentos observados

Todos os resultados abaixo são julgamentos das respectivas saídas, não aceites
transferidos entre versões. Os oito inputs e expectativas de desenvolvimento
permaneceram iguais; os programas de geração e snapshots de execução diferem.

| Caso | v4.0 | v4.1 parcial | v4.2 |
|---|---|---|---|
| adversarial | PASS | PASS | PASS |
| ambiguidade | FAIL | PASS | PASS |
| conflito de branding | PASS | FAIL | PASS |
| regras compatíveis | FAIL | PASS | PASS |
| domínio novo | PASS | sem saída | PASS |
| regra A | PASS | sem saída | PASS |
| regra B | PASS | sem saída | PASS |
| asset não lido | PASS | sem saída | PASS |

Na v4.0, ambiguidade falhou em cobertura e incerteza; regras compatíveis falhou
em cobertura. Na v4.1, o conflito falhou em incerteza pela pergunta de precedência
omitida. O PO aprovou os novos snapshots v4.2: confirmação do operador em rule,
visibilidade/revisão/aprovação em rules e pergunta explícita de precedência com
ambos os lados. Identidade permanece normativa, sem gatilho inventado; papéis não
são equiparados. A limitação de asset não lido é suficiente no artefato completo.
O custo zero mencionado nos outputs refere-se ao build, não à inferência.

Os quatro casos sem saída na v4.1 não recebem FAIL semântico nem aprovação
retroativa. A ausência resultou de uma falha técnica e da parada da campanha.
Uma nova rodada bem-sucedida não revela a causa histórica do exit 2.

## Gates restantes e sequência

1. Consolidar AHC-021 contra cada critério: separação desenvolvimento/reservado,
   contratos, estados, revisões e evidências. Este aceite cobre oito outputs de
   desenvolvimento; não aprova todo o runner, história ou DoD.
2. Consolidar AHC-022: grounding, proveniência, comparação compatível e cobertura
   das regressões exigidas, inclusive INC-0007. Preservar falhas históricas e
   limites observados; a tabela não prova causalidade do prompt ou generalização.
3. Para AHC-023, manter bloqueada a qualificação até avaliação independente
   adequada: candidato congelado antes de corpus novo, curadoria e expectativas
   revisadas, autorização própria de execução e julgamento das novas saídas.
   Casos reservados já expostos não voltam a ser holdout cego.
4. Perfis e experimentos AHC-024/025 continuam subordinados aos gates anteriores,
   com parâmetros/ambiente observados ou desconhecidos explícitos e orçamento
   próprio. Este aceite não autoriza inferência adicional ou fine-tuning AHC-026.

O orçamento da campanha está encerrado; este registro fez zero chamadas novas.
Model qualification continua not-established e compilation eligibility continua
not-authorized. Defaults, status das histórias e encerramento da Sprint 2.6 não
mudam por aprovação isolada de outputs. INC-0031 conserva a evidência de correção
nos oito snapshots atuais, sem alegação de resolução geral; INC-0033/0034 mantêm
suas causas históricas desconhecidas.
