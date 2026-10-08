# Fundamentação e protocolo experimental do entendimento

Consulta de fontes primárias em 2026-10-08. Este documento fundamenta hipóteses
de engenharia para AHC-022/023; não certifica cientificamente o compilador, um
modelo, uma composição de agentes ou os resultados do corpus interno.

## Problema observado

A [comparação de development](../delivery/ahc-022-development-comparison.md)
registrou quatro propostas estruturalmente válidas na baseline e seis no modo
compacto, em oito casos por programa e uma repetição. As seis propostas compactas
ficaram com avaliação semântica `not-run`. A projeção literal preserva citações,
mas não prova que condição, resultado ou inferência sejam sustentados por elas.
O smoke também mostrou domínio associado a restrições técnicas e perguntas
desnecessárias sobre critérios explícitos. Esses são alvos de investigação,
não exemplos de sucesso semântico.

## Evidências e limites de transferência

| Estudo primário | Resultado relevante | Consequência para o projeto |
|---|---|---|
| [Dhuliawala et al., CoVe, Findings ACL 2024](https://aclanthology.org/2024.findings-acl.212/) | Responder perguntas de verificação independentemente antes da revisão reduziu alucinações nas tarefas factuais estudadas. | Testar extração independente das mesmas fontes, seguida de confronto com a proposta. O estudo não demonstra cobertura de regras de negócio, adequação do nosso corpus ou benefício de LangGraph. |
| [Huang et al., ICLR 2024, versão 2](https://arxiv.org/html/2310.01798v2) | Autocorreção de raciocínio sem feedback externo frequentemente não melhorou resultados e pôde degradá-los. Comparações com orçamento equivalente mudaram a interpretação de ganhos de debate. | Evitar tratar a aprovação do próprio gerador como evidência. Comparar revisão com outra chamada independente sob orçamento semelhante; o resultado não proíbe toda autocorreção nem descreve os modelos atuais. |
| [Zheng et al., NeurIPS 2023, versão 4](https://arxiv.org/html/2306.05685v4) | Juízes LLM apresentaram vieses de posição, extensão e favorecimento próprio, além de limitações de avaliação. O trabalho também mostrou utilidade em aproximar preferências humanas. | Usar parecer automático como diagnóstico; calibrar contra revisão humana e trocar a ordem de respostas em comparações. Preferência conversacional não equivale a suporte de regras de negócio. |
| [Cemri et al., MAST, versão 2](https://arxiv.org/html/2503.13657v2) | A análise de sete frameworks e mais de 200 tarefas identificou 14 modos de falha ligados a especificação, alinhamento e verificação. | Definir contratos de passagem, responsáveis e término. Mais agentes não são garantia de qualidade; os sistemas estudados não representam diretamente este compilador. |
| [Zhang et al., AFlow, versão 3](https://arxiv.org/html/2410.10762v3) | Busca de workflows com feedback de execução foi avaliada em seis benchmarks de matemática, código e perguntas/respostas, com separação entre validação e teste. | Tratar topologia como hipótese comparável, conservar holdout e medir custo. Não transferir os percentuais publicados para entendimento de projetos nem executar código gerado pelo modelo no compilador. |
| [Dąbrowski et al., preprint de agosto de 2026](https://arxiv.org/html/2608.21531v1) | A avaliação entre tarefas de engenharia de requisitos encontrou desempenho dependente da tarefa; classificação/rastreabilidade e geração usaram avaliações distintas. O caso industrial possui limites de generalização. | Avaliar cobertura, rastreabilidade e interpretação separadamente; não escolher modelo por ranking universal. É um preprint e não uma validação independente do AHC. |

As consequências acima são inferências de engenharia, não reprodução dos estudos.
Uma chamada que recebe apenas o input e produz uma interpretação sem ver a
proposta anterior é independente na apresentação do contexto. Isso não torna
os erros estatisticamente independentes: modelos podem compartilhar treinamento,
família, instruções e vieses. Um segundo fornecedor também pode concordar com
uma interpretação incorreta.

## Arquitetura experimental proposta

O núcleo continua provider-independent. Um executor opcional pode coordenar
etapas por LangGraph, com estado tipado, limites de chamadas e journal, sem
colocar o framework nos contratos de domínio. A biblioteca organiza controle;
ganho semântico exige medição própria.

1. Preparar snapshot e átomos literais deterministicamente. Não incluir gold
   labels, rubrica com respostas esperadas ou avaliações anteriores no input
   do gerador. Não ler conteúdo de assets declarado como não lido.
2. Produzir interpretações independentes com o mesmo pacote elegível. Separar
   classificação de critérios, domínio/branding e conflitos, se essa divisão
   for o objeto da ablação. Guardar hipóteses e dúvidas, sem confidence inventada.
3. Projetar IDs e citações pelo compilador e validar referências, inventário,
   limites e igualdade literal. Falha estrutural não desaparece por votação.
4. Confrontar divergências e suporte usando fontes originais e parecer tipado.
   O parecer precisa identificar achado e fonte; `agree` sem suporte não basta.
   Parecer de modelo não vira `HumanSemanticReview` nem autorização do PO.
5. Permitir no máximo a revisão prevista no plano e contabilizar cada chamada,
   inclusive erro, timeout e preflight. Terminar por sucesso de contrato,
   divergência pendente ou orçamento esgotado; manter significado não avaliado.
6. Entregar proposta, verificações e divergências para adjudicação humana.
   Aprovar relatório não inicia sprint, não conclui história e não instala
   alterações em um projeto de destino.

Registrar tarefas, dependências, decisões resumidas, evidências e verificações.
Não exigir, persistir ou afirmar acesso a cadeia de pensamento privada.
Artefatos destinados a documentação e aprendizado devem distinguir observação,
hipótese e decisão; apenas soluções verificadas justificam lições reutilizáveis.

## Protocolo para comparar alternativas

Antes da execução, congelar programa, perfil, corpus e plano. A revisão da rubrica
e dos critérios de qualificação pelo PO continua pendente; experimentos em
development podem investigar falhas, mas não contornam a aprovação para holdout.

| Braço | Objetivo |
|---|---|
| Compacto com modelo local | Referência com o contrato já implementado |
| Mesmo programa com modelo via Codex CLI | Isolar efeito observado da troca de executor/modelo |
| Duas propostas independentes, sem revisão | Referência com mais chamadas para separar efeito de orçamento |
| Proposta mais verificador, com revisão limitada | Estimar benefício específico da verificação |
| Especialistas coordenados por grafo | Avaliar se divisão de responsabilidades compensa a complexidade |

Executar apenas braços realmente implementados. Usar os mesmos casos pareados,
alternar ordem entre repetições e registrar estado frio/quente do modelo, CA,
identidade observada do executor e hashes. Três repetições por caso são um mínimo
operacional proposto, não garantia de poder estatístico. Erros e ausência de
resultado entram no denominador; não comparar só propostas aceitas.

Comparar primeiro por número de chamadas e limites de saída/tempo equivalentes.
Registrar tokens efetivamente observados quando disponíveis. Tokens de modelos
distintos não são uma unidade universal de esforço; orçamento da assinatura
Codex não equivale a custo marginal de API ou custo energético local. Informações
indisponíveis ficam ausentes, nunca zero. Oito casos repetidos continuam sendo
oito casos, não 24 projetos independentes.

Separar as métricas:

- **Estrutura:** proporção de propostas aceitas pelo contrato e classes de erro.
- **Semântica:** cobertura das regras esperadas, suporte de condição/resultado,
  precisão dos vínculos de fonte, conflitos falsos/omitidos, necessidade de
  esclarecimento, respeito a assets e incerteza. Julgamento humano usa critérios
  congelados e examina cada achado; número de regras não é recall semântico.
- **Operação:** chamadas tentadas, conclusão por caso, tempo total e por etapa,
  tokens observados, timeout e interferência de concorrência no hardware.
- **Juiz:** acordo e desacordos com humanos por critério; se houver comparação
  A/B, avaliar também B/A e conservar inconsistências. Identidade do candidato
  deve ser ocultada quando praticável.

Para nova revisão humana, preferir dois avaliadores independentes, sem indicação
de fornecedor/programa, com adjudicação dos desacordos. Se houver só um avaliador,
registrar essa limitação. Publicar tabela por caso e distribuição entre
repetições; não resumir tudo em um único score. Intervalos ou análises estatísticas
devem usar o caso como unidade e explicar a dependência entre repetições.

Promover uma composição somente quando reduzir erros semânticos relevantes sem
regressões críticas e com custo operacional aceitável para o PO. Sem adjudicação,
o resultado é comparação estrutural e diagnóstico proposto. O holdout permanece
fora de otimização: após congelar candidato e obter os gates previstos, executar
sem adaptar prompts ao resultado. Exposição ou adaptação exige registrar a
contaminação e preparar outro holdout para a próxima qualificação.

## Privacidade, segurança e reprodução

Chamadas via assinatura ou servidor local são opt-in e ficam fora dos testes
default. Usar dados sintéticos ou conteúdo explicitamente autorizado. Não copiar
tokens de autenticação, prompts privados, logs internos de raciocínio ou arquivos
do usuário para evidência pública. O executor deve recusar ferramentas/ações
fora do plano; prompts de papel não constituem isolamento. Paralelismo deve
respeitar limites globais e registrar falhas de cancelamento, sem presumir que
um timeout do processo interrompeu a inferência no servidor.

Reprodução exige snapshots autorizados, hashes, contratos, configuração observada,
journals e scripts de validação. Hash comprova correspondência de bytes, não
autenticidade da execução ou verdade semântica. Alterações posteriores geram
novas evidências e revisões imutáveis de memória, preservando os achados anteriores.
