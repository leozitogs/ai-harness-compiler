# Diagnóstico offline de transporte e conflitos

Os contratos novos são aditivos: `WorkerDiagnostic/v1` e
`ConflictQuestionDiagnostic/v1`. Os schemas estão em `schemas/`. Não migram nem
modificam contratos ou resultados históricos.

## Categorias de worker

| Exit | Categoria | Etapa |
|---|---|---|
| 20 / 21 / 38 | limite / contrato inválido / I/O de entrada | input |
| 22 / 23 / 24 | CLI indisponível / assinatura requerida / timeout de autenticação | provider |
| 25 / 26 / 27 | timeout / erro reportado / limite de saída do adapter | provider |
| 28 / 29 / 30 | protocolo inválido / evento de ferramenta / stream incompleto | provider |
| 31 / 35 / 36 | falha sem categoria específica / limite de entrada / I/O | provider |
| 32 / 33 | codificação / I/O de saída | output |
| 34 / 37 | falha interna / preparação do provider | unknown / setup |
| 2 e demais desconhecidos | unknown | unknown |

Categorias reportadas pelo worker indicam onde investigar; não distinguem causas
internas do serviço como quota, autenticação ou indisponibilidade. O recibo deve
conservar status failed e failure_code worker-failed. Outros erros do supervisor
recebem not-worker-failure e mantêm seu código original. Um processo arbitrário
também pode emitir esses números; a confiança depende da fonte e comando congelados.

## Inspeção sem inferência

Criar previamente o diretório privado de saída e indicar explicitamente um
artefato local. O comando recusa arquivo já existente e saída fora de `.factory/`.

```sh
uv run python scripts/inspect_semantic_diagnostics.py --receipt .factory/example/receipt-1.json --output .factory/example/worker-diagnostic.json
uv run python scripts/inspect_semantic_diagnostics.py --analysis .factory/example/analysis.json --output .factory/example/conflict-question-diagnostic.json
```

O relatório de conflito contém a análise completa: deve permanecer privado como
o original. Um conflito sem pergunta, pergunta que cite um lado só ou pergunta
implementation-detail não satisfaz a checagem. A presença estrutural de uma
pergunta precedence com ambos os lados ainda exige julgar seu significado.

O v4.2 é um candidato opt-in por digest. Seu prompt pede conflito e pergunta
separados, sem escolher precedência ou bloquear normas compatíveis. A checagem
offline preserva omissões para observação; não converte resultados em aprovação
nem impede a retenção da resposta. As expectativas aprovadas continuam iguais.
