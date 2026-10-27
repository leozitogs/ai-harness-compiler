# Sprint 2.6 — sequência de avanço após a correção UTF-8

Data: 2026-10-27. Sequência autorizada pelo PO para preparação e engenharia;
nenhum novo orçamento de inferência concedido. Sprint em andamento, sem prazo ou
capacidade comprometidos. O escopo canônico continua AHC-021 a AHC-026.

## Primeiro incremento preparado

O worker corrigido foi integrado no PR #77 e passou em 1.266 testes offline.
Preparámos outro request para observar a compatibilidade no provedor, com o
mesmo caso `compat-catalog-v4-01` e o mesmo aceite das cinco expectativas.
Não há alteração de inputs, expectativas, rubrica ou programas lógicos de análise
e auditoria. Não é necessário pedir novamente esse julgamento do caso.

O [novo request](../../evals/understanding/v4/compatibility-utf8-reviewed/request.json)
tem SHA256 canônico:

`4d4a7f98cf43d5f7fb39f4c31bb64ca07e47a8aa26aca4132f877c335401d2a7`.

| Campo | Escopo proposto para autorização específica |
| --- | --- |
| Caso aprovado | Snapshot `46d173dc08b91833cb7cc9488bffee354e9f3dc7fb4bee885e80a920f98adb65` |
| Programa | Uma análise v4, depois uma auditoria v5 da análise válida |
| Destino/modelo solicitado | Assinatura ChatGPT/Codex CLI; `gpt-6.1-sol` |
| Máximo | Duas invocações sequenciais do adapter/worker |
| Prazo por chamada | Até 180s, também limitado pelo saldo da sessão |
| Limpeza | Reserva de até 20s por etapa, dentro da sessão |
| Sessão | Até 400s; sem garantia de tempo real do sistema operacional |
| Bytes por worker | Até 1 MiB de entrada e 4 MiB de saída |
| Parada | Primeira falha técnica; sem retry, repair, fallback ou retomada |
| Conteúdo enviado | Somente fontes públicas do caso; na auditoria, também a análise gerada |
| Exclusões | Expectativas, rubrica, julgamentos, assets, reservado, ferramentas, web, API paga por chave, treinamento e mudanças de defaults |
| Rodada | `compat-v4-catalog-20261027-03` |
| Saída privada | `.factory/supervised-v4-runs/compat-v4-catalog-20261027-03/` |

O journal interno será separado em
`.factory/semantic-v4-runs/compat-v4-catalog-20261027-03/`.
Não existe autorização, claim ou execução para essa rodada no preparo.

O freeze captura 101 fontes, runtime Python e comando fixo. Em relação ao request
anterior, apenas o hash do fonte `semantic_worker_v4.py` mudou entre esses arquivos;
o novo ID de rodada também altera a identidade do fluxo. Base do preparo:
`1989741930f5805ad1ae225149b676073d6c39e2`. O
[protocolo](../../evals/understanding/v4/compatibility-utf8-reviewed/protocol.json)
explicita o diff de hashes e o vínculo ao orçamento anterior fechado.

O request anterior `2e8963f1…` parou em `invalid-output` após uma invocação;
a segunda invocação não é transferida. A correção UTF-8 foi verificada somente
offline. A causa exata dos bytes reais descartados e a aceitação dos schemas pelo
provedor continuam desconhecidas. O novo request não reescreve nem retoma o antigo.

O limite conta invocações do adapter/worker, sem autenticar o modelo remoto ou
contar requisições internas da CLI. O freeze não é um ambiente hermético. O programa
lógico da auditoria está vinculado; seus prompt/schema dinâmicos dependerão da
análise futura. Compatibilidade de contrato ou recibo bem-sucedido não equivale
a correção semântica, qualificação, autorização de compilação ou conclusão da sprint.

## Plano de trabalho com dependências e saídas verificáveis

| Ordem | Trabalho | Dependência | Saída e condição de avanço |
| --- | --- | --- | --- |
| 1 | Compatibilidade após UTF-8 | PR #77 integrado e novo pedido congelado | Autorização específica; até duas etapas; replay e falhas preservadas |
| 2 | Julgar o caso executado | Análise aceita, se produzida | Revisão humana nova dos seis critérios; auditor consultivo; nenhum aceite automático |
| 3 | AHC-021: corpus e evals | Contratos representáveis e revisão dos critérios | Desenvolvimento versionado com expectativas compatíveis; separar not-run, erro, fail e pass; não migrar aceites para expectativas alteradas |
| 4 | AHC-022: baseline e candidato | Gates de AHC-021 | Comparação de desenvolvimento sob rubrica congelada, preservando fontes, omissões, condições e todas as tentativas |
| 5 | AHC-023: qualificação ou rejeição | Candidato congelado e AHC-022 revisada | Avaliação independente, qualidade antes de custo/latência, cold/warm e recursos observados; nenhuma obrigação de eleger vencedor |
| 6 | AHC-024: perfis por provider | AHC-021/022 revisadas | Contratos de parâmetros/fingerprints solicitados, observados ou desconhecidos; rejeitar opções incompatíveis; testes offline |
| 7 | AHC-025: experimentos | Perfis compatíveis e baseline julgável | Protocolo, repetições e orçamento próprios; métricas semânticas separadas de validade estrutural, estabilidade e recursos |
| 8 | AHC-026: decisão de treinamento | Evidência dos experimentos | Go/no-go fundamentado; piloto depende de dados/licenças/recursos e autorização; no-go é entrega válida |
| 9 | Review e encerramento | Critérios e DoD efetivamente cumpridos | Evidências, limitações, documentação, memória e pendências revisadas; não marcar Done por CI verde |

A ordem organiza o foco; não acrescenta dependências artificiais ao grafo canônico.
AHC-024 depende de AHC-021/022, não de uma conclusão fictícia de AHC-023.
Nenhum desses itens ganha status Done por esta preparação.

## Critérios de qualidade e limites da avaliação

- Julgar cobertura, suporte das citações, conflitos, assets/injection, incerteza e
  entendimento. Falha crítica ou julgamento pendente impede qualificação; médias
  positivas não compensam regras obrigatórias omitidas ou condições inventadas.
- Reutilizar o aceite do caso somente quando inputs e expectativas forem idênticos.
  Alterações materiais exigem revisão; nenhuma nova resposta herda julgamento.
- Ajustar candidatos apenas em desenvolvimento. O reservado já exposto pode servir
  como regressão histórica, sem voltar a ser avaliação cega. Uma avaliação independente
  requer novo corpus, expectativas revisadas e candidato congelado antes do acesso.
- Registrar diferenças de ambiente e variáveis não controladas. Uma execução pela
  assinatura Codex não mede VRAM, quantização ou desempenho de inferência local do
  notebook; metadados remotos não expostos permanecem desconhecidos. AHC-023 exige
  evidência própria para candidatos locais, sem equiparar providers.
- Não presumir suporte a temperatura ou outros parâmetros em todos os adapters.
  Perfis rejeitam opções incompatíveis; parâmetros não observáveis não são efeitos
  medidos. Não alterar energia, concorrência ou serviços pagos silenciosamente.
- Nenhum treino começa por existir uma proposta. Regras de negócio permanecem no
  input de cada projeto; não transformar nichos fixos em conhecimento obrigatório
  do compilador ou usar o holdout para tuning.

Neste incremento, somente o pedido e o plano estão preparados. O próximo gate é
autorizar o hash exato acima; depois, executar e registrar o resultado sem ampliar
o orçamento. A validação da correção, o novo pedido e a futura qualificação são
evidências diferentes.
