# AHC-003 — Proveniência e referências

`EvidencePack/v1` separa **SourceRecord** (origem do material) de **Evidence**
(afirmação e localizador). Fontes têm ID único, localização, origem, SHA-256
opcional, estado de verificação e timestamps quando aplicáveis. Cada afirmação
resolve uma fonte e possui escopo de projeto, domínio ou capacidade.

Origens: `user-declaration`, `external-research`, `compiler-derived`.
Correspondem respectivamente aos tipos `declared`, `research`, `derived`.
Tipos e localizadores incompatíveis com a fonte são rejeitados.

## Entrada e saída

O manifesto `ProjectInput/v1` pode acrescentar `evidence_pack`; manifestos antigos
válidos continuam funcionando. Veja o [exemplo fictício](../../examples/evidence-pack/project.yaml).
URLs são metadados e não são acessadas; não há pesquisa automática, leitura de
assets ou coleta de conteúdo nesta história.

```sh
factory validate examples/evidence-pack
factory build examples/evidence-pack --output output/evidence-demo
factory schema evidence-pack
```

A saída inclui `.ai/evidence/pack.json`, também presente na IR e no contexto.
As evidências declaradas de intenção, domínio e backlog são preservadas; fontes
externas fornecidas acompanham suas afirmações e são vinculadas à capacidade
indicada. Registros rejeitados permanecem para auditoria, mas não sustentam
referências ativas.

## Integridade e limites de confiança

`project-manifest` é reservado à fonte canônica gerada. Seu SHA-256 é calculado
sobre JSON UTF-8 de `ProjectInput.model_dump()`, incluindo defaults, com chaves
ordenadas, sem espaços e sem escape ASCII. Não é hash dos bytes originais do YAML.
O digest é conferido contra o input ao validar a DNA/compilar. Ele prova consistência
desse snapshot, sem provar verdade do conteúdo declarado.

Fontes externas exigem `collected_at` RFC3339 com timezone. Estado `verified`
exige digest, `verified_by` e `verified_at`; a revisão não pode anteceder a coleta.
Estados `unverified`/`rejected` não aceitam metadados de aprovação. Não adicionar
timestamps atuais automaticamente: são valores fornecidos e preservados, mantendo
reprodutibilidade para o mesmo input.

**O compilador valida o contrato dos metadados; não autentica o revisor nem verifica
conteúdo externo ou seu digest.** Um status fornecido como verified não é aprovação
emitida pelo compilador. Recomendação/freshness e validação independente de fontes
pertencem a adapters/evals futuros.

## Compatibilidade de referências

- IDs de fontes/afirmações são únicos; referências precisam resolver.
- Uma evidência de domínio só pode ser citada no perfil de domínio.
- Uma capacidade cita evidências com seu próprio `capability_id`.
- Decisões têm `capability_ids`: evidência específica de capacidade exige esse
  escopo explícito; evidências de projeto/domínio podem informar decisões gerais.
- Referências repetidas, capacidades desconhecidas e fontes rejeitadas são bloqueadas.

Escopo valida compatibilidade estrutural. Não afirma que uma frase textual prova
uma decisão, nem avalia qualidade científica ou causalidade de uma justificativa.

## Introdução na IR v2 e evolução

A AHC-002 evoluiu a IR para v3. O comando migrate agora leva baselines v1/v2
à v3; ver [perfil de domínio](domain-profile.md) para a política atual.

`ProjectDNA/v2` exige cadastro de fontes e proveniência das afirmações;
`HarnessSpec/v2` valida os novos escopos. `ProjectInput/v1`, CapabilityGraph/v1 e
TaskGraph/v1 mantêm suas versões. Leitores antigos de ProjectInput com campos
extras proibidos não aceitam a extensão opcional `evidence_pack`; atualizar o
compilador para usá-la.

IR v1 não é reinterpretada silenciosamente pelo comando compile:

```sh
factory migrate tests/fixtures/harness-v1.json --output output/migrated-harness.json
factory compile output/migrated-harness.json --output output/migrated-build
```

O diretório pai do novo JSON deve existir. Migração recusa sobrescrever um arquivo,
preserva configurações/decisões/afirmações e acrescenta a origem de declarações
conhecidas da baseline. Capabilities de decisões são obtidas das referências do
backlog reconhecidas. Declarações diferentes do input e evidências customizadas
ou de pesquisa sem proveniência exigem migração manual; não fabricar coleta,
digest, verificação ou novo resultado de eval.
