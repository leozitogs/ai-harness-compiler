# Incidente de teste — duração positiva não é garantida

Na CI Windows/Python 3.12, o teste de relatório contraditório com tempo total zero
não rejeitou a fixture. Isso era correto: os jobs fake rápidos também tinham
duração medida zero. A fixture não construía uma contradição naquele ambiente.

Causa: teste dependia de duração positiva observada no relógio real em vez de
definir dados contraditórios explícitos. Resolução: na fixture negativa, definir
um job com elapsed_seconds=1.0 e tempo total=0.0. Assim testa o invariante em todos
os ambientes, sem exigir sleep ou alterar o validador para rejeitar zero legítimo.

O runner e os artefatos reais não mudaram. Metadados medidos permanecem intactos;
não inferir erro de performance do modelo ou do supervisor a partir desta falha.
Referência: CI run 37694075894, Windows/Python 3.12, caso
test_contradictory_session_reports_are_rejected[time].
