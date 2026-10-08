# ADR-0014 — Análise fundamentada com destino explícito dos critérios

Status: aceito para implementação; julgamento semântico e qualificação pendentes.

## Contexto

A extração da AHC-022 preserva o input, mas o estudo original não consome os átomos
nem precisa explicar o destino de cada critério. Os pilotos têm zero BusinessRule.
Exigir que todo critério vire regra criaria regras artificiais para requisitos
técnicos e ocultaria ambiguidades. Citações completas também não provam significado.

## Decisão

GroundedAnalysisProposal/v1 combina UnderstandingProposal/v1 e uma disposição
por critério: business-rule, requirement ou needs-clarification. GroundedAnalysis/v1
vincula a proposta à extração completa. As disposições devem preservar a ordem e
citar achados existentes, do tipo correspondente e da fonte daquele critério.

- business-rule exige uma BusinessRule extraída com description literal.
- requirement exige um statement declarado de capacidade/restrição com texto literal.
- needs-clarification exige uma pergunta bloqueante vinculada à fonte.
- Claims/perfis excluídos não sustentam achados; perguntas podem pedir sua verificação.

As condições, resultados, classificações e justificativas são propostas do modelo;
validadores não comprovam suporte semântico. semantic_status e model_qualification
permanecem not-established e nenhum review humano é criado.

O adapter opcional envia a extração e usa grounded-analysis/v1. O hash do programa
inclui versão, system prompt e schemas de entrada/saída. O modo baseline mantém
prompt e cálculo de candidate_digest anteriores. Nenhum switch de domínio.

O runner existente aceita --analysis-mode grounded; aplica processo isolado,
allowance da sessão, uma chamada por tentativa, limites de bytes/tokens e identidade
observada antes/depois. WorkerResult exige análise válida e compatível com a
proposta quando o modo é grounded. Erros não preservam saída privada do provider.

## Compatibilidade e limitações

SessionSettings acrescenta analysis_mode com default baseline. WorkerResult
acrescenta grounded_analysis opcional, obrigatório apenas no modo novo. Mudança
aditiva, sem novos extras ou migração da IR. Journals anteriores continuam legíveis.

O contrato atual de declarações usa valores exatos das referências originais:
átomos de branding/restrições dentro de referências agregadas não passam a ser
novas fontes declaradas isoladas. Parafrasear continua sendo hipótese. Não relaxar
essas regras para acomodar o modelo; granularidade nova exigiria contrato próprio.

O modo é candidato experimental para verificação de engenharia. Revisão semântica
da rubrica/expectativas e aceite do PO permanecem pendentes; testes mockados e um
smoke de desenvolvimento não qualificarão o modelo ou encerrarão AHC-021/022.
Comparação de desenvolvimento, repair limitado e holdout ficam em incrementos seguintes.
