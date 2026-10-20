# Regras, guards e proveniência por componente

```sh
factory analyze-project-v3 ./project-definition --output ./analysis-v3.json
factory verify-analysis-v4 ./analysis-v3.json --output ./advice-v4.json
```

Chamadas explicitamente dependentes do modelo principal Codex CLI, sem fallback.
Arquivos existentes não são sobrescritos. Sucesso do comando significa artefato
válido salvo, não sucesso semântico, autorização de compilar ou qualificação.

`EvidenceText` contém interpretação e `source_atom_ids`. Condição, resultado e cada
exceção possuem suas próprias referências. Um componente pode citar múltiplas
declarações quando sua composição for realmente necessária. A auditoria examina
cada componente apenas contra as respectivas citações; o input completo não serve
para justificar uma fonte selecionada incorretamente.

Guards declarados em outras fontes devem permanecer separados da permissão:
por exemplo, autorização do autor vem do critério, exigência de identidade/registro
vem das restrições. `target_scope: criteria` exige alvos reais; `project` exige lista
de alvos vazia e pode representar políticas que abrangem outras capacidades.
IDs de alvo indicam aplicabilidade, não são acrescentados como fontes de suporte.

O achado reúne as fontes dos componentes, mas preserva também seus vínculos
individuais e a posição de cada exceção. Pareceres ficam stale se uma fonte muda
de componente, mesmo que texto e união de citações não mudem. Campos desconhecidos,
fontes inelegíveis, colisões de IDs e vínculos inexistentes são rejeitados.

V4 adiciona `component_judgments`, com nome e índice para exceções. O inventário
deve corresponder exatamente aos componentes existentes. Um componente contradito
ou sem evidência suficiente impede supports do achado inteiro. O ledger mantém
todos os vínculos de fontes existentes e diagnostica omissões, como v3.

O host não resolve contradições ou reescreve componentes após a resposta. Guards
são especificações propostas, não controles operacionais implementados. Semântica
continua requerendo revisão; a avaliação humana/holdout permanece num gate posterior.
Os comandos antigos continuam disponíveis e não migram automaticamente para v3/v4.

## Revisão humana offline

`factory assess-analysis-v3 analysis.json --case case.json --rubric rubric.json
--output assessment.json` produz `not-run` sem revisão (ou `fail` se já houver
incompatibilidade objetiva). `--review human-review-v3.json` recebe apenas uma
declaração humana real. A revisão inclui seis critérios, cobertura de obrigações,
suporte por achado e por componente, com nome, índice de exceção e fontes exatas.
IDs, hashes ou fontes stale são rejeitados; um guard alterado exige nova revisão.
Pass requer inventários positivos completos, caso e rubrica aprovados. O comando
retorna 0 apenas para pass e recusa sobrescrever arquivos. Parecer v4 é consultivo
e não é convertido para declaração humana v3. A compilação continua não autorizada.

## Variante corretiva em desenvolvimento

`semantic-composition/v3.2` está disponível somente por seleção explícita de
`program_version` na API Python `analyze_composition`. Default e CLI continuam
v3.1. O candidato preserva obrigações sem gatilho como contexto normativo, sem
forçá-las a um guard com condição inventada, e distingue papéis não atribuídos
de uma lacuna bloqueante de negócio. Isso não implementa enforcement de regras.

`composition_program_digest(extraction, version)` vincula versão, prompt e schema
dinâmico. Input, provider, parâmetros e ambiente precisam de registro separado;
esse digest não certifica uma execução ou qualidade semântica. A versão antiga
permanece idêntica e versões desconhecidas são rejeitadas antes da chamada.
Ver [decisão e limites do candidato](../delivery/sprint-2-6-human-judgments.md).

`semantic-composition/v3.3` acrescenta uma rota explícita de perguntas secundárias
em `issues`, com inventário próprio de fontes. Seu schema proíbe `uncertainties`
locais e restringe os índices; o host também rejeita a rota antiga, sem reescrever
a resposta. Perguntas primárias locais continuam limitadas ao próprio critério.
As versões anteriores, seus fingerprints e o default são preservados.
Ver [implementação e protocolo de desenvolvimento](../delivery/sprint-2-6-multisource-candidate.md).
