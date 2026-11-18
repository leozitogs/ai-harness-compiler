# ADR-0038 — Rascunho funcional a partir de uma avaliação semântica revisada

AHC-031 precisa ligar o entendimento do projeto à especificação funcional.
A etapa offline recebe um `SemanticAssessment/v4` com resultado `pass` e
um digest esperado do assessment completo. O contrato existente revalida
análise, caso, rubrica e declaração humana, incluindo seus vínculos.
O operador escolhe intenção, capacidades e regras, e vincula cada pergunta
a um responsável e às regras pertinentes.

A transformação usa as referências literais dos átomos e mantém condição,
resultado, exceções e, quando houver, escopo da regra. As regras entram
como hipóteses. A projeção conserva as perguntas na íntegra e exige que
um conflito tenha uma pergunta de precedência que cite todos os lados.
Se a fonte de uma regra ou pergunta também sustenta um fragmento rejeitado,
o operador precisa resolver essa sobreposição antes de importar o achado.
O manifesto original permanece como entrada não confiável.

Esta etapa usa o contrato funcional e o arquivo das fatias anteriores.
A saída recebe um recibo de digests para permitir repetir a projeção com
o mesmo assessment e os mesmos parâmetros. O arquivo funcional armazena
o rascunho. O operador guarda o assessment e o recibo junto à evidência
da mudança, em armazenamento privado quando necessário.

O escopo selecionado continua sujeito à revisão funcional, incluindo a
aplicabilidade das normas e requisitos preservados no assessment original.
A ativação no pipeline padrão depende dos gates de AHC-019, AHC-021 e
AHC-022. O passo atual é uma projeção local para revisão e arquivamento.
