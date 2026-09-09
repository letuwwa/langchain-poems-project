from datetime import datetime, timezone
from pathlib import Path

from storage import save_poem


def ingest_file(path: Path) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8-sig")

    return save_poem(
        text,
        metadata={
            "source_type": "imported",
            "source": str(path.resolve()),
            "title": path.stem,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
