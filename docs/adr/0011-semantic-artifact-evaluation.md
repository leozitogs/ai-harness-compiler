# ADR-0011 — Julgamento semântico distinto de integridade

Status: aceito para o primeiro incremento da AHC-021.

## Contexto

INC-0007 mostrou omissões e conclusões sem apoio apesar de JSON/referências válidos.
Precisamos de um protocolo que preserve falhas e julgamento pendente sem atribuir
qualidade ao modelo com base em schema, hashes ou avaliação de si próprio.

## Decisão

Separar corpus/rubrica congelados, proposta original, achados automáticos e revisão
semântica humana declarada. O primeiro runner avalia um artefato salvo, offline;
nunca chama um modelo, escreve prompts ou produz a revisão humana.

`UnderstandingArtifactEval/v1` revalida snapshot, digest, expectativas, checks,
status e mapeamentos. `pass` depende de todos os critérios, revisão com suporte de
cada item e cobertura das regras, e rubrica aprovada declaradamente. Omissões e
contradições automáticas não podem ser sobrescritas por um pass da revisão.

Corpus v1 tem 8 casos de desenvolvimento e 8 de holdout distintos, com hashes
congelados antes de tuning. Expectativas/rubrica são propostas para revisão do PO.
Holdout na CLI exige opt-in e digest de candidato congelado declarado pelo operador.
Core não codifica nomes de domínios; categorias descrevem desafios de avaliação.

## Alternativas

- Julgar com o próprio candidato: confunde autorrelato com evidência independente.
- Aprovar por schema/citação existente: repete INC-0007.
- Automatizar toda substância por matching textual: não prova significado e omite
  paráfrases válidas; a avaliação semântica precisa de revisão e evidência.

## Consequências e limites

Nenhuma versão dos contratos de entendimento/IR existentes muda. Novos contratos
e schemas são aditivos. Erros, falta de revisão e não qualificação são explícitos.
`not-run` indica julgamento semântico pendente, mesmo que o artefato exista; `error`
indica execução offline inviável. Falha detectável pode gerar fail antes da revisão.

Revisor e aprovação da rubrica são metadata humana declarada, sem autenticação.
Hashes vinculam integridade, não verdade/autoria. Avaliação offline não comprova
execução/identidade do modelo; qualificação permanece `not-established`.
Batch runner de chamadas reais, metadados de geração, budgets de sessão e seleção
de modelo permanecem pendentes. Não é o Simulation Lab genérico da AHC-008.

Referência: [protocolo e corpus](../engineering/semantic-understanding-evals.md).
