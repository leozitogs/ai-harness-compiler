# AHC-022 — Incremento de repair limitado

Implementado para revisão: diagnósticos escopados, protocolo de feedback, programa
grounded-repair/v1, controller de um caso de development e journal de tentativas.
Cada worker faz uma chamada; até duas correções configuráveis, sempre consumindo
max-attempts e saldo de tempo. Timeout/model-changed interrompem sem próxima chamada.

Verificação local: 450 testes sem skips, incluindo 38 novos testes de repair. Ruff,
formatação, mypy, schemas, AGENTS, três planos de sprint e build passaram. Journals
anteriores continuam legíveis. Sem dependências ou alterações de licença.

Primeiro smoke: not-repairable, uma tentativa, sem diagnóstico elegível. Após
diagnósticos de citações/referências, o segundo teve geração e uma correção:
proposal-reference-invalid → criterion-inventory-invalid → repair-limit. Ambos
os journals foram validados; nenhuma proposta foi aceita ou semanticamente avaliada.
Não houve comparação, ranking, holdout ou qualificação. Fonte rejeitada/unknown IDs
do candidato não entram no feedback como autoridade.

Próximos passos: revisar rubrica/expectativas, preparar comparação de development e
avaliar modelos/perfis com qualidade primeiro. AHC-021/022/023 e INC-0007 permanecem
sem conclusão semântica. A entrega de controles de repair não comprova melhoria
do modelo nem aceite do PO.
