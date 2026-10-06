"""Read-only, bounded, whitelisted repository context with TF-IDF retrieval."""

import hashlib
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ai_harness_compiler.memory.store import MemoryStore

SOURCES = (
    "README.md",
    "project-definition/project.yaml",
    "planning/sprint-1.json",
    "SECURITY.md",
    "pyproject.toml",
    "docs/architecture.md",
    "docs/contracts.md",
    "docs/engineering/standards.md",
    "docs/engineering/workflow.md",
    "docs/delivery/sprint-1.md",
    "docs/product/backlog.md",
    "docs/product/conception.md",
    ".github/workflows/ci.yml",
    "src/ai_harness_compiler/intake.py",
    "src/ai_harness_compiler/compiler.py",
    "src/ai_harness_compiler/pipeline.py",
    "src/ai_harness_compiler/planning.py",
    "src/ai_harness_compiler/models/base.py",
    "src/ai_harness_compiler/models/project.py",
    "src/ai_harness_compiler/models/harness.py",
    "tests/test_pipeline.py",
    "tests/test_cli.py",
    "tests/test_compiler.py",
    "tests/test_planning.py",
)


class RepositoryContext:
    def __init__(self, root: Path, project_id: str = "ai-harness-compiler") -> None:
        self.root = root.resolve()
        self.project_id = project_id
        self.documents: dict[str, str] = {}
        self.chunks: list[dict[str, str]] = []
        for source in SOURCES:
            path = (self.root / source).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError(f"Context source escapes repository: {source}")
            if not path.is_file():
                continue
            if path.stat().st_size > 128 * 1024:
                raise ValueError(f"Context source exceeds 128 KiB: {source}")
            content = path.read_text(encoding="utf-8")
            self.documents[source] = content
            for offset in range(0, len(content), 2000):
                self.chunks.append({"source": source, "text": content[offset : offset + 2000]})
        self.vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(
            [chunk["text"] for chunk in self.chunks] or ["no repository context available"]
        )

    def retrieve(self, query: str) -> list[dict[str, object]]:
        if not self.chunks:
            return []
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        ranked = sorted(range(len(scores)), key=lambda index: float(scores[index]), reverse=True)
        return [
            {**self.chunks[index], "relevance": float(scores[index])}
            for index in ranked[:3]
            if float(scores[index]) > 0
        ]

    def digests(self) -> dict[str, str]:
        memory = MemoryStore(self.root, self.project_id)
        return {
            **{
                source: hashlib.sha256(body.encode("utf-8")).hexdigest()
                for source, body in self.documents.items()
            },
            **memory.digests(),
        }
