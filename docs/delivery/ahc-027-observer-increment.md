# AHC-027 — Incremento do observador Scrum

2026-10-19. Sprint 2.5.5 iniciada por autorização explícita do PO. Entregues contratos,
coletores limitados, reconciliação determinística e CLI somente leitura. A história
fica em revisão; AHC-028/029 continuam planejadas. Não há nova ferramenta procedural
executada no Nexo/LangGraph neste incremento.

## Demonstração real

`factory scrum observe` coletou manifesto, plano/work-items da Sprint 2.5, política
Scrum, índice de memória, issues 15/16/17 e PR 40. O mesmo PR explicitamente vinculado
a AHC-021/022 foi consultado uma vez. Quatro leituras GitHub no snapshot final;
nenhuma escrita remota ou chamada de modelo. Houve também smoke preliminar das
mesmas quatro leituras durante desenvolvimento.

Resultado: declaração `closed_with_carryover`, objetivo declarado `not-achieved`,
três issues observadas OPEN e PR MERGED com checks reportados all-success. Oito
diagnósticos apontam fontes concretas: dependências não resolvidas/não verificadas,
PR integrado sem aceite estabelecido, checks que não certificam semântica e
fechamento parcial. Nenhuma história foi promovida a Done ou modelo qualificado.

Reconciliação offline preservou fontes e seus horários, atualizando o instante de
avaliação e o digest da observação; não fez nova consulta remota.
[Snapshots e inventário](../evidence/ahc-027-observer-20261019/inventory.json).

## Verificação

830 testes passam na suíte ampliada, com todos os extras; 63 testes novos do observador
e coletores cobrem escopo, hashes, timestamps, fontes stale/ausentes, JSON duplicado,
dependência aberta escondida por declaração local, falha de CI entre successes,
no-overwrite, falhas/limites do adapter e envelhecimento offline. Intake existente
preserva testes após extração do parser puro dos bytes capturados.

Lint, formatação, mypy, schemas e planos gerados verificados. Revisão e CI do PR
completam o fluxo de integração; este documento não representa aceite humano.

## Limitações e próximo incremento

Captura não é transação remota nem autenticação de arquivos salvos. O observador
não ingere reviews individuais de critérios, certifica DoD ou conhece a política
de required checks. A política e o índice são referências preservadas, não
interpretações do LLM ou recuperação automática de toda a memória.

AHC-028 deve tornar o diagnóstico uma ferramenta do Nexo e produzir propostas
tipadas sem converter dados em decisões humanas. AHC-029 permanece responsável
por autorizações e recibos de operações. Gates semânticos da Sprint 2.5 continuam.
