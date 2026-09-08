# Poem CLI

A simple LangChain console app using Typer, Rich, and local Ollama `gemma2:9b`.

Requires Python 3.14+, uv, and Ollama running locally.

```bash
uv sync
ollama pull gemma2:9b
uv run main.py --request "Write a poem about the sea" --lines 4
uv run main.py --request "Explain this poem: Moonlight rests upon the sea."
```

The model routes your request to writing or explanation. For explanations,
include the poem in your request; previous runs are not remembered.

For writing, the app plans a poem, writes it, and counts nonempty lines. If it exceeds the
limit, it revises once and checks again. If it still exceeds the limit, it shows
a warning and the poem. The default limit is 5 lines and applies only to writing.
`--topic` still works as an alias for `--request`.

Prompt templates are in `prompts.py`; the workflow is in `main.py`.
