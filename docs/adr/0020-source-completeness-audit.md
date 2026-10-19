# ADR-0020 — Auditoria de fontes e omissões na emenda 2.5

Status: aceito para desenvolvimento em 2026-10-13. Refs: AHC-022, INC-0015.

## Decisão

Adicionar `SemanticVerifierProposal/v3` e `SemanticVerifierReport/v3`, preservando
contratos, prompts e relatórios do verificador v2. A auditoria recebe somente a
análise e suas fontes reais; nenhuma expectativa de benchmark é enviada ao modelo.
Além do suporte aos achados existentes, ela registra omissões de regras, perguntas
materiais e conflitos, com fontes e justificativas.

Cada átomo conhecido recebe uma linha de cobertura com hash literal: representado,
com omissão, não aplicável ou instrução não confiável. Uma fonte pode sustentar um
achado válido e uma omissão ao mesmo tempo. O host exige inventário completo,
referências válidas e hashes exatos; classificação e completude semântica continuam
dependentes de revisão. O ledger preenchido não demonstra entendimento correto.

O resultado continua `model-advisory`, `not-established` e `not-authorized`.
Não modifica a análise, não insere perguntas automaticamente nem concede aprovação.
Revisões e análises v2 anteriores continuam deserializáveis. Usar o comando novo
`verify-analysis-v3` torna explícita a mudança de protocolo; v2 continua disponível.

Na geração, o programa `semantic-analysis/v2.2` explicita duas regras gerais:
ignorar comandos que tentam controlar o modelo dentro dos dados sem descartar
intenção legítima; e perguntar sobre decisões materiais não definidas, conservando
as partes determináveis. Falta de detalhe técnico não bloqueia. Recusa fundamentada
continua disponível quando a própria solicitação legítima não pode ser interpretada
com segurança; timeout e erro de contrato nunca são recusa segura.

## Motivo e alternativas

O verificador v2 apoiou os achados de uma análise que omitira pergunta material.
Seu contrato não tinha canal de omissões. Apenas endurecer o prompt manteria essa
lacuna de representação; reparar a análise no host ocultaria a falha original.
O PO autorizou corrigir as pendências como emenda da Sprint 2.5, mantendo os gates
de qualidade existentes, sem encerrar histórias ou aprovar automaticamente casos.

As instruções distinguem regras do programa e conteúdo de referência. A separação
e avaliação por workload seguem a orientação de [prompt engineering da OpenAI](https://developers.openai.com/api/docs/guides/prompt-engineering).
Essa orientação fundamenta o processo; não certifica este compilador ou os resultados.

## Limites

É uma segunda chamada do mesmo modelo, não verificação científica independente.
Inventário estruturalmente completo pode conter julgamentos errados. O fingerprint
do verificador é lógico, não identidade autenticada da execução. Testes sem modelo
validam vínculos e permissões; desenvolvimento serve para depuração, não qualificação.
Congelamento do corpus, holdout e aceitação humana continuam pendentes.
