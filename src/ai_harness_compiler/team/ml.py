"""Small supervised intent router and a measured holdout; no pretrained model downloads."""

from importlib.metadata import version

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from ai_harness_compiler.models.team import Role

TRAIN: dict[Role, list[str]] = {
    "analyst": [
        "Refinar requisitos e critérios de aceitação do backlog",
        "Descobrir ambiguidades nas histórias e necessidades dos usuários",
        "Analisar requisito funcional concepção e escopo do produto",
        "Revisar histórias de usuário e critérios observáveis",
        "Requirements analysis acceptance criteria user stories",
        "Identificar lacunas de entrada branding e restrições",
    ],
    "architect": [
        "Revisar arquitetura contratos schemas e fronteiras de módulos",
        "Planejar escalabilidade compatibilidade e evolução da IR",
        "Decidir arquitetura monólito modular ou microsserviços",
        "Modelar Pydantic ProjectDNA e HarnessSpec com versionamento",
        "Architecture design interfaces schema compatibility",
        "Registrar ADR e trade-offs de persistência e adapters",
    ],
    "engineer": [
        "Quebrar implementação em tarefas com dependências",
        "Criar plano técnico com arquivos e etapas de código",
        "Implementar feature em Python com funções e classes",
        "Preparar alterações do código e sequência de desenvolvimento",
        "Implementation coding task decomposition technical changes",
        "Dividir uma história em design implementação verificação revisão",
    ],
    "quality": [
        "Revisar testes pytest regressão cobertura e avaliação",
        "Construir matriz de qualidade e evidências dos critérios",
        "Validar casos negativos e resultados de testes",
        "Analisar falhas do benchmark e evals sem sucesso inventado",
        "Testing quality assurance regression evaluation evidence",
        "Preparar plano de testes unitários integração e ponta a ponta",
    ],
    "security": [
        "Auditar segurança permissões segredos e prompt injection",
        "Verificar ameaças dados privados e isolamento de projetos",
        "Revisar autorização e riscos das ferramentas com efeitos externos",
        "Proteger contra vazamento de dados e execução sem aprovação",
        "Security threat model permissions privacy secrets",
        "Avaliar risco de input não confiável e abuso de orçamento",
    ],
    "delivery": [
        "Preparar Sprint 1 kickoff Scrum objetivo capacidade e impedimentos",
        "Consolidar entrega prioridades pendências para Product Owner",
        "Organizar planning daily review retrospectiva e Sprint Goal",
        "Coordenar sprint backlog e fluxo de entrega",
        "Scrum delivery sprint planning product owner coordination",
        "Acompanhar impedimentos WIP e revisão com o PO",
    ],
}
HOLDOUT: dict[Role, list[str]] = {
    "analyst": [
        "Inspecione requisitos ambíguos e critérios das histórias",
        "Review user needs and acceptance criteria",
    ],
    "architect": [
        "Avalie fronteiras arquiteturais e compatibilidade dos schemas",
        "Design modular architecture and interfaces",
    ],
    "engineer": [
        "Decomponha implementação em tarefas e arquivos de código",
        "Plan coding steps and implementation dependencies",
    ],
    "quality": [
        "Confira testes de regressão e evidências dos evals",
        "Prepare quality assurance testing matrix",
    ],
    "security": [
        "Examine ameaças de vazamento de segredos e permissões",
        "Review security risks and private data protection",
    ],
    "delivery": [
        "Organize kickoff e planejamento Scrum da sprint",
        "Coordinate delivery impediments and sprint goal",
    ],
}


class IntentRouter:
    def __init__(self) -> None:
        self.roles = list(TRAIN)
        texts = [text for samples in TRAIN.values() for text in samples]
        labels = [role for role, samples in TRAIN.items() for _ in samples]
        self.model = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
                ("classifier", LogisticRegression(C=8.0, max_iter=500, random_state=42)),
            ]
        )
        self.model.fit(texts, labels)

    def route(self, text: str, threshold: float = 0.40) -> dict[str, object]:
        probabilities = self.model.predict_proba([text])[0]
        scores = {
            str(role): float(score)
            for role, score in zip(self.model.classes_, probabilities, strict=True)
        }
        predicted = max(scores, key=lambda role: scores[role])
        no_features = self.model.named_steps["tfidf"].transform([text]).nnz == 0
        abstained = no_features or scores[predicted] < threshold
        return {
            "selected_role": "delivery" if abstained else predicted,
            "predicted_role": predicted,
            "scores_uncalibrated": scores,
            "abstained": bool(abstained),
            "threshold": threshold,
            "fallback": "delivery",
        }

    def evaluate(self) -> dict[str, object]:
        details: list[dict[str, object]] = []
        for expected, samples in HOLDOUT.items():
            for text in samples:
                predicted = str(self.model.predict([text])[0])
                details.append({"request": text, "expected": expected, "predicted": predicted})
        correct = sum(item["expected"] == item["predicted"] for item in details)
        return {
            "model": "TF-IDF word ngrams + LogisticRegression",
            "sklearn_version": version("scikit-learn"),
            "train_samples": sum(len(samples) for samples in TRAIN.values()),
            "holdout_samples": len(details),
            "accuracy": correct / len(details),
            "details": details,
            "limitations": (
                "Small curated bilingual holdout; not a production generalization claim. "
                "Scores are uncalibrated."
            ),
        }
