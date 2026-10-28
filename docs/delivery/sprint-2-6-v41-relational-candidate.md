# Sprint 2.6 — candidato relacional v4.1

Data: 2026-10-27. Implementado e preparado offline; eficácia não observada.

## Mudança e limites

O candidato `semantic-composition/v4.1` acrescenta orientação geral sobre regras
relacionais e materialidade das perguntas. Busca corrigir os sintomas confirmados
em [INC-0031 e nos julgamentos do PO](sprint-2-6-v4-development-human-judgments.md):
condições necessárias, permissões, visibilidade exclusiva e ordem temporal precisam
de representação `business-rule`; obrigações incondicionais continuam requisitos.
O titular de um papel desconhecido não bloqueia por si só a análise de intenção,
mas conflitos reais e condições de resultado indefinidas continuam materiais.

Não há regra por caso/ID/nicho, repair ou pós-processamento que converta requisitos
em regras ou rebaixe perguntas para fabricar ready/PASS. O modelo pode continuar
errando; o pipeline deve preservar a saída e sua avaliação. Isso foi verificado
com respostas sintéticas deliberadamente inadequadas, sem afirmar que o modelo
real tenha melhorado.

Fluxo, supervisão e replay escolhem o programa pelo hash já existente no pedido.
A seleção v4.1 é explícita; o preparador continua com v4.0 por padrão. Campanhas
não podem misturar as duas versões. Instruções e digests originais de v4.0, schema
de saída, auditoria v5, rubrica e expectativas permanecem intactos. A
[ADR-0034](../adr/0034-versioned-relational-generation.md) documenta a extensão do
catálogo sem novos campos de contrato ou migração de autorização.

Os arquivos históricos alterados pela integração foram arquivados byte a byte
antes da mudança, endereçados por hash. A campanha anterior e seus julgamentos
continuam verificáveis em replay privado congelado. O runtime atual rejeita seu
pedido antigo contra fontes diferentes; os testes não abriram exceção nesse gate.

## Verificação offline

Os testes cobrem preservação de v4.0; rejeição de hashes/programas desconhecidos;
pacote de entrada e schema idênticos; vínculos de condição/resultado; requisito
sem applicability inventada; preservação de perguntas bloqueantes emitidas pelo
gerador; dispatch/replay nas duas versões; campanha uniforme; e integração com
workers locais contidos. Respostas são sintéticas: testes de engenharia não são
eval de eficácia do modelo.

Uma bateria integrada teve 137 PASS e uma recusa de replay após uma edição de
fonte feita durante sua execução. O gate detectou a divergência com a cópia
congelada do teste. O cenário isolado passou com fontes estáveis, sem relaxar a
validação. A suíte completa posterior usa fontes estáveis; resultados finais
ficam registrados na CI do incremento. Isso não foi falha de uma chamada ao modelo.

## Novo pedido preparado

[Pedido](../../evals/understanding/v4/development-candidate-v41/request.json) ·
[protocolo](../../evals/understanding/v4/development-candidate-v41/protocol.json).

SHA256 canônico:

`84bf9677d4e5fd3468bc5b19e41461b9790656ccaa07d0bc2b99957a22114bbc`.

Vincula 105 arquivos de implementação/configuração e os mesmos oito snapshots do
corpus revisado `8f666df6`, sem modificar seus inputs ou aceites de expectativas.
Os dois casos reprovados são alvos de correção; os seis aprovados entram como
regressão. Os julgamentos anteriores não aprovam respostas futuras. São casos de
desenvolvimento expostos, sem independência ou alegação de holdout.

| Escopo proposto | Limite |
| --- | --- |
| Geração / auditoria | v4.1 / v5; saída permanece SemanticAnalysis/v4 |
| Invocações | Até 16 sequenciais, duas por caso, na ordem do manifesto |
| Sessão global | Até 3.600 s, desde os gates de entrada |
| Chamada / limpeza | Até 180 s; reserva de até 20 s por etapa dentro do prazo global |
| Entrada / saída | 1 MiB / 4 MiB por worker |
| Destino | Assinatura ChatGPT/Codex CLI, modelo solicitado gpt-6.1-sol |
| Parada | Primeira falha técnica; sem retry, repair, fallback, concorrência ou retomada |

Enviar apenas fontes públicas do projeto e, na auditoria, a respectiva análise.
Não enviar expectativas, rubrica, julgamentos ou outros outputs. Sem assets,
reservado, ferramentas, web, API paga por chave, treino ou mudança de defaults.
Um blocked de negócio válido não é falha técnica; falhas semânticas permanecem
avaliáveis depois. Não reutilizar saldo temporal de orçamentos encerrados.

Journals propostos: `.factory/semantic-v4-campaigns/dev-v41-20261027-01/`, com oito
fluxos privados em `.factory/semantic-v4-runs/dev-v41-20261027-01-01/` até `-08/`.
Nenhum desses runs ou claim foi criado por esta preparação.

O pedido precisa de nova `SemanticCampaignAuthorization/v1` vinculada ao hash
acima, após testes/revisão/CI. O aceite anterior julgou os oito outputs antigos;
não concedeu esse orçamento. Ainda não houve chamada ao modelo para v4.1.

Depois de eventual execução, julgar novos snapshots, preservar falhas e comparar
os escopos representáveis. A hipótese conjunta de prompt não isola causalidade de
cada orientação. Não promover defaults, fechar INC-0031 ou qualificar o modelo
apenas por testes sintéticos ou sucesso de transporte. AHC-021/022 e Sprint 2.6
continuam em andamento.
