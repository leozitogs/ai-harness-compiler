# AHC-004 — Confiabilidade e benchmark offline

## Emissão e falhas

O compilador valida/renderiza a IR antes de reservar a saída com mkdir exclusivo.
Qualquer diretório ou arquivo existente é recusado, sem abrir artefatos dentro dele.
Os arquivos são escritos com criação exclusiva e UTF-8/LF; o manifesto de integridade
é emitido por último.

| Diagnóstico | Comportamento |
|---|---|
| COMPILE_EXISTS | Destino existente; não reutilizar nem sobrescrever |
| COMPILE_RESERVE | Falha ao reservar nova saída |
| COMPILE_WRITE | Falha ao criar/escrever/fechar artefato; saída nova pode estar parcial |

A CLI retorna 1. Causas de I/O são encadeadas na API Python. Uma saída parcial é
preservada para diagnóstico: **não instalar**, e repetir em outro diretório novo.
Não há rollback destrutivo, merge em projetos existentes ou promessa de emissão
transacional/durabilidade após falta de energia. Se a escrita do manifesto falhar,
ele próprio pode estar parcial: sua presença sozinha não indica conclusão.

`verify_bundle()` verifica hashes e contenção dos caminhos sem executar o hook
gerado. O hook existente continua disponível para o usuário. Integridade não é
assinatura/autenticidade nem prova de correção do produto; um manifesto adulterado
junto com arquivos não estabelece confiança independente.

## Fixtures e rastreabilidade

`benchmarks/suite.json` identifica três manifestos reais:

| Fixture | Domínio | Capacidades |
|---|---|---|
| education | education | source-library → lesson-draft |
| commerce | commerce | inventory → order |
| dev-tools | developer-tools | contract-scan → review-report |

Cada manifesto tem quatro critérios de aceitação. Os testes verificam preservação
dos critérios no plano de evals, domínio, referências, hashes e igualdade dos bytes
em duas compilações. As capacidades são requisitos dos projetos fictícios: o
compilador não implementa funcionalidades comerciais/educacionais, e seus evals
continuam not-run.

## Executar e interpretar o benchmark

```sh
factory benchmark benchmarks/suite.json --workspace output/benchmark-new --output output/benchmark-new.json --runs 5
factory schema benchmark-report
```

Workspace e relatório devem ser novos; o diretório pai do relatório deve existir.
Fixtures não podem escapar da pasta da suíte. Leitura da suíte/manifesta é limitada
a 1 MiB. São necessárias pelo menos duas repetições para verificar reprodução.
Os builds são sequenciais no mesmo processo, sem warmup descartado, chamadas a
providers ou execução de código gerado.

Cada amostra mede com perf_counter_ns: intake, checks da fixture/input, planejamento,
compilação, verificação de integridade e contagem de bytes. Registra duração, bytes,
quantidade de arquivos e digest do bundle. O relatório registra versões do compilador,
Python/Pydantic, implementação Python, sistema/release, digest da suíte/input e
digest dos arquivos Python do pacote. Não inclui caminhos absolutos, hostname ou
conteúdo privado de prompts.

Hash divergente entre repetições, fixture alterada, critérios incompatíveis ou falha
de I/O interrompem a execução sem emitir relatório de sucesso. Builds parciais podem
permanecer no workspace. Relatório não representa SLO, capacidade de produção,
latência de LLM ou avaliação do produto.

## Baseline medida

Resultado bruto: [Windows/Python 3.13](../../benchmarks/results/baseline-windows-python313.json).
Execução de 2026-10-06, compilador 0.1.0, cinco builds por fixture, zero warmups.

| Fixture | Mediana (ms) | Bytes por bundle | Arquivos |
|---|---:|---:|---:|
| education | 92,982 | 41.614 | 19 |
| commerce | 84,922 | 41.336 | 19 |
| dev-tools | 83,495 | 41.685 | 19 |

Todas as 15 emissões tiveram integridade e hashes iguais dentro de cada fixture.
Não comparar estes números sem controlar código, dependências, hardware, filesystem
e cache. A amostragem é pequena, sem isolamento de máquina ou análise estatística
de caudas; nenhuma meta de desempenho foi aprovada.
