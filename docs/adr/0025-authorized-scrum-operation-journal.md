# ADR-0025 — Operador aditivo com journal de intenção

Status: aceito para implementação em 2026-10-19; AHC-029.

## Decisão e fundamento

O operador é uma fronteira explícita de I/O, separada do compilador e das ferramentas
do Nexo. `ScrumOperationPlan/v1` vincula relatório validado, proposta, história,
issue observada, revisão esperada e etiqueta. Autorização humana por hash exato,
prazo de até uma hora e versão local esperada é distinta da aprovação do relatório.
Nenhum modelo recebe a ferramenta de autorização ou escrita.

A primeira allowlist admite somente adicionar uma etiqueta existente:
`nexo:needs-refinement`, `nexo:needs-capacity` ou `nexo:needs-evidence`, de acordo
com a proposta. Não permite mudar status, ordenar backlog, fechar issue, alterar
marcos ou substituir listas. Essas operações exigiriam contratos e evidências
adicionais, não uma interpretação livre de texto do agente.

O GitHub [não garante conditional requests para métodos de escrita](https://docs.github.com/rest/guides/best-practices-for-integrators).
Por isso usamos o endpoint [aditivo de etiquetas](https://docs.github.com/en/rest/issues/labels#add-labels-to-an-issue),
com conferência antes/depois, sem prometer compare-and-swap remoto. Mudanças vistas
antes da chamada bloqueiam; concorrência detectada depois deixa resultado incerto,
preservando os outros campos e etiquetas. A checagem de existência da etiqueta
também não é transação remota: exclusão/renomeação concorrente continua uma limitação.

## Persistência e estados

SQLite mantém projeção e recibos na mesma transação `BEGIN IMMEDIATE`, com
`synchronous=FULL`. Recibos encadeados por hash não são atualizados ou apagados pelo
aplicativo. Carregamento verifica contrato, sequência, transições, alvo, resultado
observado e correspondência da projeção. Chave idempotente é o hash do plano inteiro.

`prepared → authorized → attempted → observed | uncertain`; bloqueio antes do
dispatch produz `blocked`. Cancelamento só ocorre em prepared/authorized. Tentativa
é persistida antes da chamada externa; crash deixa attempted, sem repetir escrita.
Reconciliar faz somente leitura: comprovar o estado desejado produz observed; caso
contrário mantém uncertain. Replay observado devolve o mesmo recibo histórico,
sem reimpor etiquetas removidas posteriormente.

Versão esperada impede disputa entre autorização/cancelamento/dispatch. Índice
único reserva alvo enquanto attempted/uncertain, inclusive contra outra operação
no mesmo journal. Não há lock de banco durante chamadas de rede. Uma operação faz
até quatro requests de dez segundos cada (issue, etiqueta, POST, issue); reconciliação
faz uma leitura. Tempo total inclui I/O local e inicialização, sem promessa de SLA.

## Limitações explícitas

Um journal compartilhado por repositório é necessário; arquivos/hosts independentes
não coordenam entre si. Hashes e triggers não autenticam um proprietário com acesso
de escrita ao banco. A CLI é uma fronteira de operador confiável: o campo actor
registra uma declaração humana, sem implementar login, assinatura ou RBAC.

Não há exactly-once externo, rollback remoto ou repetição após timeout. Quando o
efeito não pode ser estabelecido, o alvo permanece bloqueado; resolução administrativa
auditada e coordenação distribuída ficam para uma evolução explícita. Cancelar uma
ação já despachada não pode ser tratado como desfazer seu efeito.

A demo fake prova a lógica local; leitura GitHub real prova apenas esse caminho.
Não houve escrita real autorizada nesta entrega, aceite de critérios, cerimônia,
início/conclusão automática de sprint ou qualificação de modelo.
