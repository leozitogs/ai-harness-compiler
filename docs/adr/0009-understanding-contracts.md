# ADR-0009 — Propostas ancoradas no snapshot e revisão separada

Estado: adotada no primeiro incremento da AHC-019, sujeito à integração por PR.

## Contexto e decisão

Para estudar qualquer proposta/branding sem nichos fixos, o modelo deve propor
interpretações que possam ser revisadas sem alterar o original. Introduzir contratos
independentes de provider para snapshot, referências, fatos citados, hipóteses,
regras, conflitos e perguntas. Separar revisão da saída permitida ao modelo e
vincular seus metadados aos hashes do input/proposta.

Reutilizar ProjectInput/v1 e manter IR v3 existente intacta neste incremento.
References resolvem JSON pointers em dados normalizados, sem execução/ingestão de
assets. Confidence permanece null. Limites e erros com valores ocultos delimitam
a fronteira da nova CLI. Não produzir um entendimento falso com templates ou fake.

## Alternativas e limites

Texto livre sem contrato impediria validação antes da adoção. Revisão dentro da
saída do modelo permitiria confundir proposta com aprovação. Não adotar essas
alternativas. Citação exata/digest não provam verdade, entailment ou identidade
do reviewer. Adapter, estudos reais, auth/revisão/aplicação e rubrica de qualidade
ainda são trabalho da AHC-019, não funcionalidades demonstradas nesta entrega.
