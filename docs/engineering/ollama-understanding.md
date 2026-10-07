# Estudo de projeto com Ollama

Instalar o extra `uv sync --extra understanding`. Com Ollama local ativo e um
modelo já instalado, executar:

```sh
factory study ./project-definition --model MODEL_NAME --output understanding.json
factory validate-understanding understanding.json
```

`MODEL_NAME` é escolhido explicitamente pelo operador. O comando não baixa modelos,
não abre assets nem consulta fontes externas. A proposta continua pendente de
revisão humana e não é aplicada ao DNA, grafo ou harness.

## Fronteiras

- Core recebe uma interface Python sem SDK de provider. Apenas o adapter importa HTTPX.
- Endpoint fixo `http://127.0.0.1:11434/api/chat`, sem redirects ou proxy de ambiente.
- Uma tentativa; timeout padrão 60 s (máximo 300 s), sem retries automáticos.
  HTTPX limita espera por operação de rede; deadline também é verificado entre
  blocos recebidos. Não é um watchdog capaz de interromper qualquer operação no
  instante exato do deadline.
- Snapshot UTF-8 até 256 KiB, envelope até 1 MiB, proposta até 256 KiB.
  Parâmetros programáticos podem aumentar os limites até tetos definidos no adapter.
- Geração até 4096 tokens (CLI aceita até 16384); temperatura zero, `think: false`,
  sem tools. Dados do projeto seguem na mensagem de usuário; política fica no system.
- Resposta completa obrigatória; truncamento declarado, tool calls, formato inválido
  ou violação do contrato interrompem execução. Erros do provider não expõem o corpo.
- Modelo só fornece proposta. Core valida referências contra o snapshot original,
  inclusive se uma implementação tentar modificar o request recebido.
- Arquivo existente é recusado antes da chamada e novamente por criação exclusiva.
  Falha do provider não cria saída; falha durante escrita pode deixar arquivo parcial.

Separar instruções e dados não elimina prompt injection. Não há ferramentas ou
autoridade de escrita no provider. Schema e citações não provam verdade, semântica
das regras, autenticidade de revisão ou qualidade de geração. A CLI informa o nome
solicitado; evidência completa de modelo/digest/ambiente pertence à execução de
verificação 019-08, ainda pendente.

Ollama pode suportar modelos remotos; para este fluxo usar somente modelos locais.
Não habilitar credenciais ou cloud na execução de demonstração.

## Verificação

`tests/test_ollama_understanding.py` usa MockTransport e fakes definidos somente
nos testes: payload/schema, limites, deadline, timeout, erros, redirects, truncamento,
tentativa de ferramenta, referências falsas, mutação do snapshot e saída exclusiva.
Esses testes não representam eval de modelo. Os testes normais não exigem Ollama.
