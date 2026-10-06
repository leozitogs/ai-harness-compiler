# Produto generalista, harness específico

Direção explícita do PO em 2026-10-06: o compilador não atende uma lista fechada de
nichos. Ele estuda cada proposta, branding, backlog, fontes autorizadas e restrições
para construir entendimento e derivar o harness das regras daquele projeto.

```text
Proposta + Branding + Backlog + Restrições
→ Entendimento proposto e fontes
→ Domínio/hipóteses + regras de negócio + conflitos/incógnitas
→ Revisão e resolução de perguntas
→ Plano de harness
→ Packs opcionais por aplicabilidade
→ IR validada e compilação incremental
```

O domínio é resultado contextual do estudo, pode ser múltiplo ou permanecer incerto.
Projetos do mesmo domínio podem exigir harnesses diferentes. Branding informa
público, tom, posicionamento e restrições; não autoriza inventar regras de negócio.
Regra explicitamente confirmada prevalece sobre sugestão de template. Conflitos
entre fontes produzem perguntas/propostas, não decisões silenciosas.

ProjectUnderstandingSpec deve separar original, declaração, interpretação e
hipótese. Cada regra possui condição, resultado, exceções quando fornecidas,
origem, estado de revisão e responsável; dados ausentes são incógnitas. O modelo
propõe, contratos validam e revisão controla a adoção. Scores não são inventados.

HarnessBlueprintSpec traduz capacidades/regras em necessidades de contexto,
prompts/skills, ferramentas, workflows, documentação e avaliações. A baseline
existente pode ser compilada após revisão; componentes futuros ficam declarados
como gaps, sem alegar geração completa de runtime.

## Templates e frameworks extensíveis

PatternPackSpec é opcional, versionado, parametrizável e isolado do core. Define
aplicabilidade, evidências, exclusões, compatibilidade, dependências e conflitos.
Packs podem reunir padrões transacionais, editoriais, de integração ou domínio,
sem uma seleção fixa baseada somente no nome do nicho. Registro declarativo não
executa scripts/plugins externos por padrão.

Ausência de pack não impede estudar um novo projeto. O baseline generalista e
perguntas pendentes são caminhos válidos. Seleções explicam por que um pack se
aplica e quais regras foram adaptadas. Templates nunca sobrescrevem regras
específicas confirmadas nem copiam dados de outros projetos.

## Avaliação de generalização

Educação, comércio e dev-tools existentes são fixtures de teste, não nichos do
produto. Avaliar também inputs reservados de domínio não cadastrado, dois projetos
do mesmo domínio com regras diferentes, branding/backlog contraditórios, falta de
informação e execução sem pack. Não usar o holdout para escolher prompts/templates.
O fake verifica contratos; entendimento semântico exige demonstração com modelo
real configurado e revisão de qualidade, sem prometer generalização universal.

## Ordem incremental

Sprint 2 replanejada: AHC-019 (entendimento) → AHC-020 (blueprint e packs).
AHC-005 (prompts/skills) passa a depender de ambos. AHC-015/016/017/018 continuam
no roadmap para concretizar documentação/aprendizado e especialistas a partir
desse entendimento. AHC-009 mantém pesquisa externa e adapters completos futuros;
o adapter mínimo de entendimento não elimina seus critérios.
