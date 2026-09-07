# Poem CLI

A simple LangChain console app using Typer, Rich, and local Ollama `gemma2:9b`.

Requires Python 3.14+, uv, and Ollama running locally.

```bash
uv sync
ollama pull gemma2:9b
uv run main.py --topic "the sea" --lines 4
```

The app plans a poem, writes it, and counts nonempty lines. If it exceeds the
limit, it revises once and checks again. If it still exceeds the limit, it shows
a warning and the poem. The default limit is 5 lines.

Prompt templates are in `prompts.py`; the workflow is in `main.py`.
