# Estudo de modelo local — 2026-10-07

Escolha provisória para desenvolvimento: **Qwen3 4B Instruct, Q4_K_M**, perfil
`ahc-qwen3:4b-instruct-8k`. Instalado no D junto ao Qwen3.5 4B para comparação.
Nenhum dos dois foi qualificado semanticamente para concluir a AHC-019.

## Hardware medido

RTX 4050 Laptop com 6141 MiB de VRAM, i7-13620H (10 cores/16 threads),
15,71 GiB de RAM física, cerca de 2,13 GiB livres no início e 249 GiB livres no D.
Driver NVIDIA 616.92; Windows, Python 3.13.7 e Ollama 0.40.0.
RAM livre varia com outros aplicativos; não fechamos aplicações do usuário.

## Comparação documental

| Candidato | Pesos/pacote anunciado | Decisão inicial |
|---|---|---|
| Qwen3 4B Instruct Q4_K_M | 2,5 GB | Alternativa textual leve; testado e escolhido provisoriamente |
| Qwen3.5 4B Q4_K_M | 3,3–4,0 GB conforme artefato | Candidato multimodal inicial; testado, sem preferência semântica confirmada |
| Qwen3 8B | cerca de 5,2 GB | Pouca margem nos 6 GB para contexto e buffers; não instalado |
| Qwen3.5 9B | 6,6–7,6 GB | Excede VRAM só nos pesos; não instalado |

Fontes: [Qwen3 Instruct](https://ollama.com/library/qwen3:4b-instruct),
[Qwen3 8B](https://registry.ollama.com/library/qwen3/tags),
[Qwen3.5](https://ollama.com/library/qwen3.5/tags).
Os model cards oficiais descrevem capacidades multilíngues e licença Apache-2.0:
[Qwen3](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) e
[Qwen3.5](https://huggingface.co/Qwen/Qwen3.5-4B).
Essas informações não demonstram desempenho no nosso pipeline.

A escolha pelo modelo menor é uma inferência de adequação ao hardware, reforçada
pelo ensaio local. Tamanho em disco não equivale ao consumo de VRAM. Aumentar
contexto aumenta memória; [documentação Ollama](https://docs.ollama.com/context-length).
Não habilitamos a janela máxima de 256k, paralelismo de agentes ou cloud.

## Ensaio real

Uma chamada por candidato, mesmo manifesto público `examples/project-definition`,
mesmo prompt do adapter, temperatura zero, `think: false`, contexto 8192,
máximo 4096 tokens de saída, timeout 180 s. Defaults restantes são próprios dos
modelos e constam nos registros. Sem ajuste do prompt entre candidatos.

| Medida | Qwen3.5 4B | Qwen3 4B Instruct |
|---|---|---|
| Tamanho instalado | 3.324.173.968 bytes | 2.497.293.463 bytes |
| Tempo total desta chamada | 172,128 s | 69,284 s |
| Alocação informada por Ollama | 100% GPU, 8192 tokens | 100% GPU, 8192 tokens |
| Leitura pontual NVIDIA | 3933 MiB usados | 3795 MiB usados |
| Schema/referências estruturais | Válidos | Válidos |
| Conteúdo | 1 conflito, 3 perguntas | 15 statements em status hypothesis |
| BusinessRule / DomainCandidate | 0 / 0 | 0 / 0 |

São duas observações, não benchmark estatístico. Inicialização, cache e RAM livre
afetam tempo; não inferir que o segundo é sempre 2,5 vezes mais rápido.
O primeiro carregamento incluiu cerca de 88 s de inicialização nos logs.
Contagens não medem qualidade; ambas as propostas continuam sem revisão/aplicação.

Falhas relevantes da leitura técnica:

- Qwen3.5 registrou como conflito duas regras de aprovação humana que ele próprio
  descreveu como compatíveis. Não extraiu regras ou entendimento principal.
- Qwen3 produziu hipóteses, não declarações confirmadas. Inventou necessidade de
  revisão externa em `s15`; citou branding para uma conclusão sobre domínio em `s4`;
  em `s14`, comentou ausência de conteúdo de asset que não foi lido.
- Ambos omitiram contratos de regras de negócio. Uma referência existente não
  garante que ela suporte a conclusão.

Evidências públicas e metadados: `docs/evidence/model-study-20261007/`.
Não armazenamos thinking, credenciais ou prompts privados. É um ensaio de
desenvolvimento; não substitui rubrica/casos reservados, revisão do PO ou DoD.

## Uso recomendado

```sh
factory study examples/project-definition --model ahc-qwen3:4b-instruct-8k \
  --timeout-seconds 180 --output output/understanding-new.json
```

Criar previamente a pasta de saída e usar arquivo novo. Perfis locais em
`D:\Ollama\profiles` reutilizam pesos; não duplicam downloads. Modelos ficam em
`D:\Ollama\models`. O adapter continua provider-independent e exige modelo explícito;
não alteramos seus defaults nem adotamos o resultado automaticamente.

Próximo gate: rubrica e conjunto reservado, cobertura de regras, suporte real das
citações, conflitos falsos e política de assets não lidos. Escolha final de modelo
depende desses evals; a escolha atual atende à operação local experimental.
