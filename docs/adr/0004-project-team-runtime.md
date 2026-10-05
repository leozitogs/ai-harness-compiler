# ADR-0004 — Runtime opcional de equipe antes da Sprint 1

Status: implementado sob solicitação do PO.

## Contexto

O PO solicitou agentes específicos e funcionais com personas, código, LangGraph
e ML antes de começar a Sprint 1. Isso acrescenta uma equipe de preparação para
o próprio projeto, sem transformar o modelo de domínio do compilador em LangGraph.

## Decisão

Criar contratos provider-independent de persona, decisões, relatórios, execução
e revisão. Implementar seis especialistas com allowlists de ferramentas e ciclos
limitados. Usar LangGraph para fan-out/fan-in, checkpoint SQLite e interrupt do PO.
Usar TF-IDF/LogisticRegression para intenção e TF-IDF para contexto, com avaliação
separada. Oferecer modo local e adapter de Ollama com decisões estruturadas.

Dependências ficam no extra `team`; comandos de compilação seguem sem SDKs de
agentes no domínio. O runtime não expõe escrita em código ou shell; a preparação
produz análises e planos verificáveis. Aprovação do relatório não inicia sprint.

## Consequências

É possível executar e verificar a equipe offline, preservar o estado de revisão
e testar os limites. A persona influencia prompts no modo LLM e define permissões
em ambos os modos. O classificador é experimental, com corpus curado pequeno;
não constitui evidência de generalização. Ollama depende de modelo local instalado.

Projetos futuros poderão ampliar ferramentas de implementação após definir
isolamento, política de execução, revisão de diffs e evidências de testes.
Não usar os especialistas atuais para alegar conclusão automática de histórias.
