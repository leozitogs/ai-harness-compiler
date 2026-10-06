# Sprint 1 — Confiança na entrada e nas evidências

Planejamento atualizado em **2026-10-06**. Timebox proposto: **dez dias úteis**.
Estado: planejada, execução ainda não iniciada. Data inicial e capacidade permanecem
em aberto; D1 a D10 indicam ordem relativa de trabalho, não eventos agendados.

**Sprint Goal:** tornar a entrada, o perfil de domínio e as evidências verificáveis,
medindo a confiabilidade da baseline offline.

## Incremento esperado

Uma definição de projeto válida entra no compilador, gera uma representação
canônica com domínio/incógnitas e proveniência, e produz um bundle reprodutível.
Entradas inválidas e falhas de escrita têm diagnósticos estáveis. A Review demonstra
o caminho em educação, comércio e ferramentas de desenvolvimento, com medições reais.

O baseline atual tem 82 testes aprovados, contratos centrais, compilador, equipe
de preparação e memória de engenharia. As quatro histórias abaixo ampliam essa
base; sua existência não implica que os novos critérios já foram atendidos.

## Sprint Backlog e trabalho concreto

| História | O que implementar | Critério de entrega |
|---|---|---|
| AHC-001 — Intake | Loader seguro com limite de tamanho, rejeição de chaves duplicadas, validação de versão/UTF-8 e diagnóstico estável | Casos válidos aceitos; duplicatas, input excessivo e versões desconhecidas rejeitados em Linux/Windows |
| AHC-002 — Domínio | Perfil multidimensional tipado: domínio, arquétipo, dados, risco, origem e hipóteses/incógnitas | Invariantes de declaração/hipótese/incerteza, confiança não inventada e compatibilidade/migração demonstrada |
| AHC-003 — Evidências | Source registry/Evidence Pack: IDs, origem, digest quando aplicável, coleta, estado e vínculo à decisão | Referências ausentes/duplicadas/incompatíveis rejeitadas; declarações e pesquisa não verificada diferenciadas |
| AHC-004 — Confiabilidade | Três fixtures de domínio, injeção de falhas de escrita e benchmark offline reproduzível | Falhas preservam conteúdo existente; benchmark registra duração, tamanho, versão e método de medição |

Critérios canônicos: `project-definition/project.yaml`. Escopo alvo: quatro histórias.
Sem capacidade e velocity conhecidas, a seleção é uma previsão para Planning, não
uma promessa de prazo. AHC-001 e a proveniência são os primeiros gates técnicos;
não reduzir validação ou compatibilidade para fazer caber mais trabalho.

## Decisões técnicas do Planning

- Definir limite inicial do manifesto e forma de configurá-lo; proposta: 1 MiB.
- Definir política para referências locais, aliases e profundidade do YAML sem ingestão de assets.
- Acordar uma representação comum de origem/IDs entre domínio e Evidence Pack antes de desenvolver contratos separados.
- Escolher versionamento e adaptação dos contratos afetados; preservar exemplos existentes e demonstrar migração.
- Separar timestamps operacionais de dados que entram na IR reproduzível.
- Definir a estratégia para falha de escrita sem sobrescrever ou remover arquivos de outros projetos.

Essas decisões são propostas de implementação a concluir na etapa de design;
registrar escolhas locais em DE e mudanças arquiteturais em ADR.

## Ordem de execução proposta

| Dias relativos | Trabalho | Checkpoint de revisão |
|---|---|---|
| D1 | Refinar critérios, interfaces de contratos, limites e plano de testes | Critérios e decisões técnicas compreendidos; branches definidas |
| D2–D3 | Entregar AHC-001 e seus testes negativos | Intake robusto integrado com CI verde |
| D4–D5 | Entregar AHC-003; alinhar o design de AHC-002 | Evidência chega ao pipeline com origem e referências validadas |
| D6–D7 | Entregar AHC-002 e demonstrar compatibilidade/migração | Perfil de domínio explícito sem certeza fabricada |
| D8–D9 | Entregar AHC-004, integrar fixtures e medir baseline | Três domínios, falhas de escrita e relatório de benchmark |
| D10 | Demo, Review e Retrospective | Aceite do incremento e uma melhoria do processo registrada |

