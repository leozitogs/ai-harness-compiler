# Nexo — propostas Scrum com evidências

AHC-028 adiciona planejamento procedural ao observador, sem escrita remota.
O núcleo não importa LangGraph nem requer modelo. Para reavaliar fontes salvas no
horário atual e emitir propostas offline:

```sh
factory scrum propose output/snapshot.json --output output/new-proposals.json
```

Fontes vencidas permanecem vencidas; este comando não recolhe GitHub. Os diagnósticos
ficam no snapshot incluído. Uma proposta de planejamento não constitui compromisso.

Para executar a persona Nexo no LangGraph, instale o extra `team`, faça uma coleta
recente com `factory scrum observe` e use:

```sh
factory team run project-definition --scrum-snapshot output/snapshot.json --repository . --request "Revisar objetivo, carryover e próximos refinamentos" --output output/new-nexo
factory team review output/new-nexo --decision approve --comment "Aprovo somente este relatório"
```

O snapshot define seleção e força modo ask/Nexo; não depende de acerto do roteador ML.
Engine padrão local: três ferramentas (`retrieve_context`, `retrieve_memory`,
`delivery_plan`) e uma finalização, dentro do limite padrão de cinco passos.
O checkpoint interrompe antes da decisão humana. `--engine` existente pode escolher
um modelo explicitamente; isso não transfere autoridade ao texto do modelo.

Cada refinamento preserva critérios, dependências e evidências da história.
Planejamento pergunta capacidade aos Developers, sem inventar horas ou velocity;
review apresenta resultado declarado e trabalho não aceito. Destinatário, opções
e autoridade constam no contrato. Textos de branding, issues e memória são dados.
Retrieval exclui drafts, superseded e evidência stale conforme o MemoryStore.

Mudança nos cinco arquivos locais observados, no manifesto normalizado, no contexto
da equipe ou na memória invalida revisão. TTL vencido exige recoleta. A captura
remota é uma observação pontual; não garante ausência de mudanças posteriores.
O cache vale apenas dentro da sessão e usa o digest completo da observação.

Relatório aprovado mantém `execution=not-authorized`, `acceptance=not-established`,
`sprint_started=false` e `backlog_modified=false`. Ainda não há autorização de
operações, aceite individual de critérios ou previsão quantitativa de capacidade.
