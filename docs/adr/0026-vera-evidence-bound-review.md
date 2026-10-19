# ADR-0026 — Vera executável com evidências e parecer de encerramento

Status: aceito para implementação; AHC-030, 2026-10-19.

## Decisão

Adicionar contratos independentes de provider/framework: `QAReviewRequest/v1`,
`QAInspection/v1`, `QACheckResult/v1`, `QAReviewReport/v1`,
`QAReviewComparison/v1` e `SprintClosureAssessment/v1`. A requisição vincula
snapshot, base/head Git, autoria declarada, fontes UTF-8, diff e seus hashes.
O pacote é limitado a 32 arquivos, 64 KiB por arquivo/diff e 256 KiB no conjunto.
Paths são explícitos, em allowlist de fontes; `.git`, credenciais e memória bruta
não são ingeridos como código. Fontes/diff omitidos ficam visíveis no escopo.

O host separa três atividades: captura, checks e inspeção. Checks usam comandos
fixos e somente executam após o operador confiar explicitamente no head. Conteúdo
de source/issue/asset nunca fornece comando executável. Execução de testes pode
executar código/plugins do projeto, portanto esse runner não é um sandbox para
repositórios hostis. O modo padrão não executa checks e não chama modelos.

A inspeção opcional usa uma tentativa, sem fallback, por Codex CLI existente ou
Ollama loopback. O modelo retorna apenas hipóteses citadas e cobertura declarada;
não pode fornecer sucesso de checks, aceite ou decisão de fechamento. Citações
precisam corresponder a paths, linhas e trechos literais, além de critérios reais.
Isso verifica localização, não a correção semântica do achado. A separação entre
inspeção estruturada e validação executada segue também o [exemplo oficial de
review e repair](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex).

## Pareceres e integração

O relatório recalcula recomendação, cobertura ausente e matriz literal de critérios.
Falha de check ou hipótese P0/P1 gera `changes-required`; evidência/inspeção ausente,
P2/P3 pendente ou diff incompleto gera `inconclusive`. `ready-for-po` apenas indica
pacote disponível para revisão humana, nunca entrega validada. Aceite por critério
permanece `not-established` em todos os casos.

Nexo recebe `SprintClosureAssessment`, com objetivo, bloqueios, checks e carryover.
`full_delivery_established=false`, `sprint_closed=false` e autoridade `none` são
constantes. O adapter `team` reutiliza Vera/Nexo, ferramentas existentes e checkpoint
SQLite/LangGraph. `TeamRun/v1` recebe campo opcional aditivo `qa_report`; quando
presente, deve compartilhar exatamente o snapshot da sessão. O digest do relatório
fica vinculado ao checkpoint. Revisão persistente revalida head, fontes, diff,
freshness e contexto/memória antes de aceitar somente o relatório.

Comparação entre revisões só registra falha de check superada quando um novo head,
sob os mesmos critérios, apresenta o mesmo check aprovado. Desaparecer um achado
do texto do modelo não comprova correção: achados anteriores continuam pendentes
de verificação. Não há waiver automático de P2 ou resolução semântica por CI verde.

## Limites e rastreabilidade

Hashes verificam consistência, não autenticidade do produtor. Autoria e reviewer
são papéis declarados, sem autenticação nem independência estatística garantida.
Somente o runner confiável produz observações de execução; arquivos importados
não são uma atestação assinada. O modelo não recebe essa interface de produção.

Git é somente leitura, sem fsmonitor, ext-diff/textconv no diff e com limites de
saída/tempo; alterações ou fonte não regular invalidam o pedido. Repositórios Git
SHA-1 e arquivos presentes no head são o escopo inicial; deleções não capturadas
ficam em excluded_paths. Runner tenta terminar a árvore de processos ao exceder
budget; não isola código hostil nem garante latência rígida de todo o sistema.

Ollama usa timeout por operação de rede e limite de resposta; não há promessa de
SLA total da chamada HTTP. Falha de inspeção registra tentativa e quantidade real
de chamadas desconhecida, sem inventar zero ou qualificação. Nenhum prompt privado
ou raciocínio privado é registrado; dados de projeto e outputs autorizados são
artefatos locais de engenharia, não memória automaticamente promovida a LES.
