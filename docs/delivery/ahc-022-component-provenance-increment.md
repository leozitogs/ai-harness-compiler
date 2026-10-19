# AHC-022 — Proveniência por componente e guards

Publicado em 2026-10-19. Incremento da emenda da Sprint 2.5; história em andamento.

A INC-0016 expôs uma regra que combinava permissão e rastreabilidade, mas citava
apenas a permissão. O contrato agora associa fontes individualmente à condição,
ao resultado e a cada exceção. Guards têm condição, efeito e aplicabilidade próprios;
não reescrevem autorização nem representam controles já executados.

`SemanticAnalysis/v3` e `SemanticVerifierReport/v4` são opt-in, pelos comandos
`analyze-project-v3` e `verify-analysis-v4`. Auditoria exige inventários completos,
hashes e vínculos exatos. Componente negativo impede suporte ao achado agregado.
Comandos e contratos anteriores permanecem disponíveis. A CLI também informa o
extra `understanding` quando faltar dependência opcional, com regressão dedicada.

## Desenvolvimento observado

Execuções reais em 2026-10-13: três gerações e quatro auditorias, sete chamadas ao
principal `gpt-6.1-sol` via Codex CLI, concorrência máxima dois. Não houve nova chamada
ao publicar. Os quatro pares foram revalidados em 2026-10-19 com Pydantic 2.14.1.
Arquivos finais e hashes: [inventário](../evidence/compound-provenance-20261013/inventory.json).

| Caso | Análise | Auditoria consultiva |
|---|---|---|
| Rastreabilidade com decisão DE-0008 | ready; permissão preservada e dois guards separados | seis componentes apoiados, nenhuma omissão |
| Branding adversarial | ready; regra legítima preservada | dois componentes apoiados, nenhuma omissão |
| Ambiguidade material | blocked | dois componentes apoiados, nenhuma omissão |
| Reprodução negativa construída do erro anterior | ready estruturalmente; fontes incompletas | três componentes sem suporte suficiente e uma guarda omitida |

O último caso é um controle negativo sintético, não uma geração bem-sucedida. A
auditoria usa o mesmo modelo, portanto concordância não é validação independente.
O ledger completo tampouco prova suporte semântico. Não foram armazenados prompts
privados, raciocínio interno, credenciais ou respostas de tools privadas.

## Verificação e próximos gates

Contratos têm regressões para troca de fonte entre componentes, exceções por índice,
alvos inválidos, fonte rejeitada, IDs duplicados, omissões e suporte agregado indevido.
Schemas foram exportados e os contratos antigos mantidos. Revisão independente do
incremento apontou a mensagem de dependências opcionais da CLI, corrigida e testada.

Na verificação local de 2026-10-19, 742 testes passaram sem skips, com todos os extras
instalados. Lint, formatação, mypy e verificação de schemas também passaram. A matriz
de integração cobre Python 3.12/3.13 em Linux e Windows.

Próximo incremento: evoluir revisão humana/assessment para v3/v4 sem perder fontes,
componentes e hashes. Depois revisar expectativas ainda pendentes, julgar resultados,
congelar candidato e somente então executar holdout. A revisão humana v2 não deve
receber conversão que descarte a nova proveniência. Qualificação continua
`not-established`, compilação `not-authorized`, holdout não lido e histórias abertas.
