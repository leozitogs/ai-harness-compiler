# Operações Scrum autorizadas

O Nexo prepara propostas; uma pessoa opera esta CLI separada. Não há comando
arbitrário, autorização automática pelo LLM ou escrita em `team run`.

1. Recolher fontes recentes com `scrum observe` e gerar relatório com `scrum propose`.
2. Inspecionar a issue vinculada para obter revisão, hashes e etiquetas atuais:

   ```sh
   factory scrum operation inspect --repo owner/repo --issue 15 --github
   ```

   Salvar o JSON UTF-8 em `expected.json`. Nenhum corpo/título integral é persistido;
   apenas hashes, identidade e metadados necessários. Se a revisão divergir daquela
   capturada, recolher o snapshot e gerar novamente o relatório.

3. Preparar o diff local, com o ID exato da proposta e história:

   ```sh
   factory scrum operation prepare --report proposals.json --expected expected.json --proposal refine-1 --story story-id --label nexo:needs-refinement --journal operations.sqlite
   ```

   Conferir alvo, etiquetas antes/depois, hash completo e sequência do recibo. O
   journal inclui o plano completo. Etiquetas permitidas precisam existir no repo;
   esta ferramenta não oferece comando para criá-las.

4. Somente após decisão humana específica, registrar autorização para aquele hash:

   ```sh
   factory scrum operation authorize --journal operations.sqlite --operation HASH --expected-version 1 --expires-at ISO_UTC --comment "Autorizo somente o diff revisado"
   factory scrum operation apply --journal operations.sqlite --operation HASH --repository . --github
   ```

   `ISO_UTC` deve estar no futuro, no máximo uma hora após o instante da autorização.
   A CLI registra `human-product-owner` como declaração do operador; não autentica
   identidade. Não registrar credenciais, prompts privados ou raciocínio privado.

5. Consultar o recibo ou reconciliar sem nova escrita:

   ```sh
   factory scrum operation show --journal operations.sqlite --operation HASH
   factory scrum operation reconcile --journal operations.sqlite --operation HASH --github
   ```

`apply` exige autorização válida, fontes locais exatas e recentes, issue aberta e
revisão remota coincidente. Revalida fontes/autorização imediatamente antes do POST.
O adapter usa host github.com, chamadas fixas, stdout limitado a 256 KiB e timeout.
Existem checks antes e depois, sem garantia de CAS remoto. Mudança concorrente
posterior pode deixar resultado uncertain mesmo que a etiqueta tenha sido aplicada.

`uncertain` ou `attempted` nunca gera retry de escrita; exige reconcile somente
leitura. Se o efeito não for estabelecido, o alvo continua bloqueado. `observed`
significa estado desejado visto naquele instante, não causalidade exclusiva nem
garantia de que continuará assim. Repetir apply em observed devolve o recibo antigo.

Cancelar apenas antes do dispatch, informando a versão atual:

```sh
factory scrum operation cancel --journal operations.sqlite --operation HASH --expected-version 2
```

Cancelamento é terminal e não representa rollback. Usar **um mesmo journal por
repositório** entre workers. Outros arquivos/hosts não compartilham a reserva local.
CLI retorna 0 para preparação/ações concluídas, 2 para blocked/uncertain e 1 para
erros de contrato/operação; código 0 nunca estabelece aceite de entrega ou DoD.

Os contratos estão em `factory schema scrum-operation-plan`, `operation-authorization`,
`operation-receipt` e `remote-issue-state`. Ver [ADR-0025](../adr/0025-authorized-scrum-operation-journal.md).
