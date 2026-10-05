# ADR-0001 — Core de compilador e contratos antes de agentes

Status: aceito para o scaffold inicial.

## Contexto

O produto gera sistemas de engenharia de IA para outros projetos. Gerar arquivos
diretamente de texto livre esconderia decisões, evidências e erros de interpretação.

## Decisão

Usar Python 3.12+, Pydantic e JSON Schema, com a sequência ProjectInput → ProjectDNA
→ CapabilityGraph → HarnessSpec → validação → compilação. Transformações são puras;
I/O fica nas fronteiras. A primeira arquitetura é uma baseline de desenvolvimento
sem agentes executáveis. Adapters futuros não controlam o modelo de domínio.

## Consequências

É possível testar compilação sem custos de modelos e revisar a IR antes de gerar.
Não há inteligência semântica, seleção de arquitetura ou automação de runtime nesta fase.
Será necessário evoluir a IR antes de implementar síntese de prompts, skills e agents.

## Alternativas

Geração direta por LLM foi descartada por falta de contratos intermediários.
Um framework agêntico como core foi adiado para preservar independência e testabilidade.
