# Sprint 2.6 — Otimização experimental de modelos

Status: **iniciada em 2026-10-19**, por pedido explícito do PO após encerrar a 2.5.5.
O [kickoff e a auditoria executada](sprint-2-6-kickoff.md) registram a fase atual:
revisão dos pré-requisitos e baseline antes dos experimentos. Seleção adaptada para
incluir AHC-021/022/023 remanescentes junto de AHC-024/025/026; não houve declaração
fictícia de conclusão para liberar o TaskGraph. Não há prazo, capacidade ou ganho prometido.

A Sprint 2.5.5 do Nexo foi posicionada antes desta sprint por pedido posterior do
PO. Sua review (ou repriorização explícita) e os gates semânticos remanescentes da
2.5 precedem os experimentos; uma proposta do Nexo não qualifica o modelo.

## Objetivo e entrada

Comparar perfis rastreáveis por qualidade semântica, estabilidade e recursos, e
decidir com evidência se treinamento adicional se justifica. A entrada exige revisão
dos resultados/pendências da Sprint 2.5 e baseline julgável, mesmo se rejeitada.
Não exige fabricar um vencedor nem declarar modelo qualificado previamente.

## Sequência verificável

1. AHC-024: versionar perfis por provider, parâmetros aceitos e fingerprint integral.
   Registrar solicitado/observado/desconhecido; rejeitar opções incompatíveis.
2. AHC-025: comparar baseline e perfis candidatos no desenvolvimento, com repetições,
   orçamento por sessão, fontes corretas, cobertura, falsos conflitos/bloqueios,
   estabilidade, truncamento, tempos cold/warm, RAM e VRAM.
3. AHC-026: decidir go/no-go de LoRA/QLoRA após identificar erro recorrente aprendível,
   curar dados revisados e medir viabilidade de memória. Piloto condicionado; decisão
   no-go documentada também atende ao objetivo de viabilidade.
4. Congelar candidato antes da avaliação separada e promover ou rejeitar por evidência.
   Não reutilizar holdout observado para otimizar nem esconder tentativas malsucedidas.

Baseline Ollama atual usa temperatura zero. Comparação inicial proposta: baseline,
baixa temperatura e recomendação do autor do Qwen3-4B-Instruct-2507 (`temperature=0.7`,
`top_p=0.8`, `top_k=20`, `min_p=0`). Separar mudança de temperatura de mudança conjunta
do sampler; depois variar contexto/saída conforme diagnóstico. Valores são candidatos,
não melhoria comprovada. Seed não assegura identidade entre ambientes/backends.

Codex CLI: explicitar esforço suportado por modelo/cliente; não presumir parâmetro
de temperatura disponível. O adapter atual ignora configuração pessoal. Alterar apenas
a chamada seria insuficiente: SessionSettings/v1 e fingerprint fixam temperatura zero;
evoluir contrato antes do experimento, preservando históricos.

## Treinamento e generalização

RTX 4050 Laptop 6 GB e RAM física próxima de 16 GB foram observadas anteriormente,
não medidas novamente neste planejamento. Treinamento completo de 4B em 16 bits já
excede VRAM apenas em pesos. QLoRA pode reduzir memória, mas ativações/contexto/otimizador
continuam relevantes; piloto limitado não garante viabilidade nem qualidade.

Treinar procedimentos generalistas de regras, guards, evidência e incerteza; regras
de negócio de cada projeto continuam no input/contexto. Não treinar a partir de
autoaprovação, memória privada ou raciocínio interno. Dataset tem origem, licença,
consentimento, deduplicação e separação por projeto/família antes do treino.

Comparar base e adapter sob prompt e decodificação equivalentes, e também contra a
melhor baseline sem treino. Avaliar exportação/quantização de implantação, não apenas
checkpoint de treino. Regredir domínio novo, negação, exceções, regras divergentes,
assets e injeção; investigar perda de generalização, vazamento e esquecimento.

Principal `gpt-6.1-sol` não suporta fine-tuning na documentação consultada. Não há
treinamento incluído pela assinatura Codex. Serviços pagos ou hardware externo
exigem proposta concreta de custo e autorização antes de contratação.

## Fontes consultadas em 2026-10-19

- [Qwen3 4B Instruct: parâmetros recomendados](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507).
- [Ollama: parâmetros de execução](https://docs.ollama.com/modelfile).
- [Codex: esforço de raciocínio por modelo/cliente](https://learn.chatgpt.com/docs/config-file/config-reference).
- [GPT-6.1 Sol: suporte a fine-tuning](https://developers.openai.com/api/docs/models/gpt-6.1-sol).
- [OpenAI: ciclo de otimização com evals](https://developers.openai.com/api/docs/guides/model-optimization).
- [QLoRA, artigo original](https://arxiv.org/abs/2305.14314) e
  [PEFT: quantização](https://huggingface.co/docs/peft/developer_guides/quantization).

A literatura fundamenta técnicas possíveis; não estabelece eficácia no AHC ou consumo
no notebook. O resultado da sprint deve permitir manter a baseline sem treinamento.
