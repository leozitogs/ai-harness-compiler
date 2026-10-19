# Vera — revisão executável e pacote de review do Nexo

Captura e checks funcionam sem extra de agentes ou rede. `--engine primary` usa a
política central; LangGraph/Vera/Nexo requerem `--team` e o extra `team`. O modo
local padrão registra checks não executados e cobertura semântica desconhecida.

## Operação

Trabalhar com revisão Git limpa. Salvar artefatos em diretório ignorado (`.factory/`)
ou fora do checkout. Recolher um snapshot recente com `factory scrum observe` e
selecionar explicitamente os arquivos a inspecionar:

```sh
factory qa capture --repository . --snapshot .factory/snapshot.json --base BASE_SHA --head HEAD_SHA --author engineer --source src/example.py --source tests/test_example.py --output .factory/qa-request.json
factory qa run .factory/qa-request.json --repository . --output .factory/new-qa
```

Base/head devem ser hashes completos de commits existentes. Captura inclui conteúdo
atual e diff dos paths escolhidos; arquivos omitidos continuam explícitos. Assets,
hooks e scripts recebidos do input não são executados. A flag de confiança abaixo
é para código local conhecido, não fornece isolamento de projetos externos:

```sh
factory qa run .factory/qa-request.json --repository . --trusted-checks-at HEAD_SHA --engine primary --team --output .factory/new-qa-team
```

Checks permitidos: lint, format, typing, tests, schemas, repo-policy e sprint-plan.
Cada comando é fixo; o operador não fornece shell ou script livre. Pedido usa
120 segundos por check e 300 segundos de budget por padrão, configuráveis no
contrato dentro dos limites. Saída por check: 32 KiB. Tempo de validação e cleanup
também existe; não são garantias de SLA. Sem confiança no head, todos ficam not-run.

A inspeção usa uma tentativa no provider explícito, com contexto de até 224 KiB.
`--engine codex-cli`/`ollama` e `--model` permitem escolha explícita. Falhas não
trocam de provider; relatório fica inconclusivo, com tentativa registrada e chamada
real desconhecida quando não observável. `--inspection arquivo.json` importa somente
hipóteses consultivas, sob o mesmo contrato de citações, sem executar reproduções.

## Artefatos e revisão humana

O diretório novo contém `qa-report.json`, `closure-assessment.json` e
`incident-candidates.json`. Candidatos registram falhas observadas de checks,
com causa e resolução não estabelecidas; não gravam INC/LES automaticamente.
Com `--team`,
Vera e Nexo executam as três ferramentas permitidas e param no gate persistente:

```sh
factory team review .factory/new-qa-team/team --decision approve --comment "Aprovo somente o relatório"
```

Também é possível iniciar uma sessão a partir de relatório atual:

```sh
factory team run project-definition --qa-report .factory/new-qa/qa-report.json --repository . --output .factory/new-review-team
factory qa assess .factory/new-qa/qa-report.json --repository . --output .factory/new-closure.json
```

O pacote mantém matriz de critérios sem aceite, achados P0–P3, checks reais,
cobertura declarada pelo inspetor e limitações. Citação válida não prova um defeito;
`verification=not-executed` identifica a reprodução proposta pelo modelo. P0/P1
impedem recomendar entrega plena. P2/P3 não são automaticamente aceitos como risco.
Mesmo `ready-for-po` mantém sprint aberta, carryover e autoridade de conclusão ausente.

Para acompanhar uma correção em nova revisão:

```sh
factory qa compare previous.json current.json --repository . --output .factory/new-comparison.json
```

A comparação preserva achados antigos como pendentes, mesmo quando omitidos pelo
modelo. Só declara checks anteriormente falhos agora aprovados sob os mesmos
critérios em um novo head. Esse resultado não equivale a resolução semântica.

### Confirmação de resolução

Preparar um JSON de evidência com `finding_id`, `citations` (path, linha e trecho
literal da revisão atual), `check_ids` aprovados e `rationale`. O achado deve existir
na revisão anterior; a nova revisão deve manter os critérios, inspecionar sua faceta
e executar checks. Citação e CI não comprovam sozinhas a resolução.

```sh
factory qa propose-resolution previous.json current.json --evidence evidence.json --repository . --output .factory/proposal.json
```

O resultado aguarda revisão humana. Somente após uma decisão humana específica,
o operador registra a confirmação ou rejeição com sua identidade declarada:

```sh
factory qa review-resolution .factory/proposal.json --decision confirm --actor HUMAN_REVIEWER --comment "Justificativa da decisão humana" --repository . --output .factory/decision.json
factory qa compare previous.json current.json --resolution .factory/decision.json --team-output .factory/new-resolution-team --repository . --output .factory/comparison.json
```

Vera/Nexo/autores não são revisores de resolução. O ator é autodeclarado em CLI
confiável, sem autenticação; não preencher identidade do PO por iniciativa do agente.
Sem confirmação, achados antigos continuam no parecer combinado do Nexo e P0/P1
continuam bloqueando. O checkpoint vincula a comparação e suas decisões por hash.
Resolução de um achado não aceita história, não encerra sprint e não qualifica modelo.
Ver [ADR-0027](../adr/0027-qa-resolution-evidence-and-human-review.md).

Modificar head, arquivo, diff, snapshot ou contexto de memória invalida reutilização
e aprovação persistente; recolher nova sessão. Registrar bugs confirmados como INC,
com causa/tentativas/resolução; LES exige evidência revisada. O revisor não promove
suas próprias alegações à memória e não realiza escrita GitHub ou encerra sprint.

Ver [ADR-0026](../adr/0026-vera-evidence-bound-review.md). Não há benchmark semântico,
qualificação de modelo ou ganho de performance estabelecido por este incremento.
