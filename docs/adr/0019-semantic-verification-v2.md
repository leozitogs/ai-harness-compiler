# ADR-0019 — Análise e verificação semântica v2

Status: aceito para desenvolvimento em 2026-10-09. Refs: AHC-021, AHC-022.

## Decisão

Adicionar contratos v2 independentes, sem reinterpretar corpus ou relatórios v1.
Cada critério conserva identidade e ordem do átomo original. Conclusões conservam
classificação, condição, resultado, exceções, impacto, motivo de recusa e fontes
exatas. O host reconstitui fontes; o provedor não declara sua validade. Hashes da
análise completa e do achado invalidam pareceres após alterações.

`ready`, `blocked` e `safely-rejected` são disposições derivadas. Perguntas materiais
e conflitos bloqueiam; detalhes de implementação não bloqueiam. Impacto ainda
exige julgamento semântico. Rejeição exige motivo e fonte: timeout e JSON inválido
são erros técnicos, nunca rejeição segura.

O verificador recebe achados e fontes por chamada independente, sem expectativas
do benchmark. Sua autoridade é `model-advisory`; concordância entre chamadas do
mesmo modelo não comprova correção. Não há votação, repair loop ou aprovação humana
automática. A avaliação humana exige cobertura e suporte completos, seis critérios
positivos e aprovações explícitas do caso e da rubrica. Falha individual não fica
oculta sob agregado pendente. Bloqueio esperado pode passar, mas compilação continua
`not-authorized`. Aprovação de critérios não aprova casos ou respostas.

## Motivo e alternativas

A revisão independente encontrou limitações da v1: cobertura exige regras mesmo
em casos ambíguos, dúvidas técnicas bloqueiam e referências-pai perdem o átomo
escolhido. Alterar v1 reinterpretaria evidências congeladas. A nova versão mantém
compatibilidade e torna explícitos os requisitos aprovados pelo PO.

## Consequências e limites

Core sem dependência de provedor, com interface de geração JSON. CLI v2 usa por
enquanto Codex CLI explicitamente invocado, sem fallback. `study` v1 continua igual.
Não existe migração automática: impacto e expectativas exigem nova revisão.
Rubrica mantém envelope compatível v1 e `version: v2`. Declarações humanas não são
autenticadas externamente; fixtures de teste não são aprovação real do PO.
Corpus v2 congelado, holdout, qualificação e autorização de compilação são posteriores.