Essa sequência é uma previsão por dependências. Se a capacidade real não comportar
o conjunto, renegociar escopo com o PO; não deixar a verificação para o último dia.
Preparação de fixtures e design de domínio podem ocorrer antes, mas o benchmark
final e a demonstração usam os contratos integrados.

## Responsabilidades

| Participante | Responsabilidade na sprint |
|---|---|
| Leonardo — PO | Prioridade, exemplos/limites de domínio, decisões de escopo e aceite de valor |
| Colaborador de código/Codex | Implementação, regressões, atualização de schemas/docs e PRs |
| Clara | Apoio ao refinamento e identificação de lacunas nos requisitos |
| Atlas | Apoio a contratos, fronteiras e compatibilidade |
| Ícaro | Apoio à decomposição e ordem das mudanças |
| Vera | Apoio à matriz de aceitação e evidências de qualidade |
| Sentinela | Apoio à análise de input, dados, permissões e efeitos |
| Nexo | Apoio à consolidação de progresso, dependências e impedimentos |

Os agentes atuais produzem análises e planos; a implementação de código é uma
atividade do colaborador de código. Seus relatórios não substituem execução de
testes, revisão técnica ou accountability humana. Um segundo revisor independente
continua uma decisão de formação da equipe.

## Tarefas e controle de progresso

`planning/sprint-1.json` define o escopo. `planning/sprint-1.tasks.json` mantém
16 estágios técnicos com oito ondas de precedência. O novo
`planning/sprint-1.work-items.json` detalha ações, entregáveis e papéis por estágio,
incluindo coordenação adicional entre evidências, domínio e benchmark.

```sh
uv run factory tasks project-definition --select ahc-001 ahc-002 ahc-003 ahc-004
uv run python scripts/generate_sprint_plan.py --check
uv run --extra team factory team run project-definition --request "Apoiar Planning da Sprint 1" --output output/sprint-1-planning
```

Fluxo: Planned → In progress → In review → Done; Blocked registra causa e ação
para desbloqueio. Começar com uma história de implementação ativa por executor.
Branches propostas: `feat/ahc-001-canonical-intake`, `feat/ahc-003-evidence-pack`,
`feat/ahc-002-domain-profile`, `test/ahc-004-compiler-reliability`.

## Definition of Done e roteiro da Review

Aplicar a [DoD do projeto](scrum.md): critérios com evidências, CI obrigatória,
revisão e integração, contratos/docs atuais, segurança e compatibilidade avaliadas.
Quantidade de testes, isoladamente, não aprova o incremento.

Na Review, demonstrar:

1. Manifesto válido aceito e duplicata/input excessivo/versão inválida diagnosticados.
2. Perfil declarado e caso incerto, sem confiança fabricada.
3. Fonte rastreável e rejeição de referência quebrada.
4. Builds das três fixtures, integridade e comparação de bytes para a mesma IR.
5. Falha de escrita simulada, proteção de conteúdo existente e benchmark com método/resultado.
6. Uma experiência relevante registrada como INC e, após evidência/revisão, LES.

## Riscos, limites e próximos passos do PO

Riscos principais: mudanças acopladas de contratos, migração maior que o previsto,
capacidade desconhecida e falsa sensação de cobertura por testes estruturais.
Mitigar com design comum, exemplos pequenos, regressões e demo por critério.

A sprint desenvolve o core offline. API, Temporal, execução distribuída, providers
pagos e geração de memória/especialistas para projetos alvo seguem nos marcos futuros.

Para iniciar, o PO precisa confirmar o Sprint Goal, a capacidade disponível e a
data inicial; definir o padrão de aceite e validar os três exemplos fictícios de
domínio. Este planejamento não muda automaticamente o estado para execução.
