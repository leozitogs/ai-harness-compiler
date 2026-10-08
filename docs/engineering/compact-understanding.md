# AHC-022 — Propostas compactas e projeção literal

```sh
factory run-understanding-evals --corpus evals/understanding/v1 \
  --analysis-mode compact --model ahc-qwen3:4b-instruct-8k \
  --expected-model-sha256 59d7f50962ef280aacad2867d041c13e22ad2d08827df5ec407ff75d348f8c90 \
  --max-attempts 8 --session-seconds 1800 --timeout-seconds 180 \
  --context-tokens 8192 --max-output-tokens 4096 --output output/new-compact-session
factory validate-model-session output/new-compact-session --corpus evals/understanding/v1
```

O modo compacto usa o runner existente: uma chamada por worker/tentativa, sem
retries e sem repair automático. Baseline continua default; repair existente é
exclusivo do modo grounded. Saída precisa ser nova. Leitura, rede e subprocessos
mantêm os mesmos limites e fronteiras.

## Responsabilidades

O programa v2 acrescenta cada critério ao final da lista de contexto citável,
permitindo conflitos entre branding e backlog com os dois source_refs originais.
Os índices antigos continuam iguais. `source_path` identifica o campo do valor,
inclusive constraints numéricas; o modelo continua sem gerar IDs ou citações.
O histórico v1 permanece uma observação do programa anterior, não uma medição v2.

| Parte | Responsabilidade |
|---|---|
| Extração | Snapshot completo e evidências literais canônicas |
| CompactInput | Contexto elegível, critérios ordenados, SHA e contagem de assets não lidos |
| Modelo | Classificação proposta, condição/resultado/pergunta e inferências de contexto |
| Projeção | IDs únicos, descrição/citação literal e source_ref do critério original |
| Validação | Quantidade/ordem, tipos, índices e igualdade entre interpretação/projeção |
| Revisão | Significado, alinhamento por posição, suporte, conflitos e necessidade das perguntas |

Regras do modelo são hipóteses; texto literal não confirma condição/resultado.
Achados de contexto são hipóteses e domínio continua livre, com confidence null.
Uncertainties viram perguntas bloqueantes. Não criamos review nem aprovamos o
projeto. O pacote não carrega rubrica, expectativas ou gold labels para o modelo.

## Tamanho da representação

No dev-compatible-rules, serialização UTF-8 do input grounded tem 8661 bytes;
CompactInput tem 1508. Schema de resposta JSON: 5264 bytes no grounded e 2673 no
compacto, usando o mesmo json.dumps para a medição. São tamanhos da representação,
não contagem universal de tokens nem prova de melhoria semântica/latência.

## Primeiro smoke

Um preflight falhou porque o Ollama não estava ativo; nenhuma inferência ocorreu
nesse smoke. Serviço instalado em D foi iniciado em background e o journal foi
preservado, sem sobrescrever evidências.

O smoke seguinte gerou uma proposta válida em 25,505 s: quatro regras, todas
hipóteses, quatro achados de contexto e perguntas de confirmação. Observações do
provider: 675 tokens de prompt, 1098 de saída, load=5,595 s, geração=18,582 s.
O segundo caso foi not-run por max-attempts=1. Avaliação ficou not-run.

Achados de revisão técnica: notas chamam requisitos explícitos de implícitos e
o candidato de domínio cita restrições técnicas, embora o nicho esteja descrito
na concepção. Isso evidencia que a aceitação estrutural não resolveu suporte
semântico. Observações técnicas não são HumanDeclaration/aceite do PO.

Há uma comparação dos oito casos de development em docs/evidence. Nenhum holdout
foi executado, a rubrica segue proposta e não existe modelo qualificado. Ver o
relatório de comparação de desenvolvimento para resultados e limitações.
