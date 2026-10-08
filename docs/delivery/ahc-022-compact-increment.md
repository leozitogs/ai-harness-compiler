# AHC-022 — Incremento de interpretação compacta

Implementado para revisão: protocolo compacto, schema dimensionado pelo input,
projeção pura de IDs/citações, modo opcional no runner e três schemas aditivos.
Regras continuam hipóteses; parâmetros inferidos não viram fatos confirmados.
Sem leitura de assets, labels de eval no prompt, dependências ou alteração de licença.

Verificação local: 475 testes sem skips, 25 novos casos de compacto; lint,
formatação, tipagem, schemas, AGENTS, três planos de sprint e build verificados.
Baseline, grounded e journals/repair anteriores permanecem compatíveis.

Smoke inicial falhou em preflight com Ollama inativo; serviço existente em D foi
iniciado em background. Smoke seguinte produziu proposta formalmente válida.
Comparação de oito casos por programa resultou em 4/8 válidos na baseline e
6/8 no compact. Todos os journals foram validados e fontes preservadas.

A melhoria observada é estrutural; há falhas de suporte e dois erros compactos.
Não houve aprovação semântica, qualificação, holdout ou encerramento de história.
Ver ADR-0016 e comparação de development; rubrica/expectativas aguardam review do PO.
