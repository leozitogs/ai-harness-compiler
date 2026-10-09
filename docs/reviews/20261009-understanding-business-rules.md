# Revisão independente de regras de negócio do entendimento

Data: 2026-10-09. Escopo: critérios aprovados pelo PO, contratos atuais e desenho
do próximo verificador. Agente: `/root/scientific_validation`, com inspeção
somente leitura e reproduções em memória. Revisão adicional do colaborador.
Não é SemanticReview de respostas reais nem qualificação de modelo.

Não houve novas inferências pelos adapters Ollama/Codex CLI, alteração da v1,
consulta de expectativas do holdout para tuning ou decisão de aceite em nome do PO.
Os scripts de reprodução usam
fixtures explicitamente sintéticas e somente o split development.

## Achados do agente

| Prioridade | Achado | Evidência atual | Consequência para a nova versão |
|---|---|---|---|
| P2 | Bloqueio correto sem regra não satisfaz a cobertura atual | `models/semantic_eval.py:77,167,262`: regra esperada obrigatória, ausência de BusinessRule gera fail, cobertura aponta somente para BusinessRule | Expectativa por caso e disposição por regra precisam distinguir entendimento completo de bloqueio fundamentado |
| P2 | Detalhe de implementação vira bloqueio | `models/compact_analysis.py:153,186`: uncertainties e questões de contexto são sempre blocking | Classificar impacto e exigir justificativa; detalhes abertos não bloqueiam automaticamente |
| P2, representação | Fontes diferentes dentro do mesmo pai produzem projeção idêntica | `models/compact_analysis.py:163` reduz índices a source_refs; `/branding` é referência ampla | Parecer deve vincular átomo, pointer e interpretação original; revisão anterior invalida quando a seleção muda |
| P2, novo contrato | Ausência de estado esperado para precedência/bloqueio/rejeição segura | Caso atual só registra conflito presente/ausente e pergunta requerida | Resultado do eval e elegibilidade para compilar são estados separados; uma precedência não autorizada reprova |

As duas primeiras linhas são incompatibilidades do comportamento v1 com critérios
novos aprovados. As demais são lacunas para o verificador; não tornam falsos os
resultados históricos publicados como pendentes. A interpretação compacta completa
retém índices, mas o relatório projetado não os inclui no vínculo de revisão.

## Reprodução complementar

Fixtures de protocolo, sem declarar revisão humana real:

1. Pergunta fundamentada sobre ator/processo de `dev-ambiguous`, sem inventar
   BusinessRule: `rule-coverage=fail` automaticamente na v1.
2. Uncertainty “Qual formato do log?”: projeção gera pergunta `blocking=true`.
3. ItemSupport com `outcome=fail`, porém check agregado de suporte `not-run`:
   relatório aceita status `not-run`. Isso não produz falso pass, mas deixa uma
   evidência negativa fora do estado agregado. Na nova versão, falha material
   explícita deve reprovar ou a contradição deve ser rejeitada na validação.

Esta terceira observação é do colaborador, não atribuída ao agente. Nenhum dos
exemplos comprova suporte semântico das fixtures ou execução de um modelo.

Reproduzir em ambiente com as dependências de desenvolvimento instaladas:

```sh
python scripts/reproduce_understanding_business_review.py
```

Os 67 testes existentes de avaliação e projeção compacta passaram sem skips;
eles verificam o protocolo atual, não demonstram atendimento aos critérios novos.

## Requisitos e testes derivados

- Caso completo: toda obrigação determinável possui regra fiel; pergunta genérica
  não pode substituir uma regra conhecida.
- Caso com bloqueio esperado: identificar motivo e fonte da ambiguidade/conflito,
  preservar obrigações já determináveis e perguntar pelo dado que muda a decisão.
  O caso pode atender à avaliação; o harness permanece inelegível para compilar.
- Rejeição segura precisa ser resposta estruturada e fundamentada. Timeout,
  JSON inválido, omissão ou falha de provedor continuam error/fail, não segurança.
- Classificar dúvidas por impacto sobre regra, autorização ou resultado, separando
  detalhes de implementação. Nome da tabela não bloqueia; ator autorizador ausente
  pode bloquear. Não adicionar revisor externo se a fonte dispensa terceiros.
- Vincular parecer ao digest do input, da interpretação, do achado e aos átomos
  específicos. Mudar um índice, condição, resultado, exceção ou hipótese invalida
  o parecer anterior, mesmo quando source_refs projetados são iguais.
- Conflito exige fontes das duas afirmações e nenhuma escolha silenciosa de
  precedência. Hipótese sem suporte não passa por estar marcada como hipótese.
- Falha material por item não pode ficar oculta por agregado pendente/positivo;
  revisões incompletas nunca viram aprovação.
- Parecer LLM tem tipo e autoridade distintos do julgamento humano; não usar
  retorno do modelo para criar HumanDeclaration ou liberar o harness.

## Guardas existentes verificadas

Suporte aprovado exige julgamento de todos os itens, incluindo hipóteses e
perguntas. Hashes vinculam caso/rubrica/proposta; ausência de revisão não produz
pass; erro não pode carregar julgamento positivo; revisão de entendimento exige
resolução de perguntas/conflitos. O core não exige catálogo de nichos. A autoridade
humana é declarada, não autenticada, como documentado.

## Encaminhamento

Os critérios aprovados permanecem válidos. O próximo incremento deve começar
pelos contratos de expectativa/disposição, impacto das perguntas e vínculo por
átomo, antes de integrar o modelo verificador. Criar uma nova versão de protocolo
e corpus; preservar v1 e seus relatórios. Não executar holdout antes da revisão
das expectativas por caso e do congelamento do candidato.

Referência: [aprovação dos critérios](../delivery/ahc-021-quality-criteria-review.md).
