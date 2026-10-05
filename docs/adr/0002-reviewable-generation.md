# ADR-0002 — Emissão reproduzível e instalação separada

Status: aceito para o scaffold inicial.

## Decisão

Gerar somente em diretórios novos. Proibir execução de código gerado dentro do
compilador. Manter texto do input em JSON, separado das instruções de AGENTS.md.
Registrar hashes e marcar evals de produto como `not-run` até execução real.

## Consequências

O usuário pode revisar e comparar bundles antes da adoção. O manifesto verifica
integridade acidental, não autenticidade. A escrita pode ficar parcial em falhas
de I/O. Runtime, sandbox, instalação transacional, assinaturas e enforcement de
políticas exigirão implementação própria e testes de segurança.
