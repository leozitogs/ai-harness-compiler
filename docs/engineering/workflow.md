# Commits, branches e revisão

Adotamos branches curtas derivadas de `main`, revisadas por PR, com squash merge.
Esse fluxo usa a base do [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow).
`develop`, branches por sprint e release branches permanentes não são necessários
para a cadência inicial. Sprint é uma organização de trabalho, não uma linha de código.

## Branches

Formato: `<tipo>/<ahc-NNN|infra>-<resumo-kebab-case>`.

```text
feat/ahc-001-canonical-intake
fix/ahc-004-partial-output
docs/infra-kickoff
ci/infra-required-checks
```

Tipos: feat, fix, docs, refactor, perf, test, build, ci, chore. Usar `infra` para
manutenção transversal sem história de produto. Dependabot tem exceção de naming.
Uma branch deve entregar um incremento revisável; evitar acumular uma sprint inteira.

## Commits e título do PR

Seguir [Conventional Commits 1.0](https://www.conventionalcommits.org/en/v1.0.0/):

```text
feat(intake): reject duplicate YAML keys
fix(compiler): preserve existing output on write failure
test(planning): reject cyclic task graphs
docs(scrum): define sprint goal and completion criteria
feat(ir)!: version the domain profile contract
```

Cabeçalho em inglês, até 100 caracteres; escopo opcional e concreto.
Tipos admitidos: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.
Descrever motivo e impacto no corpo quando necessários; referenciar `Refs: AHC-001`.
Mudanças incompatíveis usam `!` ou footer `BREAKING CHANGE:` e documentam migração.
O checker valida o cabeçalho, não prova correção do corpo ou da semântica da mudança.

O título do PR segue a mesma convenção porque será o commit de squash. `feat` e
`fix` descrevem comportamento; não usar `chore` para esconder mudanças de produto.

## Verificação automatizada

```sh
git config core.hooksPath .githooks
uv run python scripts/check_conventions.py --branch feat/ahc-001-canonical-intake
uv run python scripts/check_conventions.py --message "feat(intake): validate source limits"
```

`commit-msg` valida commits locais. O workflow Conventions valida headers, título
de PR e nome da branch no GitHub. Hooks locais podem ser desabilitados; a CI é a
verificação compartilhada. CODEOWNERS identifica @leozitogs como responsável inicial.

## Política de integração

- `main` deve passar CI; não fazer force push nem apagar a branch.
- PR apresenta problema, escopo, evidências, riscos, compatibilidade e vínculo ao backlog.
- Preferir squash; excluir a branch integrada. Não reescrever branches compartilhadas.
- Rebase local é aceitável antes de compartilhar; depois, coordenar qualquer reescrita.
- Não marcar testes de produto gerado como aprovados apenas porque o compilador passou.
- A publicação inicial é a exceção de bootstrap por push direto; evoluções passam por PR.

Com um único mantenedor, não exigir autoaprovação impossível. Exigir CI e resolução
de conversas; quando houver segundo revisor, configurar ao menos uma aprovação.
Proteção remota é uma configuração do GitHub, não consequência automática deste arquivo.

## Releases

Tags `vMAJOR.MINOR.PATCH` após gates e changelog. `0.x` permanece experimental;
mudanças incompatíveis ainda devem ser explícitas. A versão do pacote e as versões
de contratos são independentes: alterar um schema incompatível exige migração,
mesmo sem major do pacote. Publicação de pacotes não é automática nesta fase.
