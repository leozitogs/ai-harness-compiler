# Arquivo de mudanças funcionais

A segunda fatia de AHC-031 conserva versões completas de uma mudança, incluindo
fontes, regras, perguntas, requisitos e exemplos. Cada versão pode receber seu
próprio parecer. A ferramenta usa os contratos da primeira fatia e funciona offline.
Consulte o [guia do contrato](functional-change.md) e a [decisão de armazenamento](../adr/0037-functional-change-archive.md).

Crie um diretório dedicado dentro da raiz indicada, por exemplo
`.factory/change-archive`. Use armazenamento local com suporte a hard links
e mantenha fontes de projeto privadas em diretório ignorado pelo Git.

```sh
uv run python scripts/archive_functional_change.py --archive .factory/change-archive append --input examples/functional-change/change.json --expected-head empty
uv run python scripts/archive_functional_change.py --archive .factory/change-archive history
uv run python scripts/archive_functional_change.py --archive .factory/change-archive show --revision 1
```

`append` imprime o digest da versão criada. Para registrar a próxima, prepare um
`FunctionalChange/v1` com a mesma identidade e número incrementado, e informe o
digest corrente em `--expected-head`. Se outro operador publicar primeiro, confira
`history` antes de preparar a próxima revisão. `show` sem `--revision` inspeciona
o topo e devolve um relatório de prontidão com o conteúdo daquela versão.

Para registrar uma declaração humana, forneça seu JSON no formato
`FunctionalChangeReview/v1`.

```sh
uv run python scripts/archive_functional_change.py --archive .factory/change-archive review --input .factory/change-review.json
```

Projeto, mudança, versão e digest devem corresponder ao snapshot. Uma versão
bloqueada admite registro de rejeição e continua com prontidão `blocked`.
`show` expõe tanto o bloqueio quanto a decisão. Cada declaração fica vinculada
à versão original. Uma versão nova começa sem parecer, mesmo quando a alteração
é editorial. O worklog de preparação permanece separado e os locators aparecem
como `not-run`.

Entradas e arquivos persistidos têm limite individual de 1 MiB. Em conflito ou
erro de armazenamento, consulte `history` antes de repetir a operação. O CLI
usa um diretório dedicado, com acesso controlado pelo operador. Guarde o digest
do topo separadamente quando precisar detectar rollback.

O incremento entrega a sequência local de revisão e arquivamento. A importação
semântica, a avaliação com projetos reais e a execução de testes de negócio
seguem na esteira de AHC-031.

O contrato da primeira fatia precede a persistência descrita no ADR-0037.
A validação do CLI cobre conflito de gravação, vínculo entre revisões, rejeição
de parecer incompatível e consulta histórica após publicar uma nova versão.
