# Contratos e representação intermediária

Os modelos Python em `src/ai_harness_compiler/models/` são a fonte de verdade.
Os JSON Schemas em `schemas/` são gerados e versionados.

| Contrato | Responsabilidade |
|---|---|
| `ProjectInput/v1` | Identidade, concepção, domínio opcional, branding, backlog, constraints, assets |
| `ProjectDNA/v3` | Input preservado, perfil multidimensional, fontes e evidências, incógnitas |
| `CapabilityGraph/v1` | Capacidades, dependências, I/O, risco, efeitos, critérios e evidências |
| `HarnessSpec/v3` | DNA + grafo + decisões com escopo + contexto + permissões + planos de eval |
| `DomainProfile/v1` | Domínio, arquétipo, dados, risco e classificação fornecida |
| `EvidencePack/v1` | Fontes, origem, integridade, verificação declarada e afirmações |
| `TaskGraph/v1` | Seleção de capacidades, estágios técnicos, precedência e critérios |

## Manifesto de entrada

`factory` aceita o arquivo YAML ou o diretório que contém `project.yaml`.
Campos obrigatórios: `id`, `name`, `conception`, `backlog`. Cada item do backlog
precisa de ID, título, descrição e pelo menos um critério de aceitação.
Campos desconhecidos são rejeitados para revelar erros de digitação.
O [intake limitado](engineering/intake.md) rejeita duplicatas, aliases/merges e
estruturas excessivas antes da validação; seu limite padrão é 1 MiB configurável.
Strings vazias e IDs fora de `[a-z][a-z0-9_-]{0,63}` são inválidos.

Branding tem audiência, tom, princípios e restrições visuais. Constraints preserva
restrições técnicas, de segurança, de negócio e limite de custo do build.
O build atual não consome serviços pagos. Limites não constituem um budget engine.

Assets contêm caminho e descrição como metadados. O MVP não valida existência,
copia arquivos, segue URLs ou extrai seu conteúdo. Adapters de documentos e mídia
deverão ser adicionados com limites de tamanho, proveniência e validação de caminhos.

## Invariantes

- IDs de backlog e capacidades são únicos.
- Dependências existem, não se repetem e formam um DAG acíclico.
- Uma capacidade corresponde a um item de backlog nesta versão.
- Grafo e DNA pertencem ao mesmo projeto; conteúdo das capacidades preserva a origem.
- IDs de evidência, decisão e eval são únicos dentro de cada registro.
- Referências de evidência e capacidade precisam resolver.
- Todo critério de aceitação tem pelo menos um plano de avaliação correspondente.
- Nenhum critério de aceitação é declarado aprovado sem execução.
- Permissões da baseline não permitem rede durante compilação ou execução de código gerado.

O schema valida estrutura e tipos; invariantes entre campos e validação de grafos
são adicionais e executadas por Pydantic. Um validador genérico de JSON Schema
não substitui `factory validate` ou a validação de `HarnessSpec`.

## Evidência e incerteza

Fontes `project.yaml#/...` são localizadores lógicos no manifesto canônico, mesmo
quando o arquivo físico tem outro nome. O domínio informado recebe `declared` e
confiança nula: a certeza da classificação não foi medida. Sem domínio, o status
é `DOMAIN_UNCERTAIN`; o compilador não simula classificação por LLM.

O [Evidence Pack](engineering/evidence-pack.md) detalha fonte canônica, pesquisa
fornecida e escopos. O [perfil de domínio](engineering/domain-profile.md) detalha
estados e migração explícita das IRs v1/v2 para v3.

`implementation` registra a estratégia declarada (`undecided`, `deterministic`,
`llm`, `rag` ou `agent`). Selecionar `rag` ou `agent` não cria esses runtimes.

## Reprodutibilidade e alterações

Mesma IR e mesma versão do compilador produzem os mesmos bytes, sem timestamps
ou caminhos absolutos na saída. O manifesto registra versão do compilador, digest
da IR e hashes dos arquivos. Ele não assina artefatos nem é prova contra adulteração
maliciosa de arquivos junto com o manifesto.

Antes da primeira release, esses contratos são experimentais. Mudanças incompatíveis
devem criar nova versão de schema e documentar migração; nunca reinterpretar
silenciosamente uma IR publicada. Gerar novamente com:

```sh
uv run python scripts/export_schemas.py
```
