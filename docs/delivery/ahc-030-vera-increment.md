# AHC-030 — Incremento funcional da Vera

2026-10-19. Implementação autorizada pelo PO após a emenda de escopo. Entregues
captura Git limitada, contratos QA v1, runner de checks por revisão confiável,
inspeção opcional em uma tentativa e integração Vera/Nexo no LangGraph existente.
A história permanece em revisão; não há aceite ou encerramento automático.

## Comportamento

Vera recebe fontes e diff por base/head, critérios preservados e evidências de
checks. Achados têm severidade, impacto, recomendação, regra e citações verificadas
por linha. Reprodução proposta pelo modelo é sempre `not-executed`; check real
é produzido pelo runner. Cobertura declarada não certifica semântica ou completude.

Nexo deriva objetivo, bloqueios, checks falhos, matriz de critérios e carryover.
P0/P1 ou falha de execução impedem recomendar entrega plena. Parecer disponível
ao PO não estabelece critério atendido, qualificação de modelo ou cerimônia feita.
Mudanças de snapshot, commit, arquivos, diff ou memória invalidam o gate persistente.

Comparação preserva achados anteriores como pendentes de verificação semântica;
somente falhas de checks passam a superadas após resultado aprovado em novo head
sob os mesmos critérios. Falhas reais geram candidatos de INC, sem inventar causa
ou solução e sem promover LES ou modificar automaticamente a memória.

## Verificação

Regressões cobrem adulteração de conclusões, check/revisão divergentes, citações
inexistentes, injection, falso sucesso por CI verde, evidência não executada, budget,
timeout/saída, falha de provider sem fallback e retomada do gate Vera/Nexo. Os testes
de modelo são fakes offline; não são benchmark semântico de um provider.

## Demonstração executada

No commit `a1f7c6b`, a própria CLI executou lint, formatação, tipagem, schemas e
970 testes offline, todos aprovados; a suíte levou 71,19 segundos. São 63 testes
adicionais à baseline de 907. Políticas e os quatro planos gerados também foram
verificados; wheel e sdist construídos offline.

Duas execuções explícitas usaram o principal `gpt-6.1-sol` via Codex CLI:

- Seleção de seis fontes: cinco checks aprovados; uma tentativa de inspeção
  rejeitada ou falha, chamada real desconhecida. Resultado inconclusivo.
- Nova seleção de duas fontes (`qa.py` e `qa_runner.py`): schema aprovado,
  inspeção concluída com uma chamada observada, zero achados consultivos.
  O modelo declarou a ausência dos contratos, adapters, integração e testes na
  seleção. Resultado inconclusivo por cobertura incompleta, sem aceite implícito.

As duas execuções rodaram Vera/Nexo no LangGraph e pararam em `awaiting_po`,
sem aprovar o relatório ou encerrar a sprint. A comparação entre revisões,
bug de negócio com CI verde e invalidação de evidência foram exercitados nos
testes offline; não representam bugs descobertos e reproduzidos por um modelo real.

Relatórios, pareceres, candidatos de incidente, pacotes do time e hashes estão no
[inventário da demonstração](../evidence/ahc-030-vera-20261019/inventory.json).
O primeiro resultado não foi descartado ou convertido em sucesso. Zero achados
na segunda seleção não demonstra ausência de defeitos no incremento completo.
Não foram produzidos INC/LES sem problema confirmado e evidência de resolução.

A publicação desta evidência altera o checkout e a memória: os relatórios são
históricos. Para uma decisão atual do PO, recolher snapshot/captura e executar
nova sessão no head vigente. AHC-030 segue em revisão, com aceite pendente;
AHC-021/022/023 e qualificação semântica continuam fora desta entrega.

Ver [operação](../engineering/vera-review.md) e [ADR-0026](../adr/0026-vera-evidence-bound-review.md).
