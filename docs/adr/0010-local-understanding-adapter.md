# ADR-0010 — Modelo substituível e estudo local explícito

Status: aceito para o incremento estrutural da AHC-019.

## Contexto

Os contratos da ADR-0009 já separam snapshot, proposta e revisão. Precisamos de uma
implementação real sem acoplar o domínio ao runtime interno de agentes e sem tornar
a suíte dependente de rede ou de um modelo instalado.

## Decisão

`UnderstandingModel.propose` retorna somente `UnderstandingProposal`. `study_project`
preserva uma cópia independente do snapshot e revalida todas as referências no core.
O adapter opcional Ollama usa uma chamada explícita à API local, JSON Schema e
limites de bytes, tokens e timeout. Não oferece ferramentas, retries ou aprovação.
A CLI persiste exclusivamente uma proposta sem revisão em arquivo novo.

## Alternativas

- Reutilizar o loop de agentes internos: adicionaria ferramentas e objetivos que
  não pertencem ao estudo de um projeto alvo.
- Importar SDK no domínio: acoplaria os contratos a um provider.
- Usar fake no produto: confundiria execução estrutural com entendimento por LLM.

## Consequências e limites

HTTPX fica no extra `understanding`; core e preparação permanecem offline.
Transporte simulado verifica invariantes e erros; não prova qualidade semântica.
Prompt inicial geral não foi otimizado com holdout. Rubrica/casos reservados,
execução real identificada, revisão semântica e propagação revisada para DNA/grafo
continuam como entregas posteriores. Não altera versões dos contratos/IR existentes.

Referências: [contratos](../engineering/project-understanding.md),
[operação](../engineering/ollama-understanding.md) e
[API oficial](https://docs.ollama.com/api/chat).
