# ADR-0016 — Interpretar com o modelo, vincular citações no compilador

Status: aceito para implementação experimental; julgamento semântico pendente.

## Contexto

Nos smokes, o modelo confundiu IDs de referências/átomos e o inventário de critérios.
O repair parou corretamente, mas não produziu proposta aceita. Pedir ao LLM que
copie texto, gere IDs e mantenha associações mistura interpretação e serialização.

## Decisão

Introduzir CompactUnderstandingInput/Proposal/Spec v1 e um modo compacto opcional.
Enviar um inventário único de contexto e uma lista ordenada de textos de critérios,
sem repetir snapshot/referências/átomos nem expor claims externos ou nomes/conteúdos
de assets. O modelo recebe somente a contagem de assets não lidos.

O modelo propõe uma interpretação por posição: business-rule, requirement ou
needs-clarification. O schema enviado limita a lista ao número exato de critérios
e os índices de contexto ao intervalo daquele input. Validação independente
rejeita dimensões, índices e campos incompatíveis; nenhum item é truncado.

A projeção pura cria IDs, copia texto e source_ref do critério original e produz
ProjectUnderstanding/v1. Condições/resultados de regras continuam origin=hypothesis.
Um requisito preserva apenas seu texto declarado como restrição; a classificação
proposta ainda exige revisão. Achados de contexto também são hipóteses, confidence
permanece null e dúvidas geram perguntas bloqueantes. Não usar extração literal
como aprovação de uma interpretação ou como suporte semântico automático.

Interpretação original, extração e projeção são preservadas e comparadas pelo
WorkerResult. Isto é um novo protocolo para gerar propostas, não uma correção
silenciosa das respostas rejeitadas dos protocolos anteriores.

## Compatibilidade e limites

Baseline/grounded e repair mantêm seus programas e contratos. analysis_mode ganha
compact por opt-in; compact_analysis opcional só é aceito quando corresponde ao
modo/projeção. Nenhuma nova dependência, framework ou enum de nichos.

Até 64 critérios, 512 entradas de contexto, 32 achados e 16 issues; os limites
compostos de ProjectUnderstanding também se aplicam. O compilador rejeita excessos.
Um conflito necessita dois source_refs distintos; valores diferentes sob a mesma
referência agregada não recebem origens inventadas para fazer o contrato passar.

Programa inclui texto, schemas e políticas versionadas de dimensões/projeção no SHA.
Mudança material na projeção exige alterar sua versão; identidade de código também
é observada no journal. Mapeamento por posição e citações de contexto podem estar
semanticamente errados, embora os contratos passem. Comparação de desenvolvimento
não substitui revisão do PO, holdout ou qualificação com repetições.
