# Observador Scrum — AHC-027

Primeiro incremento da Sprint 2.5.5, sem chamadas de modelo. Comandos salvam um
snapshot novo e recusam sobrescrever arquivo. Código zero significa diagnóstico
salvo, não DoD aprovada, sprint concluída ou perfil qualificado.

```sh
factory scrum observe . --project-id ai-harness-compiler --repo leozitogs/ai-harness-compiler --sprint sprint-2-5 --output .factory/local-scrum.json
factory scrum observe . --project-id ai-harness-compiler --repo leozitogs/ai-harness-compiler --sprint sprint-2-5 --github --pull-request ahc-021=40 --pull-request ahc-022=40 --output .factory/remote-scrum.json
factory scrum reconcile .factory/remote-scrum.json --output .factory/reconciled-scrum.json
```

Diretório de saída deve existir. `--github` requer CLI `gh` autenticada; ausência ou
erro vira fonte indisponível, sem persistir stderr/credenciais. Não faz login,
instala dependência, inicia modelo ou muda preferência de provider.

## Fontes e bounds

Leitura de `project-definition/project.yaml`, `planning/<sprint>.json`, work-items
da mesma sprint, `docs/delivery/scrum.md` e `knowledge/INDEX.md`. Caminhos resolvidos
precisam permanecer na raiz; não segue assets ou caminhos fornecidos pelo plano.
Manifesto usa parser seguro do intake e é capturado como ProjectInput JSON; seu
`revision` identifica os bytes originais e seu content hash a projeção capturada.

Issue URLs precisam coincidir com `--repo` e tracking. PRs são selecionados explicitamente
e deduplicados por número, mesmo vinculados a duas histórias. `GitHubReader` admite
fake offline; `GitHubCLIReader` executa só `issue view`/`pr view`, com host explícito,
campos limitados, stdout limitado, stderr descartado e timeout de até dez segundos.

Limites: 256 KiB/fonte, 4 MiB de conteúdo total, 6 MiB de observação serializada,
256 fontes, 64 histórias e 128 vínculos story/PR. Coleta remota padrão: 16 leituras
e sessão de até 120 s; `--max-remote-reads` aceita 0..64. Sem retry automático. Fonte
grande fica indisponível; plano inválido não dispara rede. Reconciliação aceita
snapshot salvo de até 8 MiB. Consultas GitHub não formam uma transação: cada fonte
tem seu próprio horário de observação.

`--max-age-seconds` define TTL de 1..86400 s, padrão 3600. Horários têm timezone.
Fonte vencida não sustenta fato atual. `reconcile` envelhece observações no horário
atual; os mesmos dados antigos não se tornam uma nova coleta.

## Diagnóstico e limitações

Preservar declaração do plano, estado remoto e evidências separadamente. Diagnósticos
incluem fontes indisponíveis/stale, divergências, Done sem aceite estabelecido,
dependências não declaradas completas, PR integrado sem evidência de aceite e
fechamento com carryover. Referências apontam para fontes capturadas. JSON com chaves
duplicadas e recursos fora de escopo não orientam fatos.

Checks vazios, skipped/neutral e formatos desconhecidos ficam unknown. `all-success`
significa apenas que todos os checks reportados tinham success; não verifica
configuração de proteção ou inventário de checks obrigatórios.

Não ingere pareceres humanos por critério, nem certifica Done, adjudica semântica ou
autentica declarações de arquivos salvos. Ler índice não equivale a recuperar todas
as lições. AHC-028 integrará esse diagnóstico ao Nexo; AHC-029 tratará escrita autorizada.
