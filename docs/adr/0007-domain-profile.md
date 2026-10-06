# ADR-0007 — Perfil fornecido, multidimensional e sem scores inventados

Estado: adotada na implementação da AHC-002; incremento em revisão por PR.

## Contexto

O contrato anterior tinha apenas primary, status, confidence e evidências. Campos
de arquétipo, dados e risco precisavam ser tipados, e a aceitação de confidence
numérica não exigia método de medição. Critérios: AHC-002 no backlog canônico.

## Decisão

DomainProfile/v1 representa declarações, hipóteses fornecidas e domínio incerto.
Todos os estados mantêm confidence null. Perfis e alternativas preservam origem,
justificativa e evidências; campos ausentes permanecem desconhecidos. O core não
faz inferência. ProjectDNA/HarnessSpec passam para v3, com migração explícita das
baselines v1/v2 e atualização de digest sob contrato, sem herdar aprovação inválida.

## Alternativas e consequências

Classificar por palavras-chave confundiria correlação com domínio e precisão sem
avaliação. Manter um score opcional permitiria certeza inventada. Não adotamos essas
alternativas. Classificação por LLM/ML fica atrás de adapter com dataset e evals
futuros; taxonomias de domínio/arquétipo são extensíveis como texto.

Consumidores de IR precisam migrar. A origem descreve a classificação primária;
dimensões e alternativas são fornecidas sob o mesmo perfil, sem verificação
independente de negócio/regulação. Ver o contrato de domínio e os testes.
