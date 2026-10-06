# Sprint 2 — Estrutura operacional aprovada

PO aprovou o escopo AHC-019/020 em 2026-10-06. Estruturação não inicia implementação,
fecha a Sprint 1 ou confirma capacidade/data. O gate de aprovação do plano está
atendido; os demais gates permanecem explícitos em planning/sprint-2.readiness.json.

## Organização e ownership

Um milestone, duas issues de história, oito estágios e 21 subtarefas. IDs AHC são
identificadores do produto; números das issues são mapeados no manifesto da sprint.
Colaborador/Codex implementa e coleta evidências; PO decide regras e aceite semântico.

[Milestone Sprint 2](https://github.com/leozitogs/ai-harness-compiler/milestone/1),
[AHC-019 / issue #11](https://github.com/leozitogs/ai-harness-compiler/issues/11) e
[AHC-020 / issue #12](https://github.com/leozitogs/ai-harness-compiler/issues/12).
Clara/Atlas/Ícaro/Vera/Sentinela/Nexo apoiam, sem representar seis developers ou
capacidade de execução paralela. Um item de implementação ativo por executor.

Estados: planned → in progress → in review → done; blocked registra causa, impacto,
responsável e próxima ação. Não fechar a issue apenas porque o plano foi gerado.
Branches: feat/ahc-019-project-understanding e feat/ahc-020-harness-blueprint-packs.
Commits convencionais, PR por incremento, CI obrigatória, squash e DoD do projeto.

## AHC-019 — Entendimento generalista

| Subtarefa | Etapa | Evidência de conclusão |
|---|---|---|
| 019-01 | Design | Contratos de input original, interpretação, regra, fonte, conflito, pergunta e estado de revisão; política de versão/migração |
| 019-02 | Design | Interface de modelo/timeout/limites, erro e structured output; domínio sem SDK de provider |
| 019-03 | Design | Rubrica e casos reservados definidos antes do ajuste de prompts/packs |
| 019-04 | Implement | Intake de fontes autorizadas, limites, UTF-8, origem e separação de instruções/dados |
| 019-05 | Implement | Adapter real configurável e fake de teste; prompts gerais sem switches de nicho |
| 019-06 | Implement | Proposta → revisão/resolução → propagação consistente para DNA/grafo; snapshots originais preservados |
| 019-07 | Verify | Negativos de JSON/referências/confiança inventada/conflitos e revisão inconsistente |
| 019-08 | Verify | Modelo real identificado, parâmetros/ambiente registrados e execução controlada com evidências |
| 019-09 | Verify | Revisão semântica dos casos novos, ambíguos e mesmo domínio/regras distintas |
| 019-10 | Review | ADR, migração, documentação e limitações atualizadas; comentários técnicos resolvidos |
| 019-11 | Review | PR integrado com CI verde e demonstração do entendimento ao PO |

Áreas propostas: models/understanding.py, understanding/, adapters/llm/ e fronteira
CLI/intake. Arquivos são orientação de design, não implementação existente ou ordem
para copiar o runtime interno de agentes. Modelo/provedor concreto ainda a definir.

## AHC-020 — Blueprint e packs opcionais

| Subtarefa | Etapa | Evidência de conclusão |
|---|---|---|
| 020-01 | Design | Blueprint liga regra/capacidade a necessidade do harness, alternativas e gaps |
| 020-02 | Design | Pack versionado com parâmetros, aplicabilidade, exclusões, compatibilidade e conflitos |
| 020-03 | Implement | Registry declarativo limitado, sem execução automática de plugins/scripts externos |
| 020-04 | Implement | Seleção explicável e resolução de conflitos; regra confirmada do projeto prevalece |
| 020-05 | Implement | Revisão do blueprint alimenta baseline e mantém módulos futuros como gaps |
| 020-06 | Verify | Caminho sem pack e novo pack sem alterar core, com evidências |
| 020-07 | Verify | Mesmo domínio com regras diferentes produz planos diferentes por conteúdo |
| 020-08 | Verify | Snapshots, escopos, revisão inválida, isolamento e exportação segura |
| 020-09 | Review | Documentação, ADR/migração, segurança e licença/proveniência de packs |
| 020-10 | Review | PR integrado, demo do fluxo e material da Sprint Review |

Áreas propostas: models/blueprint.py, models/pattern_pack.py, blueprint/, packs/,
pipeline e compiler. Design formal espera AHC-019 revisada/integrada. Refinamento
antecipado pode ocorrer, sem começar a implementação antes do contrato estabilizar.

## Matriz de demonstração

| Caso | Observação exigida |
|---|---|
| E1 — Domínio novo | Input aceito sem nome de nicho/pack cadastrado; entendimento e perguntas rastreáveis |
| E2 — Mesma categoria, regras A/B | Regras divergentes mudam decisões/procedimentos, não só nomes |
| E3 — Branding/backlog contraditórios | Conflito explicitado e resolução controlada pelo responsável |
| E4 — Proposta ambígua | Hipóteses e lacunas preservadas; sem certeza/score inventado |
| E5 — Sem pack/com pack | Baseline viável sem pack; seleção justificada e regras locais preservadas |
| E6 — Pack novo/incompatível | Registro sem editar core; incompatibilidade rejeitada antes de adoção |
| E7 — Snapshot/isolamento | Alteração de origem, revisão inválida e referência cruzada bloqueadas |

Os briefs e resultados esperados são preparados/congelados em 019-03; esta matriz
não declara datasets ou execuções existentes. Holdouts não entram no ajuste do
prompt/catálogo. Toda regra inferida deve ter origem e status; conclusões sem apoio
viram perguntas ou findings. Findings críticos impedem aceite. Rubrica/manual
precisa de revisão do PO; quantidade de testes não substitui qualidade semântica.

## Pacote de evidências e checkpoints

Registrar por caso: hash/versão do input, contrato/prompt/pack, modelo e parâmetros,
resultado estruturado, referências, latência/custo quando medidos, findings e
reviewer. Redigir/remover dados privados; não guardar credenciais ou CoT privado.
Fake aprova apenas comportamento estrutural. Demo com modelo real é gate da AHC-019.

D1: contratos/modelo/rubrica; D5: entendimento revisado; D9: blueprint/pack/baseline;
D10: Review e Retro. Dias são relativos, sem reuniões agendadas ou data final.
Daily atualiza tarefa, evidência, impedimento e próximo passo. Retrospective registra
uma melhoria verificável; Review confirma valor e reordena o backlog com o PO.

Próximo item técnico é 019-01. Antes da execução da sprint, resolver gates de entrada
sem inferir retrospectiva realizada, modelo instalado ou capacidade confirmada.
