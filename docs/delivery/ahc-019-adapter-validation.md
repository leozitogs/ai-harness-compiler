# AHC-019 — Segundo incremento: interface e adapter local

Verificação em Windows/Python 3.13.7 em 2026-10-07:

- 273 testes passaram sem skips; 36 novos testes do adapter/CLI.
- Ruff lint/formatação, mypy, schemas, AGENTS e planos das sprints passaram.
- Transporte simulado cobre payload estruturado, erros, limites, timeout/deadline,
  rejeição de redirects/tools/truncamento, isolamento do snapshot e saída exclusiva.
- Testes não chamam modelos ou serviços. Fake existe somente na suíte.

Contratos do PR #13 integrados. Este incremento fornece `UnderstandingModel`,
`study_project`, adapter Ollama no extra opcional `understanding` e `factory study`.
Sem migração de IR/schema, sem revisão automática e sem aplicar propostas ao harness.

## Ambiente local disponível

PO autorizou instalar Ollama no D. Instalador oficial com assinatura Authenticode
Valid de Ollama Inc. Instalado em `D:\Ollama`; versão CLI/API 0.40.0 confirmada.
`OLLAMA_MODELS` do usuário aponta para `D:\Ollama\models`; API `/api/tags` retornou
lista vazia. RAM observada 15,7 GiB, NVIDIA GeForce RTX 4050 Laptop GPU.
Paths são fatos deste ambiente, não requisitos ou configurações embutidas no produto.

Nenhum modelo baixado, nenhuma geração real demonstrada. Instalação não comprova
entendimento, sucesso de eval ou qualidade semântica. 019-03/019-06/019-08/019-09
e aceite da AHC-019 permanecem pendentes. O prompt inicial não foi otimizado nem
avaliado com casos reservados.
