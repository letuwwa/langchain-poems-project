from functools import lru_cache
from hashlib import sha256
from math import isfinite
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

DB_PATH = Path(__file__).resolve().parent / "data" / "chroma"


@lru_cache(maxsize=1)
def get_store() -> Chroma:
    return Chroma(
        collection_name="poems",
        embedding_function=OllamaEmbeddings(model="embeddinggemma"),
        persist_directory=str(DB_PATH),
    )


def save_poem(text: str, metadata: dict) -> tuple[str, bool]:
    text = text.strip()
    if not text:
        raise ValueError("Cannot save an empty poem.")

    poem_id = sha256(text.encode("utf-8")).hexdigest()
    store = get_store()

    if store.get(ids=[poem_id])["ids"]:
        return poem_id, False

    store.add_documents(
        documents=[Document(page_content=text, metadata=metadata)],
        ids=[poem_id],
    )
    return poem_id, True


def search_poems_with_scores(
    query: str, limit: int = 3, max_distance: float | None = None
) -> list[tuple[Document, float]]:
    """Return nearest poems within an optional distance cutoff (lower is closer)."""
    if not query.strip():
        raise ValueError("Search query must not be blank.")
    if limit < 1:
        raise ValueError("limit must be at least 1.")
    if max_distance is not None and (not isfinite(max_distance) or max_distance < 0):
        raise ValueError("max_distance must be finite and nonnegative.")

    results = get_store().similarity_search_with_score(query, k=limit)
    return [
        (document, distance)
        for document, distance in results
        if max_distance is None or distance <= max_distance
    ]


def search_poems(
    query: str, limit: int = 3, max_distance: float | None = None
) -> list[Document]:
    return [
        document for document, _ in search_poems_with_scores(query, limit, max_distance)
    ]
