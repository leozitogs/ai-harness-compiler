# ADR-0017 — Comparação independente de provedores e fontes completas

Status: aceito como experimento de engenharia em development, 2026-10-08.

## Problema e evidência

A comparação anterior aceitou estruturalmente 6/8 propostas compactas locais,
mas não estabeleceu correção semântica. Duas chamadas exploratórias ao Codex CLI
0.162.0-alpha.2 autenticado com ChatGPT produziram interpretações do conflito entre
branding e critério de aceite que a projeção rejeitou: o pacote permitia citar
somente o branding. Os critérios não estavam na lista de contexto citável.

Além disso, valores numéricos de constraints chegavam sem o nome do campo;
`max_build_cost_usd: 0.0` aparecia apenas como `0.0`. É uma perda de contexto
introduzida pela representação, não evidência de incapacidade do modelo.

## Decisão

Acrescentar critérios ao final do contexto, preservando as posições antigas.
Adicionar `source_path` opcional a CompactContext e preenchê-lo deterministicamente
com o caminho original. Atualizar o programa compacto para v2. A saída continua
CompactUnderstandingProposal/v1; IDs/citações ficam com o compilador e condições
e resultados continuam hipóteses. Conflitos ainda exigem fontes distintas;
os validadores não estabelecem contradição semântica.

Adicionar um adaptador opt-in Codex CLI que usa login ChatGPT existente, sem ler
credenciais ou reutilizar tokens diretamente. Requer modelo explícito, diretório
temporário isolado, `--ignore-user-config`, `--strict-config`, `--ephemeral`, sandbox
read-only e ferramentas shell/web/subagentes desativadas. Rejeitar eventos de
ferramenta, erro, stream excessivo ou turno incompleto; descartar eventos privados.
Não registrar transcripts, prompts privados ou raciocínio intermediário.

Um grafo LangGraph opcional executa exatamente duas propostas independentes,
uma local e uma via CLI. Contabiliza erros/timeout e gera comparação tipada.
Não há juiz, voto, escolha automática, reparo ou aprovação. Concordância é
igualdade dos campos do critério, excluindo sua nota, e não prova de verdade.

## Validação e limites

Testes offline verificam isolamento dos inputs, orçamento, rejeição de eventos
inesperados, inventário de divergências, vínculo com corpus e métricas contraditórias.
Chamadas reais usam exclusivamente development sintético e ficam fora da suíte.
A [fundamentação científica](../engineering/understanding-scientific-basis.md)
define as ablações e explicita que nenhum artigo certifica este sistema.

O CLI é cliente agêntico, não endpoint de inferência puro: sandbox e flags reduzem
a superfície, enquanto o consumidor rejeita qualquer evento de ferramenta. Isso
não comprova isolamento de todo recurso do sistema operacional. O timeout mata
o processo local; não atesta cancelamento da inferência remota. Não há checkpoint
ou retomada nesta comparação e não se qualificará modelo sem revisão semântica.
O nome solicitado ao CLI não é hash dos pesos ou atestado do modelo remoto.

## Compatibilidade

CompactContext aceita novo kind `acceptance-criterion` e `source_path` opcional;
leitores antigos podem rejeitar o novo kind. Não há mudança nos campos da saída.
Artefatos antigos continuam válidos no leitor atual: índices antigos não mudam.
Hashes de programa mudam e a comparação histórica v1 não mede o programa v2.
Snapshots e relatórios antigos permanecem intactos.
