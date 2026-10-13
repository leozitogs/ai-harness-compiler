# DE-0008 — Resolução da rastreabilidade operacional

Data: 2026-10-13. Decisão tomada pelo colaborador sob delegação explícita do PO:
“cria a ideia de resolução, estuda ela, planeja e verifica as possibilidades de erro
e acerto, com base nisso, decida.” Não é revisão humana de respostas ou qualificação.

## Fatos e dúvida

Na entrada `dev-rules-b`, o critério autoriza o autor a liberar publicação sem
aprovação de terceiros. A restrição exige registrar a identidade do responsável.
O backlog inclui organizar publicações e registrar decisões. A fonte não define
onde associar identidade nem equipara autor, executor, proprietário e aprovador.

O modelo conservou a autorização, mas bloqueou perguntando se a identificação
se aplicava à publicação, às decisões ou a ambas. A pergunta tem origem na entrada;
não é um conflito provado. A decisão abaixo acrescenta uma política específica
de engenharia, identificada como tal, em vez de alegar que a fonte já a determinava.

## Decisão

Cobrir **cada liberação e cada decisão persistida** com rastreabilidade operacional.
Para essa política, responsável operacional é a identidade autenticada do executor
do evento. Isso não define propriedade do conteúdo, responsabilidade de negócio ou
poder de aprovação. Papéis adicionais só entram quando declarados pelo projeto,
com vínculos próprios; não inferir que autor, proprietário e executor são iguais.

Essa definição resolve a dúvida de alcance para a proposta derivada. Preservar
autorização do autor sem terceiros. Esquema, armazenamento e formato do registro
podem ser definidos no blueprint. A identificação exigida não é uma aprovação.
Identidade válida também não concede autorização: um administrador ou serviço
autenticado não recebe o direito do autor por esse motivo. Em delegação validada,
registrar executor e representação separadamente, sem inferir vínculo inexistente.

Na futura execução, impedir a ação coberta quando a identidade não puder ser
verificada ou o registro obrigatório não puder ser garantido. Escolher mecanismo
de autenticação, transação/outbox e recuperação faz parte da implementação posterior;
nenhum desses mecanismos está implementado por esta decisão.

É uma política desta entrada, não regra universal do compilador. Se outra entrada
trouxer escopo, anonimato permitido, atores ou obrigações diferentes, suas regras
prevalecem e precisam de nova análise. Não usar resolução externa silenciosamente
para mudar a classificação da entrada original: criar input derivado com proveniência.

## Alternativas examinadas

| Opção | Benefício | Erro possível | Escolha |
|---|---|---|---|
| Bloquear todo entendimento | Evita escolher alcance sem decisão | Paralisa regra já clara e mistura desenho futuro com autorização | Descartada após esta decisão explícita; antes dela a dúvida era legítima |
| Só publicação | Menor volume de eventos | Decisões persistidas podem perder autoria | Descartada neste projeto |
| Só decisões | Dá histórico de decisões | Liberação pode perder associação ao executor | Descartada neste projeto |
| Ambos, com papéis separados | Cobre as duas capacidades sem terceiro aprovador | Volume, retenção e falha de gravação exigem desenho | Selecionada |
| Responsável = autor/proprietário em todos os casos | Simplifica campos | Atribuição incorreta quando outro ator executa ou há delegação | Descartada |

## Fundamentação e limites

PROV-O separa atividade, agente e papel na associação; essa distinção permite
representar funções sem presumir que toda participação tenha a mesma responsabilidade.
[W3C PROV-O](https://www.w3.org/TR/prov-o/#qualifiedAssociation).
OWASP recomenda registros contextualizados por evento, com identidade quando conhecida,
ação e objeto; também trata exclusão de dados sensíveis e proteção dos logs.
[OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).

A cobertura das duas capacidades e a definição de responsável operacional são
**escolhas nossas**, não determinações desses documentos. Eles não certificam a
decisão nem fornecem regras de negócio do projeto. Identificadores também podem
ser sensíveis; não registrar credenciais, prompts privados ou conteúdo integral
por padrão. Definir acesso e retenção no blueprint antes de ativar a política.

## Cenários de acerto e erro

| Cenário | Resultado correto | Erro a prevenir |
|---|---|---|
| Autor identificado libera publicação | Autorizar conforme regra e registrar executor/evento | Exigir terceiro aprovador |
| Usuário registra decisão persistida | Registrar executor e alvo da decisão | Evento sem vínculo de identidade |
| Executor diferente de responsável de negócio declarado | Conservar ambos os papéis separadamente | Substituir um pelo outro |
| Serviço executa em nome do autor | Registrar serviço e delegação validada; verificar autorização própria | Chamar o serviço de autor ou conceder autorização pela identidade |
| Identidade exigida ausente ou não verificável | Impedir a ação coberta, sem inventar identidade | Publicar e completar identidade posteriormente |
| Registro obrigatório falha | Não declarar sucesso até garantia de persistência definida | Evento perdido ou duplicado em retry |
| Publicação já emitida em retry | Deduplicar por identificador de evento/operação | Duplicar publicação ou atribuir outro autor |
| Leitura, rascunho volátil ou detalhe de tabela | Não ampliar automaticamente escopo da política | Registrar tudo ou bloquear entendimento |
| Outra entrada permite anonimato ou define escopo contrário | Aplicar regra dessa entrada e estudar conflito real | Impor esta política como template universal |

## Plano executável de desenvolvimento

1. Registrar DE-0008 e criar candidato derivado que mantém as declarações originais
   e acrescenta a resolução explicitamente; manter o corpus e resultados anteriores.
2. Verificar manifesto/grounding e comparar input derivado com o original: só ID,
   nome e restrições da resolução podem mudar.
3. Executar análise e auditoria v3 no candidato público, verificando autorização,
   cobertura e ausência de pergunta de alcance; sem expectativa enviada ao auditor.
4. Levar a política ao futuro blueprint: envelope mínimo (evento, ação, alvo,
   executor, instante, resultado, versão da política), idempotência, persistência,
   acesso e retenção. Vínculos de papéis de negócio apenas quando declarados.
5. Antes de executar ações reais, testar identidade ausente, escrita indisponível,
   retry e distinção de papéis. Estes testes operacionais são requisitos futuros,
   não testes já executados. Aprovação semântica e holdout continuam separados.

## Verificação realizada

O candidato derivado foi validado pelos contratos existentes, e a comparação do
input confirmou mudanças apenas no ID/nome e nas restrições explícitas da decisão.
O caso B original, suas expectativas e resultados permaneceram intactos.
Duas chamadas reais de desenvolvimento produziram análise ready e auditoria v3
válida, com nove julgamentos supports e nenhuma omissão proposta. A avaliação
continua not-run: não existe aprovação das expectativas ou revisão humana.

A recuperação demonstra que explicitar uma decisão resolve a pergunta nesse
ensaio, não que o modelo compreendeu perfeitamente todas as implicações. O plano
operacional acima foi analisado por cenários e revisão independente; não há serviço
de auditoria, transação ou execução de publicação implementado nesta entrega.

Há ainda um limite de evidência a tratar antes de qualificar o candidato: a regra
gerada combinou a autorização original com os novos guards de identidade/registro,
mas seu binding de critério aponta apenas para a fonte da autorização. Os guards
existem nas restrições do input derivado; a conclusão composta precisa citar ambos
os conjuntos. O parecer supports do modelo não elimina essa lacuna de proveniência.
O blueprint deve conservar regras/guards separados ou fornecer binding composto
validado. Não alterar a política ou o caso original para ocultar esse resultado.
