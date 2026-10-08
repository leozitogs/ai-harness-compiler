# Comparação experimental local + Codex CLI

O núcleo continua independente de provedores. LangGraph pertence ao extra `team`.
Codex CLI é executável externo opcional; não se torna dependência do compilador.
O login existente com ChatGPT é confirmado por `codex login status`; não copiar
auth.json, tokens ou chaves para o projeto.

A documentação oficial estabelece [login com assinatura](https://learn.chatgpt.com/docs/auth)
e [execução não interativa com JSON Schema](https://learn.chatgpt.com/docs/non-interactive-mode).
O experimento força ChatGPT e remove overrides de API key do ambiente do filho.
Primeiro verifica `login status` e recusa sessão de API ou ausência de login;
não troca autenticação nem chama logout. Só depois aplica a restrição de método.
As chamadas consomem limites da assinatura e enviam o pacote ao serviço remoto;
usar somente dados sintéticos ou conteúdo explicitamente autorizado.

```powershell
uv sync --all-extras
codex login status
factory compare-understanding --corpus evals/understanding/v1 `
  --case dev-branding-conflict --ollama-model ahc-qwen3:4b-instruct-8k `
  --expected-model-sha256 59d7f50962ef280aacad2867d041c13e22ad2d08827df5ec407ff75d348f8c90 `
  --codex-model <modelo-disponivel-na-sua-conta> `
  --timeout-seconds 180 --output output/new-comparison
factory validate-understanding-comparison output/new-comparison `
  --corpus evals/understanding/v1
```

Exatamente um caso de development, duas chamadas e nenhuma repetição/reparação
automática. Cada adaptador impõe timeout; paralelismo máximo dois. O provedor
local usa o worker isolado com preflight e identidade observada. A chamada CLI
usa schema estrito, stream limitado, sandbox read-only e contexto temporário.
Não usa execução gerada, assets, shell, web, MCP do usuário ou delegação.
Qualquer evento de ferramenta invalida a geração; sandbox não é prova universal
de que nenhuma leitura externa seria possível em outra versão do cliente.

O diretório deve ser novo. Plano precede chamadas; worker local e relatório
final preservam falhas e não contêm raciocínio privado. A validação offline
confronta caso/corpus, input, programa, metadados e resultados. Hash comprova
correspondência de bytes; não autentica remotamente a execução ou o modelo.

`criterion_agreements` e `criterion_disagreements` comparam exatamente kind,
condition, outcome, question e uncertainties. Notas são excluídas. Parafrasear
uma regra pode gerar divergência textual sem divergência de significado.
`unavailable_criteria` conserva todos os critérios se uma chamada falhou.
Concordância não marca eval como aprovado. `semantic_status` e
`model_qualification` permanecem `not-established`, com revisão humana exigida.

O exit code de comparação indica apenas se as duas propostas passaram no contrato.
O validador pode retornar sucesso para um relatório consistente contendo falhas.
O [protocolo científico](understanding-scientific-basis.md) propõe orçamento
equivalente, ablações e adjudicação; o smoke não substitui esse experimento.
