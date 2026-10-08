# AHC-023 — Seleção operacional do principal

Principal: **Codex CLI / gpt-6.1-sol**. Alternativa local explícita:
**Ollama / ahc-qwen3:4b-instruct-8k**. A escolha atende ao pedido do PO de usar
o melhor resultado disponível, sem inventar qualificação ou ranking universal.

## Por que este principal

Na [comparação anterior](ahc-022-independent-comparison.md), o modelo local teve
maior conclusão estrutural (8/8 contra 7/8), mas o Codex apresentou interpretação
e vínculos de fonte mais adequados nos casos relevantes:

| Caso | Diferença observada que favorece Codex |
|---|---|
| Domínio novo | Mantém responsável/origem, sem inferir maturidade do orçamento zero |
| Regra de aprovação | Separa evento de liberação e aprovação prévia |
| Publicação pelo autor | Preserva ausência de terceiros; não inventa tensão com controle humano |
| Conflito de branding | Cita branding e critério `[2,7]`; local omite critério |
| Regras compatíveis | Vincula domínio/capacidades às fontes correspondentes e preserva quatro obrigações |
| Assets não lidos | Preserva responsável/origem sem alegar conteúdo de arquivos |

Não existe score humano aprovado nesta tabela. Notas/condições/resultados continuam
hipóteses; detalhes adicionais foram convertidos em dúvidas bloqueantes pelo
Codex e ainda precisam de adjudicação. Isso impede afirmar que seja melhor em
todo problema ou qualificado em produção. A escolha é preferencial para
desenvolvimento, com a melhor evidência semântica disponível.

## Verificação adicional

Uma nova chamada de development para `dev-adversarial` com o principal completou
o contrato em 11,632 s e manteve responsável/origem. Artefatos em
[primary-adversarial](../evidence/ahc-023-primary-adversarial-20261008).
A falha antiga não foi substituída, o denominador da comparação segue 7/8 e
a causa do erro anterior permanece desconhecida. Sem holdout, adjudicação humana
ou alegação de segurança geral.

O caminho padrão `factory study examples/project-definition` foi executado
com o principal e gerou proposta válida com review null. O adapter retorna
propostas tipadas; falhas de stream passam a expor somente códigos fixos,
nunca tokens, prompts privados ou eventos de raciocínio.

Um especialista real (Nexo/entrega) executou `retrieve_context`, `retrieve_memory`
e `delivery_plan`, finalizou seu relatório consultivo e chegou a `awaiting_po`,
sem aprovação ou início de sprint. Os seis papéis são verificados offline com
provedor falso; somente este especialista teve smoke real nesta seleção.
[Observações e exemplo](../evidence/ahc-023-primary-smokes-20261008).

O primeiro smoke tentou escopo sem pré-requisitos e foi rejeitado antes do modelo.
O seguinte falhou na primeira decisão simbólica; diagnóstico limitado registrou
`CODEX_EVENT_INVALID`. O prompt foi corrigido para distinguir APIs do host de
tools da sessão Codex e exigir somente um JSON. Novo run atingiu o gate do PO.
Isso não prova que o prompt tenha sido a única causa do erro anterior.

## Como usar

```sh
factory model-policy
factory study examples/project-definition --output output/new-understanding.json
factory team run project-definition --engine primary --output output/new-primary-team
factory study examples/project-definition --provider ollama --output output/new-local.json
```

Criar a pasta do arquivo de saída e usar destinos novos. O primeiro estudo envia
entrada ao serviço da assinatura ChatGPT; usar conteúdo autorizado. O comando
da equipe usa as quatro histórias iniciais por padrão; para outro escopo incluir
todos os pré-requisitos, sem declará-los concluídos por conveniência.

A preferência vem de `src/ai_harness_compiler/default-model-policy.json`, incluído
no pacote. `--model-policy` aceita outra política validada; `--provider/--engine`
e `--model` são overrides explícitos. Todos os seis papéis herdam o principal.
`team run` sem engine segue determinístico/offline; `--engine primary` habilita
o principal para decisões LLM. Os runners de benchmark local permanecem específicos
do Ollama e não mudam de provedor ao aplicar essa preferência.

Nenhum fallback automático, alteração de configurações globais, substituição de
inputs confirmados, autoaprovação ou marcação Done. AHC-023 mantém a qualificação
semântica pendente; a seleção operacional está implementada e verificável.

Verificação final: 566 testes sem skips; Ruff, formatação, mypy, schemas, políticas,
três planos de sprint, memória/índice e build. O wheel contém a política principal
empacotada; o usuário não precisa do checkout para carregar a preferência.

A auditoria pós-commit detectou hashes de observações calculados com CRLF,
enquanto Git publicou LF. Normalizamos os arquivos de evidência antes de congelar
novos hashes e preservamos revisões anteriores. Isso corrige correspondência de
bytes, sem alterar valores, medições ou alegar autenticidade da inferência.
