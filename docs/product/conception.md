# Concepção do AI Harness Compiler

## Problema e oportunidade

Equipes repetem decisões de contexto, ferramentas, prompts, políticas e avaliação
a cada projeto de IA. Arquivos gerados sem especificação intermediária dificultam
revisão, evolução e comparação de arquiteturas. O produto deve reduzir esse trabalho
preservando controle e explicabilidade das decisões.

## Product Goal

Permitir que uma equipe transforme a definição de um projeto em um harness de
engenharia de IA específico, rastreável e verificável, e consiga evoluí-lo com base
em evidências sem perder controle sobre custos, permissões e compatibilidade.
Cada projeto alvo deverá receber sua memória de engenharia e especialistas de
domínio, com ferramentas e avaliação, conforme o [pipeline de geração](project-generation-pipeline.md).

## Usuários e jornadas

| Usuário | Trabalho a realizar | Evidência de valor |
|---|---|---|
| AI engineer | Sair do backlog para contratos e estrutura de trabalho | Bundle compilado e critérios rastreáveis |
| Tech lead | Revisar decisões e controlar complexidade | IR, alternativas, ADRs e riscos explícitos |
| Product Owner | Conectar funcionalidades a critérios de sucesso | Backlog ordenado, incrementos e evals |
| Operador futuro | Executar e evoluir harnesses de vários projetos | Traces, budgets, isolamento e rollback |

Jornada inicial: preparar manifesto → validar → revisar DNA/grafo/IR → compilar →
verificar integridade → revisar plano de trabalho. Adoção em runtime e instalação
automática são jornadas futuras, sujeitas a gates próprios.

## Escopo por horizonte

Agora: contratos, CLI, planos verificáveis e compilação offline. Próximo incremento:
intake robusto, domínio explícito, Evidence Pack e benchmark. Depois: síntese tipada,
context engine, policy engine, eval runner, adapters, orquestração durável e pesquisa.
Busca de arquitetura e autoevolução dependem de avaliações confiáveis.
AHC-015 a AHC-018 especificam a geração da documentação permanente, captura de
desafios/soluções e agentes especializados. Sua entrega será avaliada em domínios
distintos; a implementação interna do compilador é uma referência inicial.

Não faz parte da Sprint 1: UI, SaaS multi-tenant, infraestrutura Kubernetes,
agentes autônomos, chamadas pagas, execução distribuída ou aprendizado automático.

## Hipóteses a validar

1. Modelar antes de gerar reduz decisões implícitas e retrabalho de revisão.
2. Uma baseline sem agentes atende parte relevante das necessidades iniciais.
3. Evidências e evals permitem comparar harnesses de maneira útil ao usuário.
4. O custo de manter contratos é compensado por reprodutibilidade e evolução segura.

Ainda não há validação com clientes ou métricas de adoção. Entrevistas e pilotos
devem testar essas hipóteses antes de comprometer a arquitetura com uma oferta SaaS.

## Métricas e escalabilidade

Medir tempo até um bundle revisável, erros identificados antes de emissão,
cobertura de critérios, esforço de revisão, falhas, latência, custo e reuso.
A Sprint 1 produz baseline de desempenho; metas quantitativas surgem depois.
Escala por volume de projetos exige jobs isolados, quotas, backpressure e estado
durável; escala por complexidade exige contratos e decomposição de dependências.

## Riscos e decisões abertas

Riscos: expansão de escopo, classificação errada, avaliação superficial, prompt
injection, custo de busca e contaminação entre projetos. Mitigações: roadmap com
gates, incógnitas explícitas, holdouts, policy engine e separação de dados.
Em aberto: provedor inicial, benchmark de qualidade, capacidade da equipe e canal
de feedback de usuários. Apache-2.0 e monólito modular são as decisões iniciais.
