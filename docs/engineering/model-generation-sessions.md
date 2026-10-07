# AHC-021 — Runner de geração local limitada

`run-understanding-evals` complementa o avaliador offline com geração sequencial
supervisionada. Só o input do projeto vai ao modelo; rubrica/expectativas permanecem
no control plane. Prompt atual não foi otimizado e holdout não foi executado.

```sh
factory run-understanding-evals --corpus evals/understanding/v1 \
  --model ahc-qwen3:4b-instruct-8k --case dev-compatible-rules dev-new-domain \
  --max-attempts 1 --session-seconds 300 --timeout-seconds 180 \
  --context-tokens 8192 --output output/new-session
factory validate-model-session output/new-session --corpus evals/understanding/v1
```

Instalar extra understanding. Sem `--case`, seleciona os casos do split development.
Saída precisa ser nova; plano gravado antes de chamadas e session.json por último.
Um `job-NNN.json` registra cada caso/repetição, inclusive os não executados.
Validador cruza plano, jobs, sessão e corpus. Journal incompleto não passa.

## Budgets

- Até 30 tentativas por sessão, até 3600 s, timeout por job até 300 s (default 180).
- Contexto default 8192, limitado a 512–32768; saída default 4096, até 16384 tokens.
- Repeats de 1 a 3; são chamadas independentes, não retries ocultos.
- Timeout do supervisor usa o menor entre timeout do job e saldo da sessão.
- Worker próprio sem shell, ferramentas ou código gerado, com stdin/stdout JSON
  limitado a 2 MiB; corpo do provider é limitado pelo adapter. Traceback/stderr e
  thinking/system privados do provider não são persistidos.
- Plano/job/sessão limitados a 64 MiB por arquivo para comportar propostas repetidas.
  Falha de I/O pode deixar journal parcial; não faz rollback ou resume automático.

Tentativas incluem preparo/preflight e erros; não afirmam quantidade exata de
chamadas LLM quando há erro. Geração em processo é encerrada em timeout e nenhuma
outra tentativa inicia; cancelamento interno no servidor/GPU não é comprovado.
Criação de processo, validação, escrita e cleanup (até 5 s) podem exceder o budget
nominal; o limite é de admissão/espera, não um SLA de tempo real.

## Identidade e evidência

Ollama local: endpoint loopback fixo, sem redirects/proxies de ambiente. Exige
modelo instalado com formato GGUF; aliases remotos indicados pela API são rejeitados.
Registra nome/digest, família/quantização/tamanho, versão do provider, código do
compilador, Python/plataforma, parâmetros solicitados e hash dos herdados. A API
local é observada, não autenticada; não há atestado criptográfico de execução.

ProviderObservation registra modelo retornado, hash opaco da resposta, tokens e
tempos de carga/prompt/geração quando fornecidos. Ausência fica null; durações
negativas ou componente maior que total são rejeitadas. Métricas são reportadas
pelo provider, sem inferir confiança, SLA ou causalidade.

Identidade/configuração antes/depois e entre jobs precisam coincidir. Mudança
gera error/stopped, sem misturar resultados. `--expected-model-sha256` fixa também
um digest esperado pelo operador. O prompt/producer permanece o código atual.

## Estados

run_status completed significa que todas as tentativas planejadas foram contabilizadas,
não sucesso semântico. limited registra saldo esgotado e stopped timeout/drift.
Jobs usam completed/error/not-run. evaluation_status permanece fail/error/not-run,
e model_qualification é sempre not-established. O relatório offline interno ainda
não estabelece execução isoladamente; a sessão externa contém a observação de geração.

CLI retorna zero para geração completed sem erro, inclusive quando eval=fail;
não é comando de gate de qualificação. Retorna 1 para sessão limitada/stopped/error.
Validação do journal retorna zero por consistência, mesmo que o resultado seja fail.

Holdout é bloqueado enquanto a rubrica v1 não tem review. Requer `--allow-holdout`,
`--expected-model-sha256` e `--candidate-sha256` iguais ao digest de modelo, prompt e
configuração calculado por SessionPlan.candidate_digest(). Declaração não substitui
revisão/cegamento; não usar holdout para tuning.

## Demonstração

Sessão final em `docs/evidence/ahc-021-live-session-final/`: um job do caso público compatível
foi gerado com Qwen3 fixado por digest; o segundo ficou not-run por max_attempts=1.
Com o código final, tempo total observado 28,429 s; provider reportou 1567 tokens
de saída, carga 0,003 s, prompt 0,023 s e geração 27,306 s. Modelo retornado e
metadados permaneceram iguais. Não comparar esses tempos como efeito de uma mudança
de modelo: cache/carga e a saída diferem entre chamadas.
O journal foi validado e eval=fail por regras ausentes. Não é benchmark estatístico
ou qualificação; INC-0007 continua aberto. Energia/RAM por fase e ranking ficam na
AHC-023; rubrica do PO e pipeline de grounding da AHC-022 permanecem pendentes.

O ensaio inicial em `docs/evidence/ahc-021-live-session/` também foi preservado.
Nenhum artefato de execução foi sobrescrito; cada sessão mantém seu código/hash e tempos.
