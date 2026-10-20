# Materialidade de perguntas — Sprint 2.6

## Problema e decisão de engenharia

O PO reprovou somente incerteza em dois snapshots v3.3. A pergunta adicional
sobre aplicabilidade do registro de identidade possuía fontes, mas não impedia
entender a obrigação normativa. Os impedimentos legítimos dos dois projetos
permaneciam. Ver INC-0024 e LES-0006: suporte e disposição não certificam pertinência.

`semantic-composition/v3.4` é uma receita explícita e experimental, baseada em
v3.3. Seu único acréscimo é a política de materialidade: cada pergunta bloqueante
deve identificar a decisão de negócio que depende da resposta. Ausência de
mecanismo, momento de execução ou nome de pessoa não é, isoladamente, impedimento
para analisar intenção. A obrigação continua no contexto normativo; limitações
ficam declaradas e perguntas úteis podem usar `implementation-detail`.

Isso não transforma toda dúvida de aplicabilidade em detalhe. Autorização
indeterminada, condições de conclusão desconhecidas e conflito entre regras
declaradas continuam exigindo perguntas quando as fontes sustentam a dependência.
A receita não contém nomes de casos, regras de nicho ou alteração da rubrica.

Alternativas descartadas: remover perguntas por palavras-chave; reclassificar
automaticamente a resposta; apagar a obrigação; aprovar os casos pela disposição;
retocar respostas históricas. Essas abordagens esconderiam a falha ou poderiam
eliminar um impedimento real. A política orienta a geração; não prova que um
modelo a seguirá. O host preserva a resposta e a revisão continua independente.

## Compatibilidade e verificação offline

Default/CLI continuam v3.1; v3.2/v3.3 permanecem idênticas. O schema de saída da
nova receita é o mesmo da v3.3; o fingerprint muda pelo prompt/versão. Não há
migração de contrato, aprovação humana ou seleção operacional automática.

As regressões conferem os oito fingerprints históricos v3.3, o default, a rota de
fontes e a preservação de bloqueios. Exemplos injetados demonstram somente o
comportamento do contrato: trocar explicitamente a materialidade em uma cópia
não apaga outros impedimentos; o host não corrige classificações recebidas.
Não são novas respostas reais nem novos julgamentos humanos.

## Rodada corretiva limitada

O [protocolo próprio](../evidence/sprint-2-6-v34-development-20261020/protocol.json)
congela oito casos de desenvolvimento e a receita antes de executar. O PO pediu
continuidade da sprint; o operador fixa o limite numérico, sem atribuir ao PO uma
declaração que ele não fez. O orçamento v3.3 permanece consumido e encerrado.

Limites desta rodada: até 16 chamadas seriais pela assinatura existente, uma
geração e uma auditoria por caso, 180 segundos por chamada e 3.600 por sessão;
zero retries, repair, holdout, leitura de assets, ferramentas, treinamento ou API
paga. O runner registra todas as tentativas e falhas. Não há rodada adicional
automática. Novos snapshots exigem julgamento próprio; resultados anteriores
não são transferidos. Nenhum candidato é promovido pelo parecer do auditor.

Esta rodada é verificação corretiva de desenvolvimento com uma repetição, não
o experimento repetido AHC-025, medição cold/warm ou qualificação AHC-023. O protocolo
também registra o hash do código-fonte; não substitui os perfis completos AHC-024.

## Plano de trabalho

1. Versionar a política e testar compatibilidade e preservação dos bloqueios.
2. Congelar código/protocolo e executar somente a rodada corretiva delimitada.
3. Preservar respostas e produzir assessments sem aprovações transferidas;
   submeter novos resultados à revisão humana antes de alegar correção semântica.
4. Consolidar a revisão AHC-021/022, mantendo falhas explícitas. Prosseguir para
   AHC-024/025 pelos gates reais; não usar ajustes ilimitados como substituto da comparação.

O incidente permanece aberto até evidência adequada; este incremento não encerra
a história nem a sprint. Fine-tuning, qualificação e promoção não estão autorizados
por um teste offline ou um resultado estruturalmente válido.
