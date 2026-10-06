# Visão do produto

O AI Harness Compiler transforma a definição de um novo projeto em um sistema
de engenharia de IA específico, versionado, avaliável e evolutivo.
Seu produto final é um harness completo, não apenas uma resposta de LLM ou um agente.

## Entradas e saídas desejadas

Entrada: branding, backlog, concepção, assets, restrições e requisitos técnicos.
Saída: arquitetura do produto e de IA, AGENTS.md, sistema de contexto, prompts,
skills, tools, MCP, agents, workflows, guardrails, evals, hooks, observabilidade,
políticas de desenvolvimento, CI, documentação e critérios de evolução.
Isso inclui um sistema executável de documentação e aprendizado para o projeto
alvo, e especialistas de domínio com competências, ferramentas e evals próprias.

O compilador não deverá pressupor que toda capacidade precisa de IA. Código
determinístico, workflows fixos, LLMs, retrieval e agentes são alternativas a
comparar com evidências. Zero agentes é uma saída válida.

## Pipeline alvo

1. Intake e normalização de fontes com proveniência.
2. ProjectDNA com propósito, usuários, domínio, riscos e incógnitas.
3. Perfil multidimensional: domínio, arquétipo, dados, risco, interação e operação.
4. Pesquisa direcionada e Evidence Pack, com origem, confiança e atualidade.
5. Compilação de requisitos, critérios de avaliação e CapabilityGraph.
6. Busca de arquiteturas candidatas sob limites de custo e complexidade.
7. HarnessSpec como IR versionada; validação anterior à emissão.
8. Compilação de artefatos de desenvolvimento/runtime, memória de engenharia e especialistas de domínio.
9. Simulação, avaliações de saída e trajetória, regressão e reparo limitado.
10. Aprovação e instalação com diff, rastreabilidade e rollback.
11. Observação, classificação de falhas, proposta de evolução e nova avaliação.

O ciclo de aprendizado gera INC e, após regressão e revisão, LES com evidência,
aplicabilidade e limites. O [pipeline por projeto](product/project-generation-pipeline.md)
detalha essa modalidade e a geração de agentes aprofundados.

## Princípios

- A especificação formal precede a geração de arquivos.
- Toda decisão substantiva deve ter evidência e alternativas explícitas.
- Inferências incertas permanecem hipóteses; domínio ausente não é inventado.
- Critérios de avaliação surgem dos requisitos antes da busca arquitetural.
- O contexto é selecionado por relevância, proveniência, confiança e orçamento.
- Memória é promovida sob demanda, sem despejar históricos inteiros no prompt.
- Workflows têm controle por software; agentes possuem decisões dinâmicas pelo modelo.
- MCP é uma fronteira de integração, sem assumir controle do core.
- Permissões, budgets e condições de parada pertencem ao control plane.
- Evolução exige regressão, revisão e aprovação; sem autoalteração irrestrita em produção.

## Critérios de sucesso futuros

Medir qualidade do harness em tarefas do projeto, cobertura de requisitos,
correção no uso de ferramentas, falhas, custo, latência e complexidade.
Comparar candidatos no mesmo conjunto de tarefas, com splits que evitem otimizar
sobre o conjunto de teste. Selecionar soluções pela fronteira de Pareto conforme
as restrições do projeto, sem declarar uma arquitetura universalmente melhor.

As referências acadêmicas presentes na concepção original são insumos para uma
futura revisão bibliográfica. Este scaffold não depende de suas alegações nem
assume que resultados de benchmarks se transferem automaticamente para o produto.
