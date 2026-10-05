# Fundamentos de engenharia e escalabilidade

## Fronteiras e desenho

Começar como monólito modular. Contratos de domínio e transformações puras não
dependem de CLI, API, banco, rede, Temporal ou SDK de modelos. Adapters convertem
I/O em contratos, e o control plane compõe operações com políticas explícitas.
Extrair serviços somente quando medições, isolamento ou ownership justificarem.

Cada mudança deve declarar requisito, invariantes, modos de falha, estratégia de
teste e observabilidade. Interfaces públicas precisam de erros e compatibilidade
documentados. Não adicionar abstrações sem consumidor ou duplicação concreta.

## Mapa de organização

| Diretório | Responsabilidade e fonte de verdade |
|---|---|
| `src/ai_harness_compiler/models/` | Contratos versionados e invariantes |
| `src/ai_harness_compiler/` | Intake, transformações, planejamento, compilação e CLI |
| `schemas/` | Saída gerada; não editar manualmente |
| `project-definition/` | Definição do próprio produto e critérios canônicos do backlog |
| `planning/` | Seleção de sprint e grafo gerado; nenhum estado de execução fictício |
| `docs/product/` | Concepção, priorização e contexto de negócio |
| `docs/delivery/` | Kickoff, Scrum e Sprint 1 |
| `docs/engineering/` | Processo, licenciamento e decisões operacionais |
| `docs/adr/` | Registro de decisões e consequências |
| `tests/` | Evidência automatizada do comportamento do compilador |
| `examples/` | Fixtures demonstráveis, sem dados reais |
| `.github/`, `.githooks/`, `scripts/` | Verificações e automação do repositório |

Novos adapters serão adicionados apenas quando implementados; diretórios vazios
não representam capacidades prontas. Código, documentação e contratos evoluem no mesmo PR.

## Qualidade e testes

- Unitários para invariantes e transformações; contrato para compatibilidade e referências.
- Integração para filesystem, adapters e serviços; ponta a ponta para CLI e bundles.
- Cenários negativos: IDs, ciclos, fontes ausentes, timeout, input excessivo e escrita parcial.
- Fixtures offline de múltiplos domínios; reservar datasets para evals de generalização.
- Proteger dados do usuário e impedir regressões de determinismo e isolamento.

Gates atuais: Ruff, mypy, pytest, schemas, política gerada, plano da sprint e build,
em Python 3.12/3.13 e Linux/Windows na CI. Não adotar um percentual de cobertura
como substituto para avaliar risco; medir cobertura quando houver política calibrada.

## Estratégia de escala por estágio

| Estágio | Medição e evolução | Gate antes de avançar |
|---|---|---|
| CLI offline | Tamanho do manifesto, tempo e memória do build, número de nós | Limites e benchmark reprodutível |
| Worker durável | Fila, tentativas, orçamento, latência por etapa | Retomada e idempotência comprovadas |
| Multi-projeto | Quotas, backpressure, concorrência limitada por projeto | Testes de autorização e isolamento |
| Busca arquitetural | Custo por experimento, ganho sobre baseline, taxa de falhas | Holdout, budgets e condições de parada |

PostgreSQL e object storage guardarão estado e artefatos; payloads grandes não
devem circular indiscriminadamente entre workers. Referências devem carregar
digest, versão e escopo de projeto. Redis, índices vetoriais e cache só após
medir necessidade. Cache exige chave por versão de input, compilador, política
e tenant, além de invalidação e proteção contra vazamento entre projetos.

## Confiabilidade e operação futuras

Efeitos externos exigem chaves de idempotência, timeout, retries limitados com
backoff e compensação quando aplicável. Retries não podem amplificar custos sem
limite. Aprovações expiram e vinculam identidade, ação, argumentos e versão do plano.

Instrumentar spans por etapa e métricas de sucesso, falha, latência e custo.
Estabelecer SLOs após benchmark e perfil de uso; nenhum número é anunciado como
atingido antes de medição. Antes de operação multi-projeto: backup/restore testado,
retenção, runbooks, health checks, migrações e recuperação de jobs.

## Segurança e supply chain

Schemas não tornam texto confiável. Separar dados e instruções, limitar tamanho,
validar caminhos e aplicar permissões fora do LLM. Não executar ferramentas ou
código gerado durante compilação. Secrets ficam fora do Git e dos traces.

Versionar lockfile, revisar atualizações e licenças, usar permissões mínimas em CI
e actions fixadas por SHA. Antes da primeira release distribuída: inventário de
dependências, SBOM e verificação de vulnerabilidades com triagem documentada.
