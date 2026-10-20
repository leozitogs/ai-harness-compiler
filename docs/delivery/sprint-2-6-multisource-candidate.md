# Sprint 2.6 — Candidato com perguntas de múltiplas fontes

Data: 2026-10-20. AHC-022; não conclui histórias ou qualifica modelos.

## Correção implementada

`semantic-composition/v3.3` conserva o tratamento de obrigações sem gatilho da
v3.2 e encaminha perguntas secundárias para `issues`. Perguntas locais de um
critério herdam apenas o átomo desse critério; por isso não servem para comparar
declarações de origens distintas. Uma issue possui seus próprios índices de contexto.

Na variante v3.3, o schema exige `uncertainties=[]`, restringe os índices às
fontes disponíveis e o host rejeita perguntas secundárias na rota antiga mesmo
se um provider ignorar o schema. Índices duplicados continuam rejeitados pelo
contrato no host. Não há adição automática de fontes nem reescrita de respostas.
Uma pergunta primária de esclarecimento ainda pode citar seu próprio critério;
interpretações que dependem de outras fontes devem usar uma issue.

As versões v3.1/v3.2 mantêm prompts e fingerprints históricos. Default e CLI
continuam v3.1. A nova versão é selecionada explicitamente pela API Python, sem
trocar o modelo principal. Revisões antigas são rejeitadas para análises alteradas.

## Protocolo congelado antes da rodada

[Protocolo ativo](../evidence/sprint-2-6-v33-development-20261020/protocol-v2.json):
oito casos públicos de desenvolvimento, previamente congelados e julgados pelo PO.
O operador fixa limites sob a autorização existente para continuar a sprint e usar
a assinatura; não atribui ao PO uma nova declaração sobre os números do orçamento.

- Até 16 chamadas: uma geração e uma auditoria por caso válido.
- Uma chamada por vez, 180 segundos por chamada, teto de sessão de 3.600 segundos.
- Uma rodada, zero retries, zero repair, nenhum holdout, asset ingerido ou treino.
- Codex CLI / `gpt-6.1-sol` via integração existente da assinatura; sem fallback,
  serviços de API pagos, novas permissões de ferramentas ou mudança de parâmetros.
- Modelo observado, custo, sampler e outros dados não expostos permanecem desconhecidos.

As respostas de auditoria são consultivas. Cada chamada registra hashes de prompt,
schema e schema efetivo, status inicial/final e tempo; somente a resposta final do
modelo é retida. Logs intermediários privados e credenciais não são armazenados.
Falha de geração não é aprovação nem gatilho de retry; sua auditoria fica não executada.

A preparação inicial `protocol.json` nunca foi executada. Foi substituída por
`protocol-v2.json` antes das chamadas para manter unicidade no host e usar no schema
apenas as restrições selecionadas. A documentação oficial descreve um subconjunto
de JSON Schema e lista `minItems`/`maxItems` para arrays; não foi observado erro
remoto de rejeição do primeiro schema. [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

O uso de `codex exec` com schema de saída segue o mecanismo de execução estruturada
documentado, mantendo as restrições mais estreitas do adapter deste repositório.
[Exemplo oficial](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex).

## Limites da comparação

A referência histórica contém sete gerações válidas e uma tentativa com erro,
com recuperação separada. Os cinco passes e três fails humanos pertencem às
respostas selecionadas daquela referência, nunca ao novo candidato.

Uma nova rodada sem repetições não mede estabilidade nem estabelece causalidade,
latência cold/warm, ganho de recursos ou desempenho de produção. A revisão humana
das novas respostas permanece necessária. Alterar suporte, IDs ou representação
invalida os aceites anteriores; não há migração automática.
