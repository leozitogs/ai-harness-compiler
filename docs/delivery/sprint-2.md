# Sprint 2 — Harness específico por domínio

Planejamento de 2026-10-06. Dez dias úteis propostos, sem data inicial ou capacidade
confirmadas. Execução não iniciada. Duas histórias são previsão de escopo, não
compromisso de prazo ou velocity inferida da Sprint 1.

**Sprint Goal:** compilar prompts, skills e uma especificação de documentação/
aprendizado rastreáveis e distintos para projetos de educação e comércio.

## Entrada e dependências

AHC-001/002/003 estão integradas (PRs #6/#8/#7). O PR #9 corrigido tem CI verde,
mas continua aberto na data do planejamento. Antes de iniciar: integrar esse PR,
realizar Review/Retrospective da Sprint 1 e confirmar capacidade/início/escopo.
As duas falhas de revisão ensinam a validar contratos desserializados e preservação
do snapshot, além de testar o produtor. Incorporar essa verificação desde o design.

## Escopo e incremento esperado

| História | Trabalho | Entrega demonstrável |
|---|---|---|
| AHC-005 | PromptSpec/SkillSpec, registries, validação de referências e compiladores | Educação e comércio geram prompts e procedimentos diferentes, com inputs/outputs, contexto, regras, tools declaradas e avaliação |
| AHC-015 | DocumentationLearningSpec por projeto | Duas configurações tipadas de documentação/memória: taxonomia, ownership, revisão, retenção, proveniência, isolamento e regras rastreáveis |

Critérios canônicos: project-definition/project.yaml. Prompt/Skill não podem ser
apenas textos genéricos com nome de domínio trocado: os passos devem refletir
capacidades e critérios diferentes. LearningSpec é um contrato exportado, não
um runtime de memória já instalado no projeto alvo.

## Trabalho concreto

AHC-005:

1. Definir contratos versionados de prompts e skills, schemas de I/O, activation,
   exclusões, passos, contexto, verificadores e referências a requisitos/evidências.
2. Especificar registries e política de referências a ferramentas ainda declarativas;
   não simular ToolSpec executável antes da AHC-007.
3. Compilar prompt registry, templates e skills com metadata resumida, SKILL.md e
   referências sob demanda. Separar instruções do template de inputs não confiáveis.
4. Validar IDs, escopos, snapshots, ciclos quando houver dependência, versões e
   referências, tanto na criação quanto no JSON desserializado/antes da emissão.
5. Usar educação para preparação de rascunhos com fontes e revisão; comércio para
   procedimentos de disponibilidade/pedido com valores explícitos. Verificar
   diferença procedural, rastreabilidade e reprodutibilidade.

AHC-015 (após a integração de AHC-005):

1. Modelar DE/DOC/ADR/INC/LES/RUN/EXP, proprietários/revisores, estados, retenção,
   proveniência, escopo, captura de desafios e promoção de lições por evidência.
2. Derivar políticas rastreáveis de DNA, constraints e Evidence Pack. Não inventar
   obrigação regulatória, prazo de retenção ou dado ausente; registrar incógnitas.
3. Exportar a spec e integrá-la ao contexto do harness, mantendo memória privada
   do compilador fora dos artefatos gerados.
4. Testar diferenças por domínio, regras sem evidência, conflito/remoção de origem,
   JSON contraditório e referências/projetos cruzados. Exigir autorização para
   qualquer futura transferência de experiências entre projetos.

## Sequência proposta

| Dias relativos | Trabalho |
|---|---|
| D1 | Refinar exemplos, contratos, ameaças e plano de testes; decidir versionamento/migração |
| D2–D4 | Implementar AHC-005 e compilar artefatos nos dois domínios |
| D5 | Verificação, revisão e integração de AHC-005 |
| D6–D8 | Design e implementação de AHC-015 com regras/evidências por domínio |
| D9 | Verificar isolamento, invariantes, regressões e integrar AHC-015 |
| D10 | Demo, Sprint Review e Retrospective |

Refinamento inicial de AHC-015 pode ocorrer cedo; seu gate formal de design depende
de AHC-005 revisada. Uma história de implementação ativa por executor. Se escopo
não couber, PO e colaborador renegociam; não excluir critérios ou declarar uma
spec incompleta como Done.

## Pessoas, controle e gates

PO: prioridade, exemplos, políticas de negócio, capacidade e aceite de valor.
Colaborador/Codex: código, schemas, testes, docs e PRs. Clara/Atlas apoiam contratos,
Ícaro tarefas, Vera verificações, Sentinela limites e Nexo andamento. Seus relatórios
não comprovam implementação ou aprovação. Não agendar reuniões automaticamente.

Planning até 90 min, Daily até 15 min, Review 45 min e Retro 30 min, conforme o
acordo local. Fluxo planned → in progress → in review → done; blocked registra ação.
Branches: feat/ahc-005-prompt-skill-spec e feat/ahc-015-documentation-learning-spec.
Aplicar DoD do projeto, CI obrigatória e revisão/integração em cada incremento.

## Artefatos do plano e validação

planning/sprint-2.json seleciona escopo e registra gates. sprint-2.tasks.json possui
oito etapas técnicas em oito ondas de precedência. sprint-2.work-items.json detalha
ações/entregáveis. Ondas não são dias nem execução efetivamente realizada.

```sh
factory tasks project-definition --select ahc-005 ahc-015 --completed ahc-001 ahc-002 ahc-003
python scripts/generate_sprint_plan.py --sprint sprint-2 --check
```

As declarações completed referem-se a incrementos integrados; não encerram a
Sprint 1 nem eliminam o gate do PR #9. Alteração incompatível da IR requer versão,
migração explícita e preservação de contratos que ainda sejam compatíveis.

## Roteiro da Review e limites

Demonstrar geração dos dois domínios, vínculo de cada prompt/skill aos requisitos,
metadata antes de SKILL.md, referência inválida rejeitada antes de escrever,
LearningSpecs diferentes com incógnitas explícitas e tentativa de acesso cruzado
bloqueada. Verificar hashes/repetição e reexecutar benchmark sem inventar SLO.

Fora do escopo: Context Engine completo (006), Policy Engine executável (007),
Simulation Lab (008), providers/pesquisa (009), memória funcional gerada (016) e
agentes especializados gerados (017). Não há stretch automático. Esses itens
entram em sprints posteriores conforme dependências, aprendizado e capacidade.
