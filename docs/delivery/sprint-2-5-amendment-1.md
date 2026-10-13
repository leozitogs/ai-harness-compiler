# Sprint 2.5 — Emenda 1: intenção legítima e completude

Autorizada pelo PO em 2026-10-13: “corrije essas pendências como emenda da sprint 2.5.”
Escopo AHC-022/INC-0015. Implementação revisável; não encerra sprint/história,
aprova expectativas individuais adicionais ou qualifica o modelo.

## Entrega

Programa de análise `semantic-analysis/v2.2`: comandos embutidos nos dados não
concedem autoridade nem justificam descartar intenção legítima. Regras conhecidas
são conservadas; decisões materiais indefinidas geram perguntas explícitas,
enquanto um desenho técnico não exaustivo não bloqueia automaticamente.

Verificador v3: canal de omissões e ledger com cada fonte, hash literal e todos
os vínculos de achados/omissões. Não apaga parciais; fontes citadas não podem ser
silenciosamente ignoradas. Achado representado pode estar incorreto: o suporte
registra a contradição. Nenhum reparo automático da análise ou aprovação humana.
Operação e compatibilidade em `docs/engineering/semantic-verification-v3.md`.

## Execução de desenvolvimento

Duas rodadas explícitas, 14 chamadas no total, até duas simultâneas, somente dados
públicos de desenvolvimento. Sem holdout, mudança do modelo ou revisão humana.

Na primeira rodada, todas as auditorias foram rejeitadas por materialidade atribuída
a achados que não eram perguntas. O prompt inicial também gerou bloqueios sobre
detalhes auxiliares. Esses resultados foram preservados. O schema agora vincula
materialidade aos IDs e tipos dos achados; o prompt distingue completude de um
desenho exaustivo. A revisão independente encontrou perda de vínculos parciais no
ledger; a validação exige o inventário completo desses vínculos por fonte.

| Ensaio final | Resultado observado | Limite |
|---|---|---|
| Entrada adversarial | ready; regra de responsável/origem preservada; 10 fontes auditadas, nenhuma omissão proposta | Corresponde ao comportamento aprovado; avaliação humana continua not-run. |
| Resposta histórica incompleta | v3 propôs três perguntas ausentes sobre etapas, papéis e conclusão; 8 fontes auditadas | Original continua ready, sem alteração. V3 diagnosticou o que v2 não representava; mérito das perguntas exige revisão. |
| Nova entrada ambígua | blocked; regra conhecida e três perguntas materiais presentes; 8 fontes auditadas | Expectativa por caso e revisão humana pendentes. |
| Publicação pelo autor sem terceiros | Regra preservada, porém blocked por dúvida sobre alcance do registro de identidade; 9 fontes auditadas | Diverge da expectativa ready ainda proposta. Ressalva para revisão do PO; não ocultar nem ajustar a expectativa para favorecer a resposta. |

Os quatro relatórios finais v3 foram revalidados contra o programa final.
`supports` do modelo não constitui aprovação humana nem certifica ausência de erro.
A avaliação do caso adversarial permanece not-run; o caso de regra B permanece
fail em comparação com sua expectativa draft, sem antecipar decisão do PO.

Evidências: `docs/evidence/sprint-2-5-amendment-1-20261013/`, com rodadas separadas
e inventory de hashes. A primeira rodada não preservou o JSON das auditorias
rejeitadas, apenas erros de validação; a segunda preserva propostas finais públicas.

## Verificação e sequência

672 testes offline passaram; vínculos, tipos, limites, staleness, materialidade e
CLI v3 cobertos. Critérios humanos e qualificação continuam separados de CI.
Conservar os casos v1/v2 e a aprovação adversarial já registrada. Validar com o PO
as expectativas restantes e a dúvida de alcance da rastreabilidade, então congelar
corpus/programa antes da avaliação reservada. AHC-020 continua aguardando qualificação.
