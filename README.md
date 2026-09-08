# Poem CLI

A simple LangChain console app using Typer, Rich, and local Ollama `gemma2:9b`.

Requires Python 3.14+, uv, and Ollama running locally.

```bash
uv sync
ollama pull gemma2:9b
```

Write or explain a poem:

```bash
uv run main.py --request "Write a poem about the sea" --lines 4
uv run main.py --request "Explain this poem: Moonlight rests upon the sea."
uv run main.py --help
```

The model classifies your request as `write` or `explain`, and Python selects
the matching workflow. The selected route is shown in the terminal.

- **Write:** Plan → Write → Count nonempty lines → Revise once if needed → Check again.
  If the revised poem still exceeds the limit, display a warning and the poem.
- **Explain:** Explain the supplied poem's meaning, mood, and imagery.
  Include the poem in your request; previous runs are not remembered.

Rich displays loading spinners and panels for the plan, poem, or explanation.
If the router returns an unsupported response, the app asks you to rephrase and exits.

`--request` is required; `--topic` is an alias. `--lines` defaults to 5, must be
at least 1, and applies only to writing.

Prompt templates are in `prompts.py`; the workflow is in `main.py`.
