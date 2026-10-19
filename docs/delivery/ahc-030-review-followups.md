# AHC-030 — Correções e evidências após a review

2026-10-19. PO autorizou cobrir pendências e corrigir os problemas encontrados.

## Correções

1. **P2 da captura importada:** o guard recalcula a lista completa de alterações
   entre base/head no Git. Exclusões removidas, inventadas ou duplicadas são
   rejeitadas antes de rodar checks, inspecionar ou recomendar revisão.
   Separação NUL preserva nomes com espaços/caracteres não ASCII.
2. **Resolução de achados:** proposta tipada com relatórios exatos, novo head,
   critérios preservados, inspeção atual, citações e checks aprovados; confirmação
   ou rejeição humana separada. Ausência de confirmação conserva a pendência.
3. **Nexo:** comparação e decisões vinculadas ao gate persistente; achados antigos
   não confirmados entram no parecer combinado. P0/P1 continuam bloqueando,
   mesmo quando a inspeção atual não os repete. Entrada Python também rejeita
   decisões futuras; alteração posterior da comparação invalida o checkpoint.

Ator é declaração de um operador confiável, sem autenticação ou assinatura.
Nenhuma ferramenta de confirmação foi concedida ao modelo. Resolução de achado
não estabelece aceite por critério, qualificação semântica ou encerramento de sprint.
Ver [ADR-0027](../adr/0027-qa-resolution-evidence-and-human-review.md).

## Verificação e inspeção ampliada

No commit `5ae0ab9`, os sete checks do runner passaram. **988 testes offline
passaram, sem skips, em 107,05 segundos** — 18 adicionais à baseline de 970.
Lint, formato, tipos, schemas, política gerada e plano da sprint passaram no mesmo
runner. Os quatro planos existentes foram verificados separadamente; mypy Linux
e empacotamento offline também foram executados. CI do PR é gate de integração.

Dois agentes independentes revisaram código e regras de negócio. Confirmaram a
rejeição da reprodução anterior e detectaram durante a implementação a omissão
de bloqueios históricos no parecer do Nexo, corrigida e coberta por regressão.
Revisão de agente não é aceite humano.

A Vera executou duas inspeções explícitas no principal `gpt-6.1-sol`:

- Núcleo: sete fontes, incluindo contratos, comparação, coletor Git, runner, CLI e
  regressões de runtime/resolução; sete checks realmente aprovados; uma chamada
  concluída, zero novos achados consultivos.
- Integração: onze fontes adicionais, incluindo team contracts/runtime/tools/CLI,
  personas, adapter do modelo, testes e documentação; uma chamada concluída, zero
  novos achados consultivos. O check schema desse pacote ficou `not-run` porque
  sua execução não foi autorizada nessa sessão; resultado real está no pacote núcleo.

As dezoito fontes estão enumeradas no inventário. Cada pacote explicita seus
arquivos excluídos e limitações; nenhum isoladamente representa cobertura total.
As duas chamadas não são benchmark, qualificação ou prova de ausência de defeitos.
Vera e Nexo ficaram em `awaiting_po`; relatórios continuam `inconclusive` pela
cobertura parcial de cada seleção e pelas pendências de revisão humana.

## Demonstração de resolução

Fixture isolada, código conhecido e pytest real: `authorize(False)` falha antes da
correção e passa depois. A comparação sem decisão mantém `approval-bypass` P1 e
o Nexo recomenda `changes-required`. Após confirmação **explicitamente simulada**
por `simulated-fixture-human`, a comparação registra o achado resolvido e remove
o bloqueio; gate continua `awaiting_po`, sem aceite global ou encerramento.
Não houve chamada de modelo nessa fixture. A primeira tentativa de demonstração
foi recusada porque pytest gerou bytecodes não ignorados; o fixture final ignora
esses arquivos gerados, mantendo o guard de checkout limpo sem relaxamento.

No projeto real, foi produzida apenas uma proposta para `independent-001`, com
regressões aprovadas e citação da correção. Não executamos `review-resolution`
em nome do PO: a confirmação permanece pendente e o Nexo conserva o achado.

## Evidências e estado

[Inventário e hashes](../evidence/ahc-030-followups-20261019/inventory.json) preservam
os dois relatórios de modelo, pacotes Vera/Nexo, fixture antes/depois, decisão
simulada, proposta real e comparação ainda pendente. A publicação altera head e
memória: esses pacotes são históricos; nova decisão exige captura atual e válida.

Funcionalidade e correção implementadas, confirmação humana ainda pendente.
AHC-030 permanece em revisão e Sprint 2.5.5 aberta. AHC-021/022/023 continuam
pendentes; não foi iniciado treinamento, promoção de modelo ou Sprint 2.6.
