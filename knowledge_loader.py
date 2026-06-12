from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


SUPPORTED_SUFFIXES = {".md", ".yaml", ".yml"}
DEFAULT_LOAD_ORDER = [
    "agent-operating-rules.md",
    "business-context.md",
    "tableau-sources.yaml",
    "product-catalog.yaml",
    "monthly-report-template.md",
    "reminders.md",
]


@dataclass(frozen=True)
class KnowledgeDocument:
    name: str
    path: Path
    content: str


@dataclass(frozen=True)
class KnowledgeBase:
    directory: Path
    documents: List[KnowledgeDocument]

    @property
    def loaded(self) -> bool:
        return bool(self.documents)

    @property
    def file_names(self) -> List[str]:
        return [doc.name for doc in self.documents]

    def as_prompt_context(self, max_chars: int = 12000) -> str:
        parts = []
        remaining = max_chars
        for doc in self.documents:
            section = f"\n\n# FILE: {doc.name}\n{doc.content.strip()}"
            if remaining <= 0:
                break
            parts.append(section[:remaining])
            remaining -= len(parts[-1])
        return "\n".join(parts).strip()

    def lookup(self, keyword: str, max_matches: int = 5) -> List[Dict[str, str]]:
        if not keyword:
            return []
        needle = keyword.lower()
        matches: List[Dict[str, str]] = []
        for doc in self.documents:
            for line in doc.content.splitlines():
                if needle in line.lower():
                    matches.append({"file": doc.name, "line": line.strip()})
                    if len(matches) >= max_matches:
                        return matches
        return matches

    def status(self) -> Dict[str, object]:
        return {
            "loaded": self.loaded,
            "directory": str(self.directory),
            "files": self.file_names,
            "document_count": len(self.documents),
        }


def _ordered_paths(directory: Path, load_order: Iterable[str]) -> List[Path]:
    if not directory.exists():
        return []

    by_name = {
        path.name: path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    }

    ordered: List[Path] = []
    for name in load_order:
        path = by_name.pop(name, None)
        if path:
            ordered.append(path)

    ordered.extend(path for _, path in sorted(by_name.items()))
    return ordered


def load_knowledge_base(directory: Path) -> KnowledgeBase:
    documents = []
    for path in _ordered_paths(directory, DEFAULT_LOAD_ORDER):
        documents.append(
            KnowledgeDocument(
                name=path.name,
                path=path,
                content=path.read_text(encoding="utf-8"),
            )
        )
    return KnowledgeBase(directory=directory, documents=documents)
