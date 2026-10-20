# Sprint 2.6 — Adjudicação técnica dos diagnósticos

2026-10-20. Continuação da preparação autorizada pelo PO após o parecer favorável
do Nexo. Este documento contém recomendações técnicas, **não julgamentos humanos**.
Nenhuma resposta foi promovida a aprovada, nenhum prompt foi ajustado e o holdout
permaneceu sem leitura.

## Trabalho executado

Foram confrontadas com suas fontes as **6 possíveis omissões e 1 avaliação negativa
de componente** presentes nas oito respostas selecionadas. Os casos sem diagnóstico
negativo não foram automaticamente aceitos. A matriz completa anterior continua
com 70 achados/30 componentes e seus seis critérios pendentes por caso.

O [rascunho estruturado](../evidence/sprint-2-6-adjudication-20261020/draft.json)
preserva hashes de análises/advice, textos originais dos diagnósticos, fontes
literais e identidade dos achados/componentes. Seu estado é `awaiting-human-judgment`,
autoridade `advisory-only`, sem `SemanticHumanReview` criado.

## Decisões específicas submetidas ao PO

### Q-S26-01 — Suporte da condição em ambiguidade

- Fonte da obrigação: “Registrar a identidade do responsável.”
- Fonte citada pela condição: descrição do backlog sobre organizar publicação e
  registrar decisões.
- Condição produzida em `guard-1`: “Ao registrar decisões no processo de publicação
  da equipe.” O resultado continua exigindo registrar a identidade.
- Recomendação: rejeitar o suporte dessa condição, preservando a obrigação.
  Citar uma atividade relacionada não estabelece por si a ligação usada como
  ativação da restrição. O tratamento das perguntas materiais de conclusão continua
  sendo outra parte da avaliação.

Pergunta enviada ao PO: confirmar rejeição, considerar a condição sustentada ou
manter o julgamento pendente. **Sem resposta registrada.** Isso julga um componente,
não autoriza preencher os demais critérios como pass/fail.

### Q-S26-02 — Materialidade em regras compatíveis

- Regras mantidas: materiais visíveis somente ao educador responsável e publicação
  dependente de revisão/aprovação do educador.
- Auditor sugeriu perguntar como determinar essas pessoas e se seriam a mesma.
- Recomendação: tratar a pergunta como não bloqueante na fase de entendimento,
  preservando as duas obrigações e sem afirmar identidade entre os papéis.
  A configuração operacional de quem ocupa um papel não cria automaticamente
  uma contradição ou um novo aprovador.

Pergunta enviada ao PO: confirmar diagnóstico não bloqueante, considerar
esclarecimento bloqueante ou manter pendente. **Sem resposta registrada.** A decisão
vale para o diagnóstico, não para todos os achados/critério de incerteza do caso.

## Outros diagnósticos examinados

| Caso / alvo | Observação verificável | Recomendação técnica pendente |
| --- | --- | --- |
| `dev-adversarial` / `omission-1` | A identidade está expressa em `context-4`, como capability; não há guard. | Revisar força normativa da representação. Não alegar ausência literal de uma informação presente, nem concluir completude apenas porque o texto aparece. |
| `dev-branding-conflict` / `omission-1` | O conflito preserva dispensa e exigência de aprovação com ambas as fontes e pergunta de precedência. | A exigência de mais uma regra própria pode ser redundância de representação. Não selecionar um lado nem exigir uma regra executável para resolver o conflito. |
| `dev-rules-a` / `omission-1` | A aprovação pelo responsável designado está preservada, sem aprovador externo. | A rotina de designação pode ser detalhe de implementação; não criar bloqueio adicional automaticamente. |
| `dev-rules-a` / `omission-2` | Não foi afirmada equivalência entre responsável do registro e aprovador. | Manter papéis não identificados como iguais; ausência de uma equivalência não demonstrada não exige inferi-la nem bloquear por padrão. |
| `dev-rules-b` / `omission-1` | O autor mantém permissão sem terceiros; a obrigação usa o termo responsável sem igualá-lo ao autor. | A identidade deve ser vinculada posteriormente, sem inventar ator ou aprovação. Julgar separadamente a aplicabilidade do guard. |

São propostas de adjudicação, sujeitas à decisão humana e à verificação completa
dos seis critérios. Alertas do auditor podem ser falsos positivos; também é possível
haver falhas não apontadas por ele.

## Comparação transversal observada

Além da ambiguidade, a mesma restrição de identidade aparece em outros seis casos: em alguns
é contexto, em outros vira guard. O auditor acusa omissão em uma representação como
capability, mas não acusa em outras como constraint. Isso exige revisar a força
normativa e a aplicabilidade preservadas, não somente contar guards ou alertas.

Não é experimento causal: os demais inputs e outputs diferem. Não se infere que
trocar um rótulo resolva o problema. Nenhum ajuste ao corpus ou resposta histórica
foi feito para produzir um vencedor.

## Encaminhamento técnico após as decisões

1. Registrar somente os julgamentos específicos recebidos, vinculados aos hashes;
   sem transformar confirmação de um diagnóstico em aprovação integral do caso.
2. Se um componente for reprovado, usar o assessment parcial suportado pelos
   contratos: falha explícita com os demais critérios ainda não julgados, sem
   inventar reviewer, mapeamentos ou suporte positivo ao achado.
3. Para nova geração futura, propor comportamento generalista: preservar obrigação
   e incerteza sem inventar ator, condição de ativação ou relação entre papéis.
   Não codificar nichos/nomes deste corpus no core e não editar a saída antiga.
4. Comparar candidato somente após liberar os gates e fixar orçamento/programa;
   não ajustar parâmetros ou executar treinamento como resposta automática a um alerta.

## Gate que permanece

O [ADR-0022](../adr/0022-component-human-assessment.md) estabelece: “Parecer de modelo
não é importado como revisão humana”. As duas perguntas pendentes pedem decisões
sobre fontes/componentes, não permissão para trabalhar. Sem esses julgamentos,
continua válida apenas esta análise técnica consultiva. AHC-024 e os experimentos
permanecem dependentes dos gates AHC-021/022.

## Atualização — julgamentos específicos recebidos em 2026-10-20

As duas decisões específicas foram confirmadas pelo PO após este snapshot.
O estado atual é 1 caso fail e 7 not-run, sem aprovação integral de casos.
Ver [registro humano e candidato corretivo](sprint-2-6-human-judgments.md).
As pendências descritas acima representam o momento da preparação original.
