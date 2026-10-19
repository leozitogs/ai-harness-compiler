# ADR-0021 — Proveniência por componente e guards separados

Status: aceito para desenvolvimento em 2026-10-13. Refs: AHC-022, INC-0016.

## Decisão

Adicionar `SemanticAnalysis/v3` com condição, resultado e exceções como textos
interpretados associados a átomos específicos. O critério original continua como
âncora de identidade/ordem; ele não se torna prova automática de cada componente.
Hashes por achado incluem posição das fontes em cada componente e alvos dos guards.
Trocar as fontes entre condição e resultado invalida o parecer mesmo que a união
das fontes permaneça igual.

Representar guards declarados como achados separados, com condição, efeito e
aplicabilidade por critérios ou projeto. Alvo de guard não é evidência de suporte.
Escopo de projeto permite representar restrições de capacidades descritas no
backlog que ainda não possuem critério próprio. A condição continua delimitando
aplicabilidade; escopo de projeto não significa impor uma restrição indiscriminada.
Nada nesse contrato executa guards, concede autorização ou instala código.

A auditoria `SemanticVerifierReport/v4` exige julgamento de cada componente contra
suas próprias fontes, além de suporte por achado e cobertura completa das fontes.
Omissão de julgamento, referência trocada, hash stale ou agregado supports com
componente negativo são rejeitados. O parecer conserva autoridade model-advisory
e estados not-established/not-authorized, inclusive quando todos os componentes
recebem supports. Semântica e completude não são provadas por inventários válidos.

## Motivo

Na reprodução da INC-0016, a análise combinava permissão do autor com guards de
identidade/registro, mas citava só o critério de permissão. O verificador apoiou o
resultado completo. Um campo único de fontes permitiria esconder o problema numa
união de citações; a correspondência por componente explicita qual fonte sustenta
cada afirmação. Guards separados preservam a autorização em vez de reescrevê-la.

## Compatibilidade e limites

Contratos, comandos e evidências anteriores permanecem inalterados. Novos comandos
opt-in: `analyze-project-v3` e `verify-analysis-v4`. Sem migração automática, sem
reclassificação de resultados antigos, sem cópia de revisão humana anterior.

A união por achado v4 aceita até 512 fontes elegíveis para não truncar componentes;
cada componente mantém limite de 32. Auditorias v2/v3 mantêm seus limites originais.
Targets e fontes são revalidados contra o input canônico e excluem asset não lido
e claims externos rejeitados. Nenhuma nova dependência ou catálogo de nichos.

O programa de composição usa a mesma política de modelo já escolhida. Auditor e
gerador podem compartilhar o modelo, por isso concordância não qualifica o sistema.
A avaliação humana v2 não recebe automaticamente v3: seu contrato é versionado e
deve evoluir sem perder hashes/componentes antes do gate de qualificação/holdout.
