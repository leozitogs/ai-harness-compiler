# Sprint 2.6 — Julgamentos específicos e candidato corretivo

Data: 2026-10-20. AHC-021/022 em andamento; nenhuma história concluída.

## Decisão do PO e efeito observado

O PO respondeu “Confirmo os dois julgamentos recomendados” à pergunta que
identificava os dois casos e limitava explicitamente o escopo da confirmação:

1. `dev-ambiguous`: reprovar o suporte da condição de `guard-1`, preservando
   a obrigação de registrar a identidade do responsável.
2. `dev-compatible-rules`: a escolha dos responsáveis é detalhe de implementação
   não bloqueante; manter visibilidade restrita e aprovação, sem presumir que os
   papéis sejam exercidos pela mesma pessoa.

Foi registrada uma declaração `human-declared-not-authenticated`, atribuída a
`leozitogs:po-declared`. Não há alegação de autenticação externa. O
[registro escopado](../evidence/sprint-2-6-human-judgments-20261020/decisions.json)
liga as decisões aos hashes dos casos, rubrica e análises.

O [assessment reproduzível](../evidence/sprint-2-6-human-judgments-20261020/dev-ambiguous-assessment.json)
resulta em **fail** para suporte de citações, com cinco critérios `not-run`.
O diagnóstico não bloqueante do segundo caso não contém inventário completo
de julgamentos e, portanto, não é convertido em aprovação do critério de incerteza.

Situação atual: **1 caso fail, 7 not-run; 1 de 48 julgamentos por critério
registrado, 47 pendentes; nenhum pass**. O
[progresso](../evidence/sprint-2-6-human-judgments-20261020/status.json)
complementa os relatórios anteriores, preservados como snapshots históricos.

## Problema e alternativa corretiva

A análise histórica inventou o vínculo “ao registrar decisões no processo de
publicação” para a obrigação de identificação. O contrato `GuardSpec` exige
condição, mas a fonte da obrigação não declara um gatilho. A exigência do campo
é uma possível pressão de representação; não foi demonstrada como causa causal
do comportamento do modelo por experimento controlado.

Em vez de afrouxar citações ou preencher uma condição genérica, o candidato
`semantic-composition/v3.2` orienta:

- Preservar obrigações sem gatilho declarado como contexto normativo
  `subject=constraint`, citando a própria restrição e explicitando o limite de
  aplicabilidade, sem inventar uma política executável.
- Usar guards somente quando condição e efeito possuem suporte independente.
  Links de alvo não substituem evidência de aplicabilidade.
- Não equiparar papéis nem acrescentar aprovações por faltar a atribuição de uma pessoa.

O contrato v3 já suporta essa representação. Não há migração de schemas, alteração
dos inputs, reescrita de respostas antigas ou codificação de nichos/casos no prompt.
É uma hipótese corretiva a avaliar: preservar texto normativo como contexto ainda
não demonstra cobertura semântica nem equivalência a controles de execução.

## Implementação e reprodução

A API Python `analyze_composition` recebe `program_version` opcional. O default
e a CLI permanecem em **v3.1**. A variante v3.2 exige seleção explícita pela API;
não foi promovida ao principal. `composition_program_digest` vincula versão,
prompt e schema dinâmico; não é um fingerprint completo de uma execução, pois
não inclui modelo, parâmetros, input e ambiente.

```python
from ai_harness_compiler.semantic_composition import composition_program_digest

# Preparação offline; extraction é uma GroundingExtraction já validada.
fingerprint = composition_program_digest(extraction, "semantic-composition/v3.2")
```

Depois de liberar os gates, um runner explícito poderá chamar
`analyze_composition(extraction, generator, program_version="semantic-composition/v3.2")`,
registrando input, receita, modelo, parâmetros, tentativas e revisão separadamente.
Nenhuma geração real, holdout, ajuste de temperatura ou treino foi executado neste incremento.

## Verificação e continuação

Testes offline verificam preservação exata do prompt v3.1, seleção explícita,
fingerprints distintos e rejeição de versão desconhecida antes de chamar o modelo.
A regressão real reproduz o julgamento do PO pela CLI, mantendo cinco critérios
pendentes e compilação não autorizada. Respostas injetadas nos testes não provam
que v3.2 melhorou o entendimento do modelo.

Próximas etapas: concluir julgamentos restantes da matriz de desenvolvimento;
consolidar falhas e congelar o candidato/programa; definir budget concreto antes
de novas gerações. AHC-024/025/026 continuam dependentes dos gates existentes.
