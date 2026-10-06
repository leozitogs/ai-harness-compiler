# AHC-001 — Fronteira de entrada

O intake lê somente o manifesto. O limite padrão é **1 MiB em bytes**, incluindo
BOM; a leitura pede no máximo limite + 1 bytes antes de decodificar UTF-8. UTF-8
com BOM é aceito. Assets permanecem referências: não há leitura, cópia, execução,
resolução de URL ou checagem de existência dos assets nesta etapa.

```sh
factory validate project-definition --max-manifest-bytes 1048576
factory build project-definition --output output/new-project --max-manifest-bytes 524288
```

`validate`, `plan`, `tasks`, `build` e `team run` aceitam a opção. A API Python
expõe `load_project(path, max_manifest_bytes=...)`. O limite deve ser inteiro
positivo. `compile` recebe IR JSON e não usa o loader de manifesto.

## Política YAML

- Um documento, com mapping na raiz e chaves textuais em todos os mappings.
- Chaves duplicadas são rejeitadas inclusive em objetos aninhados.
- Aliases e merges são rejeitados; anchors sem uso de alias não expandem dados.
- Até 64 níveis de nós e 50.000 nós, incluindo chaves e valores.
- Construção por SafeLoader; tags desconhecidas ou executáveis são rejeitadas.
- `schema_version` ausente mantém o default `ProjectInput/v1`; versão explícita
  desconhecida é rejeitada, sem tentativa silenciosa de migração.

Os limites de profundidade/nós são fixos nesta versão. O limite de bytes é local
à execução; não alterar os contratos ou adicionar esses parâmetros à IR.

## Diagnósticos

A CLI retorna 1 e escreve `factory: <código>: <mensagem>` em stderr. Erros de
intake omitem valores de entrada e detalhes de caminhos. As causas originais
permanecem encadeadas na exceção Python, destinadas a diagnóstico controlado.

| Código | Motivo |
|---|---|
| INTAKE_LIMIT | Configuração de limite inválida |
| INTAKE_READ | Manifesto não pode ser lido |
| INTAKE_TOO_LARGE | Limite em bytes excedido |
| INTAKE_ENCODING | Bytes não são UTF-8 |
| INTAKE_YAML | Sintaxe, tag ou quantidade de documentos inválida |
| INTAKE_DUPLICATE_KEY | Chave repetida |
| INTAKE_YAML_ALIAS / INTAKE_YAML_MERGE | Alias ou merge proibido |
| INTAKE_YAML_DEPTH / INTAKE_YAML_NODES | Estrutura excede limites |
| INTAKE_YAML_KEY / INTAKE_YAML_MAPPING | Mapping inválido |
| INTAKE_SHAPE | Raiz não é mapping |
| INTAKE_SCHEMA_VERSION | Versão desconhecida |
| INTAKE_CONTRACT | Falha no contrato ProjectInput/v1 |

Esses códigos pertencem ao intake; falhas posteriores do grafo/compilador seguem
seus diagnósticos atuais. Não confundir rejeição de entrada com eval de produto.

## Compatibilidade e verificação

Manifestos válidos existentes continuam aceitos. Entradas antes aceitas com
duplicatas, aliases ou merges devem ser reescritas explicitamente. Assets ainda
são metadados livres; um futuro adapter de leitura/cópia deverá validar caminhos
e isolamento antes de acessar conteúdo.

`tests/test_intake.py` verifica cada classe de rejeição, byte boundary, BOM,
referências locais e ausência de rede/leitura de assets. `tests/test_cli.py`
exercita o fluxo público. A CI executa toda a suíte em Linux/Windows e Python
3.12/3.13; resultado local sozinho não comprova essas quatro combinações.
