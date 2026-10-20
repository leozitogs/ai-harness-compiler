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

## Rodada executada

O [registro comparativo](../evidence/sprint-2-6-v33-development-20261020/comparison.json)
conserva todos os casos e tentativas. Foram executadas **16 chamadas seriais**, com
oito gerações válidas e oito auditorias válidas, sem retry/repair. Tempo observado
do runner: 468,018132 segundos; não é medição cold/warm nem evidência de ganho de latência.
Os inputs foram conferidos contra o manifesto congelado antes das chamadas.

As oito disposições coincidem com as expectativas congeladas: seis `ready`, duas
`blocked`. Isso apenas verifica a disposição; os oito assessments iniciais ficam
`not-run` sem revisão humana. **Zero reviews históricas reutilizadas**: todas as
análises mudaram de snapshot. A referência selecionada conserva cinco passes e
três fails humanos, incluindo um pass de recuperação e a tentativa original error.

Os novos artefatos contêm 74 achados e 24 componentes. O auditor registrou nove
possíveis omissões e nenhum componente negativo; contagens consultivas não são
métricas de qualidade sem adjudicação. Nas respostas observadas, a pergunta de
precedência cita os dois lados e as obrigações de identidade não recebem o guard
anterior. Isso não comprova completude ou pertinência de todas as perguntas.

A inspeção também identificou perguntas adicionais de identidade como dúvidas
bloqueantes de regra nos dois casos `blocked`. Elas precisam de julgamento próprio:
um impedimento legítimo não torna automaticamente pertinentes todos os demais.
Os textos completos, átomos, inventários e diagnósticos estão no
[pacote de revisão](../reviews/sprint-2-6-v33-development/dev-branding-conflict.md).
As duas perguntas objetivas ao PO distinguem as seis respostas ready desses dois casos.

As regressões offline reproduzem os vínculos e limites da rodada, não a geração:
testam 16 chamadas numeradas, protocolos/hashes, snapshots, budgets e o estado
inicial sem aprovação humana. Nenhum teste padrão chama o provider.

## Julgamento humano posterior — rodada encerrada

O PO respondeu “Aprovo os seis critérios das seis novas respostas ready” e
“Confirmo: incerteza fail e os outros cinco critérios pass nos dois casos”.
O [manifesto humano](../evidence/sprint-2-6-v33-development-20261020/human-review/manifest.json)
vincula declarações reais, cobertura, suporte de cada achado/componente e
assessments aos novos hashes. Declarações são humanas declaradas, sem autenticação
independente. Não são pareceres do auditor convertidos para aceite.

| Snapshot v3.3 | Resultado humano | Critérios reprovados |
| --- | --- | --- |
| dev-adversarial | pass | nenhum |
| dev-ambiguous | fail | uncertainty |
| dev-branding-conflict | fail | uncertainty |
| dev-compatible-rules | pass | nenhum |
| dev-new-domain | pass | nenhum |
| dev-rules-a | pass | nenhum |
| dev-rules-b | pass | nenhum |
| dev-unread-assets | pass | nenhum |

Resultado final desta rodada: **6 pass, 2 fail; 46 critérios pass e 2 fail,
zero critérios pendentes**. As oito disposições coincidiam com a expectativa,
mas isso não detectava as duas perguntas indevidamente bloqueantes. O suporte
de fontes e a pertinência/materialidade são eixos distintos: as perguntas têm
fonte, mas o PO confirmou que não devem impedir esta análise de intenção.

Cobertura e citações das falhas anteriores foram aprovadas nestes snapshots
específicos. Isso permite registrar a resolução escopada dessas falhas, sem
concluir que toda pergunta futura será completa ou material. Os dois fails novos
permanecem explícitos e impedem qualificação/promoção. O auditor LLM não substitui
esse julgamento de negócio.

O orçamento de 16 chamadas foi consumido e a rodada foi encerrada. **Nenhuma chamada
adicional, retry ou repair foi executado depois dos julgamentos.** As avaliações
iniciais `not-run` e o pacote de revisão são snapshots anteriores preservados;
o manifesto humano é o estado posterior, sem reescrever respostas.

Próxima tarefa: estudar a política de materialidade de perguntas sobre restrições
normativas e preparar uma correção generalista versionada. Não inserir nomes de
casos no core, remover perguntas em pós-processamento ou enfraquecer a rubrica para
fazer o candidato passar. Nova rodada exige protocolo/orçamento próprio; AHC-024/025/026
continuam sujeitas aos gates de dependências. Default permanece v3.1; candidato não promovido.
