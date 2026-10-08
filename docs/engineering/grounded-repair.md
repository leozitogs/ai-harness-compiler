# AHC-022 — Repair limitado e auditável

```sh
factory run-understanding-repair --corpus evals/understanding/v1 \
  --case dev-compatible-rules --model ahc-qwen3:4b-instruct-8k \
  --expected-model-sha256 59d7f50962ef280aacad2867d041c13e22ad2d08827df5ec407ff75d348f8c90 \
  --max-repairs 1 --max-attempts 2 --session-seconds 300 --timeout-seconds 180 \
  --context-tokens 8192 --max-output-tokens 4096 --output output/new-repair
factory validate-understanding-repair output/new-repair --corpus evals/understanding/v1
```

Um caso de development por sessão. --max-repairs admite 0–2; o total de chamadas
é no máximo max-repairs+1 e também respeita max-attempts. Cada tentativa usa processo
próprio sem retries internos. O menor entre timeout e saldo da sessão rege a admissão.
SHA do modelo é obrigatório; nenhum profile é ajustado automaticamente.

## Registros e encerramento

plan.json, attempt-NNN.json e repair.json compõem o journal completo. Cada tentativa
preserva request original, diagnóstico usado, resultado, offset/tempo e timeout.
Não há proposta rejeitada, thinking ou erro privado do provider no diagnóstico.
Inventário de arquivos é fechado; acrescentar/remover uma tentativa invalida o journal.

| Encerramento | Significado |
|---|---|
| completed | Uma proposta passou pelos contratos; o eval permanece separado |
| repair-limit | Todas as correções configuradas foram consumidas sem aceitar proposta |
| attempt-limit/time-limit | Um repair elegível não foi executado por budget |
| not-repairable | O erro não produziu diagnóstico elegível; nenhuma nova chamada |
| worker-timeout/model-changed | Interrupção; não há próxima chamada |

Retorno zero do comando de geração indica completed, mesmo com eval fail/not-run.
Retorno zero do validador indica journal consistente, inclusive de uma sessão rejeitada.
Completar um inventário não comprova regra, condição/resultado ou suporte semântico.
Nenhum resultado vira review aprovado, história Done ou modelo qualificado.

## Diagnóstico

Códigos criterion-* usam IDs de átomos; declared-quote-invalid,
extracted-quote-invalid e proposal-reference-invalid usam referências originais.
Motivos são enumerações fixas. Source refs excluídos e escopos de outro input não
entram no feedback. SHA de proposta é identificador opaco, não conteúdo armazenado
nem prova autenticada de execução. repair usa programa versionado por texto/schemas.

## Evidência em 2026-10-08

Primeiro smoke: uma tentativa, 19,790 s de sessão, grounded-analysis-invalid,
sem diagnóstico elegível; terminou not-repairable. O resultado foi preservado.
Depois de detalhar diagnósticos, um segundo smoke executou duas tentativas:

- 19,723 s: proposal-reference-invalid, feedback com inventário elegível de input refs.
- 44,177 s: criterion-inventory-invalid, esperado atom-16/17/19/20; terminou repair-limit.

Tempo total: 63,912 s. Ambos os journals foram validados. A saída rejeitada não foi
armazenada, então o diagnóstico não diferencia omissão, troca de IDs ou ordem no
inventário inválido. Nenhuma proposta foi aceita e nenhum eval semântico foi executado.

Alimentação observada antes do primeiro smoke: PowerOnline=true, Charging=true,
Discharging=false. Tempos de tentativas únicas com cache não controlado; não são
benchmark ou comparação causal. Não houve execução de holdout.

Próximos passos: revisar rubrica/expectativas, comparar qualidade no development,
congelar candidato e avaliar holdout/repetições conforme AHC-023. INC-0007 permanece aberto.
