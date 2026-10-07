# Sprint 2.5 — Piloto com alimentação CA

Executado em 2026-10-07 com `ahc-qwen3:4b-instruct-8k`, Ollama 0.40.0.
Mesmo manifesto público, modelo/digest, prompt e parâmetros do estudo anterior;
uma chamada cold após unload explícito e duas warm sequenciais, sem tuning.
PowerOnline=true foi observado antes/depois das três chamadas; Windows estava
no plano Desempenho Máximo. Não alteramos plano de energia nem fechamos aplicativos.

| Chamada | Tempo observado | Statements | BusinessRule | Hash do JSON de entendimento |
|---|---:|---:|---:|---|
| Cold | 43,939 s | 15 | 0 | fb7479c3… |
| Warm 1 | 28,386 s | 12 | 0 | 30eaae53… |
| Warm 2 | 28,080 s | 12 | 0 | 30eaae53… |

As três saídas passaram nos contratos e continuam sem revisão/aplicação. O modelo
ficou 100% GPU com contexto de 8192. Mediana das duas observações warm: 28,233 s;
amostra insuficiente para estimar percentis, SLA ou velocidade geral.
Tempo inclui preparação/telemetria anterior à chamada, não apenas geração.
Potência, clocks e temperatura são leituras pontuais, não uma série sob carga.
TGP não foi disponibilizado pelo driver. RAM/energia por fase serão instrumentadas
no runner de qualificação; este piloto não substitui essa história.

A cold reproduziu exatamente o hash do ensaio anterior de 69,284 s. As warm
reproduziram entre si outro hash, com 12 statements. Temperatura zero não garantiu
mesma saída entre cold/warm; causa não foi isolada. Não interpretar variação como
melhoria semântica. Hashes completos, contexto e parâmetros estão nos registros.

Leitura de conteúdo: omissão de regras persistiu nas três chamadas. Na cold,
permanecem inferências indevidas sobre revisão externa e asset não lido. Nas warm,
domínio cita branding e `s12` inventa conflito entre orçamento zero e uso de Python/
contratos versionados. Esse conflito não é sustentado pelo input: custo de serviços
limitado não implica incompatibilidade com ferramentas disponíveis sem cobrança.
Também permanece referência indevida a conteúdo de asset não ingerido.

O desempenho observado melhorou em relação ao ensaio anterior, mas a alimentação
anterior não foi registrada e cache/RAM/ambiente não foram controlados entre períodos.
Não atribuir causalidade exclusivamente à tomada. A falha semântica continua aberta
em INC-0007; nenhum modelo qualificado ou LES derivada deste piloto.

Evidências públicas: `docs/evidence/sprint-2-5-ac-pilot/` com run/understanding por
chamada; modelo/input/prompt/outputs identificados por SHA-256. Não contém thinking,
segredos ou prompts privados. São execuções de preparação da sprint, não holdout.
