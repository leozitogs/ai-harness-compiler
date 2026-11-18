# ADR-0039 — Plano de testes vinculado à revisão funcional

Os cenários funcionais descrevem o que precisa ser verificado. AHC-031 passa
a exportar um artefato para quem vai implementar esses testes. O comando
valida o relatório `FunctionalReadiness/v1` e exige que a revisão exata
produza estado `approved`.

O plano `FunctionalBusinessTestPlan/v1` registra o projeto, a mudança, a
revisão e os digests da mudança, da prontidão e do aceite. Catálogos
preservam as regras, os requisitos, os exemplos, as exceções de
cobertura e as perguntas com respostas registradas. Os cenários mantêm
seus vínculos por ID e conservam os locators como dados planejados.
As fontes aparecem por ID e pointer. Seus valores e a declaração de
aceite ficam no relatório de origem.

O verificador recompõe o plano e compara os bytes. Esse formato permite
uma conferência determinística sem criar uma segunda autoridade para editar
resultados esperados. Uma alteração passa pelo contrato funcional e
pelo aceite da versão correspondente antes de gerar outro plano.

O estado permanece `not-run`. O comando não procura testes no repositório
alvo e não converte locators em comandos. O relatório aprovado e o plano
devem permanecer disponíveis durante a implementação e a futura coleta de
evidências de execução.
