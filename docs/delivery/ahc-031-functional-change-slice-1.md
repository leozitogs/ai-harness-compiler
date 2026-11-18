# AHC-031 — primeira fatia funcional offline

Início autorizado pelo PO em 18/11/2026: “pode começar com a primeira fatia”.
Plano: `planning/ahc-031.slice-1.json`. O pedido autoriza implementar e verificar
esta fatia; não declara AHC-019/021/022 concluídas nem inicia outra sprint.

## Resultado implementado

Uma mudança funcional pode representar regra e fontes exatas, exemplos sintéticos
de sucesso/falha/fronteira, pergunta com responsável/impacto, requisito e locators
de teste. Confirmações e decisões humanas vinculam hashes dos objetos e do pacote
de fontes. O review vincula projeto, mudança, revisão e conteúdo completo.

O serviço puro recalcula bloqueios e prontidão; uma aprovação global não supera
pergunta material aberta ou regra sem confirmação. Trocar texto ou referências
invalida declarações; editar conteúdo exige review novo. Checklist de cenários
preparados vive num worklog separado e não representa teste executado.

O [CLI offline](../engineering/functional-change.md) lê input/review explícitos
e grava relatório em arquivo novo, com limites de bytes e paths. A fixture em
`examples/functional-change/change.json` continua blocked pela pergunta aberta;
usa declarações sintéticas, sem aceite real de negócio.

## Critérios desta fatia

| Comportamento | Verificação |
|---|---|
| Fonte literal, projeto, capacidade e IDs consistentes | Mutações de quote, pointer, escopo e referências são rejeitadas |
| Regra confirmada só no snapshot declarado | Texto ou pacote de fontes alterado invalida confirmação |
| Exemplos concretos e categorias justificadas | Categoria ausente bloqueia; todas as categorias isentas não eliminam mínimo concreto |
| Pergunta material preservada | Dono e impacto permanecem; decisão só resolve pergunta/fontes exatas |
| Requisito → exemplo → locator de teste | Referência quebrada, regra divergente ou comando disfarçado falham |
| Aceite não atravessa mudança semântica | Review antigo retorna stale; checklist de progresso não muda o digest |
| Nenhum sucesso de runtime inventado | Testes not-run, compilação not-authorized e modelos não qualificados são constantes |
| Compatibilidade histórica | Pedidos v4.0/v4.1/v4.2 intactos, registry histórico arquivado e gate atual não afrouxado |

Verificação local: 48 testes novos e seis testes de regressão passaram (54 no total).
A execução da fixture emite
`blocked; 1 blockers; tests not-run`, preservando a pergunta sobre excesso de
entradas. O bloqueio é o resultado esperado, não uma falha a corrigir automaticamente.
Os checks completos e a CI são exigidos antes da integração.

## Fronteira da entrega

São quatro schemas aditivos e serviços opt-in; ProjectInput, HarnessSpec, build,
prompts e qualificação atuais não mudam. O registry de schemas recebe os tipos
novos e o código histórico continua preservado em arquivo de evidência e replay.
Não houve chamada a modelo, leitura de assets, instalação ou cópia de conteúdo
externo. Nenhum nicho, agente ou framework obrigatório foi acrescentado.

Para AHC-031 ainda faltam ciclo de revisão/archive, integração semântica após os
gates, validação real por projeto e execução de testes de negócio. O grafo global
de impacto pertence a AHC-032. A declaração humana é rastreável, mas não autenticada
pelo contrato; suporte semântico, privacidade e inaplicabilidade exigem revisão.
Esta fatia não encerra a história ou a Sprint 2.6.
