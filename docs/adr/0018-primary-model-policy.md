# ADR-0018 — Principal único para tarefas com LLM

Status: aceito como preferência operacional de desenvolvimento em 2026-10-08.

## Decisão

Adotar `gpt-6.1-sol` por Codex CLI autenticado com ChatGPT como principal.
Todas as funções com LLM — entendimento, análise, arquitetura, engenharia,
qualidade, segurança e entrega — herdam a mesma política central empacotada.
Manter `ahc-qwen3:4b-instruct-8k` como alternativa local explicitamente solicitada.
Nunca trocar silenciosamente modelo/provedor após erro.

O PO pediu verificar o melhor resultado e definir o principal. A escolha prioriza
interpretação operacional e suporte de fontes, não apenas JSON válido. A comparação
existente aceitou 8/8 propostas locais e 7/8 remotas estruturalmente; inspeção das
propostas revelou erros locais em domínio, capacidades, fontes do conflito,
benefícios apresentados como resultados e dúvidas sem contradição demonstrada.
O Codex preservou melhor essas relações nos casos disponíveis. Há dúvidas
excessivas nos dois e nenhum modelo qualificado por adjudicação/holdout.

Nova execução isolada do caso adversarial com o principal completou o contrato;
a observação antiga permanece intacta e a causa de sua falha não foi reconstruída.
O smoke não prova correção universal, resistência geral a injection ou preferência
para tarefas que ainda não foram avaliadas. Ver [seleção](../delivery/ahc-023-primary-selection.md).

## Implementação

ModelPolicy/v1 registra principal, alternativa, escopo, evidências e limitações.
`factory model-policy` mostra o snapshot. `factory study` sem override usa o
principal e o protocolo compacto. Flags antigas `--model` sem `--provider`
mantêm Ollama; não enviar entradas de comandos antigos à nuvem implicitamente.
`--provider ollama` é escolha local explícita. Não ignorar token caps que o
adapter remoto não consegue impor.

`factory team run --engine primary` resolve a política antes do checkpoint.
Decisões dos seis especialistas usam Codex com ferramentas do CLI desativadas;
o runtime executa somente ferramentas locais registradas e permitidas por persona.
Mantém orçamento, três consultas obrigatórias, concurrency máxima dois, relatos
consultivos e revisão persistente do PO. Retomada usa o modelo do snapshot,
sem reconsultar a preferência ou executar o agente outra vez.

`build`, `plan`, testes e equipe determinística continuam offline. Nenhum caminho
de compilação determinística ganha chamadas ao modelo. Escolha operacional do
principal não aprova fatos, instala harness ou marca histórias Done.

## Compatibilidade e limites

Schema de equipe/relato acrescenta `codex-cli`; leitores antigos podem rejeitá-lo,
enquanto os atuais mantêm runs existentes. Novo uso de `study` sem modelo usa a
assinatura e envia o input ao provedor: CLI/help/README explicam o novo padrão.
Não alterar autenticação existente ou configuração global do aplicativo Codex.
O executável externo continua opcional; falhas não ativam alternativa local.
Oito casos sintéticos e observações adicionais não provam superioridade em todas
as tarefas. Os papéis herdam a preferência, não uma qualificação por especialidade.
