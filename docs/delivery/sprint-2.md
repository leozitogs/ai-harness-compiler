# Sprint 2 replanejada — Entender o projeto antes de especializar

Replanejamento de 2026-10-06 após rejeição explícita do plano anterior pelo PO.
Escopo aprovado pelo PO em 2026-10-06; execução não iniciada. Dez dias úteis são um timebox
proposto, sem capacidade ou data inicial confirmadas, sem promessa de prazo.

**Sprint Goal:** estudar proposta, branding e regras de negócio de um projeto
sem nicho pré-programado, produzir entendimento rastreável e derivar um plano de
harness adaptável, com compilação da baseline após revisão.

## Direção de produto

O core é generalista. Educação/comércio/dev-tools são fixtures, não destinos do
produto nem ramificações de geração. O domínio emerge do estudo; projetos do mesmo
domínio com regras diferentes precisam de planos diferentes. Templates/frameworks
servem como packs opcionais, extensíveis por registro e aplicabilidade, nunca
como requisito para aceitar um projeto. Ver pipeline generalista de produto.

## Escopo alvo

| História | Entrega | Critério observável |
|---|---|---|
| AHC-019 — Entendimento generalista | ProjectUnderstandingSpec, estudo via adapter de modelo, regras e perguntas rastreáveis | Proposta/branding/backlog geram hipóteses e regras com origem; conflitos e incógnitas não viram fatos |
| AHC-020 — Plano e packs opcionais | HarnessBlueprintSpec + PatternPackSpec/registry e integração com baseline | O plano responde às regras do projeto; novo domínio funciona sem pack; escolha de pack é explicável e validada |

AHC-005 e AHC-015 saem da seleção desta sprint. Não cancelar suas funcionalidades:
elas serão geradas a partir do entendimento/blueprint, em incrementos posteriores.
Critérios canônicos em project-definition/project.yaml.

## AHC-019 — Trabalho concreto

1. Modelar objetivo, público, posicionamento/tom do branding, entidades, capacidades,
   regras (condição/resultado/exceções), restrições, origens, conflitos e perguntas.
2. Preservar o input original e distinguir afirmação fornecida de inferência.
   Definir confiança como incógnita até haver avaliação; validar snapshots/referências.
3. Implementar interface própria de modelo com fake para testes e adapter real
   configurável (local quando disponível). Validar structured output, timeout e
   limites antes de aceitar propostas. Core não importa framework/provedor.
4. Integrar fontes textuais locais autorizadas, limitadas e tratadas como dados;
   parsing multimodal e pesquisa web aberta ficam fora desta fatia.
5. Implementar estudo, revisão/resolução e propagação consistente para DNA/grafo.
   Não promover hipótese, inventar requisito ou modificar original silenciosamente.
6. Demonstrar uma execução controlada com modelo real. Fake não comprova entendimento
   semântico; se faltar modelo, marcar essa demonstração pendente, não Done.

## AHC-020 — Trabalho concreto

1. Mapear capacidades/regras a contexto, skills, tools, workflows, documentação e
   critérios de avaliação. Plano contém origem, alternativas, decisões e gaps.
2. Definir pack versionado: aplicabilidade por requisitos, parâmetros, exclusões,
   compatibilidade e conflitos. Criar pequeno catálogo de padrões abrangentes,
   com registro declarativo sem executar código/plugin externo por padrão.
3. Selecionar/adaptar packs por evidências do projeto; regras específicas confirmadas
   prevalecem. Explicar recusa, conflito e caminho sem pack.
4. Compilar o baseline atual após revisão, com blueprint/evidências anexos. Não
   alegar prompts, memória ou agentes completos antes de seus compiladores.
5. Validar propostas/decisões também ao desserializar, antes da emissão. Testar
   isolamento, reprodutibilidade e revisão inválida sem mudar projeto existente.

## Avaliação e roteiro de Review

Reservar inputs para avaliação antes de ajustar prompts/packs. Usar critérios
semânticos revisados pelo PO, além dos checks estruturais:

- Domínio novo sem nome/pattern cadastrado produz entendimento e baseline revisável.
- Dois projetos do mesmo domínio com regras distintas produzem planos distintos.
- Branding e backlog em conflito geram pergunta explícita, não uma regra arbitrária.
- Proposta ambígua mantém hipóteses alternativas e incógnitas.
- Mesmo projeto com/sem pack registra decisões; pack não sobrescreve regra confirmada.
- Pack novo é registrado sem editar lógica do core; seleção incompatível é rejeitada.
- Chamada real de modelo, saída validada, revisão e baseline têm evidências disponíveis.

Fixtures existentes continuam úteis para regressão. Elas não delimitam os nichos
aceitos. Não inferir generalização universal, SLO ou qualidade de agentes desses casos.

## Ordem proposta e responsabilidades

| Dias relativos | Trabalho |
|---|---|
| D1 | Confirmar escopo/capacidade, escolher modelo, reservar casos de avaliação e decidir contratos |
| D2–D4 | AHC-019: intake de estudo, adapter, propostas estruturadas e revisão |
| D5 | Avaliação semântica com modelo real, regressões e integração de AHC-019 |
| D6–D8 | AHC-020: blueprint, registro/seleção de packs e baseline adaptada |
| D9 | Casos novos/conflitos, isolamento, compatibilidade, revisão e integração |
| D10 | Sprint Review e Retrospective |

Uma implementação ativa por executor; refinar AHC-020 cedo, mas seu gate formal
depende da revisão da AHC-019. PO define regras/aceite/prioridade e avalia qualidade.
Colaborador/Codex implementa, testa e publica PRs; equipe interna apoia sem substituir
execução de checks ou decisões do PO. Planning 90 min, Daily 15 min, Review 45 min,
Retro 30 min são propostas locais, sem eventos agendados.

## Entrada, DoD e limites

Antes de iniciar: integrar PR #9 corrigido; Review/Retro da Sprint 1; aprovação
explícita do novo plano/capacidade; modelo configurado e uso autorizado. Serviços
pagos/pesquisa externa exigem autorização específica; a proposta não presume gastos.
Aplicar DoD do projeto, CI e revisão/integração. Versionar alterações incompatíveis
de IR com migração; manter snapshots originais e metadados de revisão íntegros.

Fora desta sprint: geração completa de prompts/skills (005), learning runtime
(015/016), agentes especializados (017), pesquisa web completa (009), eval sandbox
genérico (008), instalação/rollback (012) e execução distribuída. O adapter mínimo
de estudo não declara essas histórias concluídas.

## Artefatos e controle

planning/sprint-2.json registra status approved, gates e seleção AHC-019/020;
sprint-2.work-items.json detalha oito etapas. TaskGraph registra oito ondas de
precedência, sem executar tarefas ou prometer agenda. Branches propostas:
feat/ahc-019-project-understanding e feat/ahc-020-harness-blueprint-packs.

```sh
factory tasks project-definition --select ahc-019 ahc-020 --completed ahc-001 ahc-002 ahc-003
python scripts/generate_sprint_plan.py --sprint sprint-2 --check
```

PR #10 é atualizado em lugar de criar um plano concorrente. A revisão anterior
permanece no Git e na memória. O escopo refeito está aprovado, sem inferir início.
A [estrutura operacional](sprint-2-execution.md) detalha 21 subtarefas, evidências,
matriz de demonstração e responsabilidades; readiness e issues constam no manifesto.
