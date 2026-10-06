# Roadmap

## M0 — Fundação executável (este scaffold)

Contratos centrais, intake estruturado, pipeline puro, grafo validado, baseline IR,
compilador local, evidências, planos de evals, hashes, CLI, exemplo, testes e CI.
Critério: exemplo compila sem credenciais; resultados reproduzíveis; entradas
inválidas falham antes da emissão; a CI verifica contratos e artefatos.

## M1 — Project Intelligence

Adapters separados de branding, backlog, concepção e assets; normalização semântica,
taxonomia multidimensional, classificação com evidências e múltiplas hipóteses.
Criar adapter de LLM substituível e fixtures determinísticas para testes.
Critério: projeções rastreáveis às fontes, benchmark rotulado, tratamento explícito
de baixa confiança e limites de custo aplicados por software.

## M2 — Harness IR e compiladores especializados

Contratos para contexto, memória, prompts, skills, tools, MCP, agents e workflows;
validadores cruzados; progressive disclosure; policies independentes do modelo.
Inclui AHC-015 a AHC-017: DocumentationLearningSpec, compilador de documentação/memória
por projeto e AgentSpec com competências, ferramentas e critérios de domínio.
Critério: harnesses de dois domínios diferem por requisitos, com caso válido de zero agentes;
tool schemas, permissões, budgets, condições de parada e evals definidos antes de runtime.

## M3 — Execução durável e Simulation Lab

API FastAPI, persistência, workflows Temporal, runtime via adapters, Policy Engine,
aprovação humana, isolamento, observabilidade OpenTelemetry e execução de evals.
Critério: tarefas retomam após falhas; efeitos externos respeitam permissões;
evals verificam resultado e trajetória; nenhum PASS apenas por autodeclaração do modelo.
Demonstrar memória e especialistas compilados em dois domínios; AHC-018 conecta
incidente, correção, regressão, lição revisada e recuperação numa tarefa futura.

## M4 — Research e Architecture Search

Evidence Pack, Engineering KB, busca limitada de candidatos, benchmarks compartilhados,
ranking por qualidade/custo/latência/complexidade, regressão e reparo com limites.
Critério: comparar candidatos contra baseline e demonstrar ganhos no conjunto de teste
reservado; respeitar orçamento e critérios de parada; registrar alternativas descartadas.

## M5 — Instalação e evolução controlada

Instalação com diff, detecção de drift, rollback, aprovação e migrações;
Experience Store, biblioteca de skills versionada, otimização de prompts e meta-tools.
Critério: mudanças rastreáveis a falhas/evidências, regressões bloqueiam promoção,
restauração da versão anterior e proteção contra contaminação entre projetos.
Transferência de experiências exige autorização, anonimização e revisão; otimização
ou treinamento é um EXP separado, com avaliação e budgets.

## Geração de equipes e aprendizado por projeto

O [pipeline específico](product/project-generation-pipeline.md) define os contratos,
compiladores e gates. A equipe e a memória internas já implementadas servem de
referência; transformá-las em produto gerado é trabalho de AHC-015 a AHC-018.

## Próximas tarefas concretas

1. Ampliar fixtures de ProjectInput para três domínios e entradas incompletas.
2. Definir ontologia e critérios de confiança para DomainProfile.
3. Projetar EvidencePack e políticas de trust/freshness.
4. Introduzir PromptSpec e SkillSpec com semântica testável.
5. Escolher o primeiro provider adapter e sua suite de avaliação offline.

As fases posteriores dependem dos critérios de conclusão anteriores, sem datas artificiais.
