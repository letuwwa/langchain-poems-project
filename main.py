from datetime import datetime, timezone
from math import isfinite
from pathlib import Path

import typer
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ingestion import ingest_file
from prompts import (
    explanation_prompt,
    planning_prompt,
    revision_prompt,
    router_prompt,
    writing_prompt,
)
from storage import save_poem, search_poems_with_scores

app = typer.Typer()


def validate_poem(poem: str, limit: int) -> bool:
    return 0 < sum(1 for line in poem.splitlines() if line.strip()) <= limit


def validate_distance(value: float | None) -> float | None:
    if value is not None and (not isfinite(value) or value < 0):
        raise typer.BadParameter("Distance must be finite and nonnegative.")
    return value


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    request: str | None = typer.Option(
        None,
        "--request",
        "--topic",
        help="Ask to write or explain a poem.",
    ),
    lines: int = typer.Option(5, min=1, help="Maximum amount of lines."),
    save: bool = typer.Option(False, "--save", help="Save the final generated poem."),
    rag: bool = typer.Option(
        False, "--rag", help="Use stored poems as writing references."
    ),
    reference_limit: int = typer.Option(
        3, min=1, help="Maximum number of RAG references."
    ),
    max_distance: float | None = typer.Option(
        None,
        min=0,
        callback=validate_distance,
        help="RAG reference distance cutoff; no cutoff by default.",
    ),
):
    if ctx.invoked_subcommand is not None:
        return

    if not request or not request.strip():
        raise typer.BadParameter("Provide --request, or use an ingest/search command.")

    model = ChatOllama(model="gemma2:9b")
    router_chain = (
        router_prompt | ChatOllama(model="gemma2:9b", temperature=0) | StrOutputParser()
    )

    console = Console()
    with console.status("Choosing a route...", spinner="dots"):
        route = router_chain.invoke({"request": request}).strip().lower()

    if route not in {"write", "explain"}:
        console.print(
            "[red]Could not choose a route. Please rephrase your request.[/red]"
        )
        raise typer.Exit(code=1)

    console.print(f"[dim]Route: {route}[/dim]")
    if route == "explain":
        if save or rag:
            console.print("[dim]--save and --rag apply only to writing poems.[/dim]")
        explanation_chain = explanation_prompt | model | StrOutputParser()
        with console.status("Explaining your poem...", spinner="dots"):
            explanation = explanation_chain.invoke({"request": request})
        console.print(
            Align.center(
                Panel.fit(
                    Text(explanation.strip()), title="Explanation", border_style="cyan"
                )
            )
        )
        return

    topic = request
    context = ""
    if rag:
        with console.status("Finding reference poems..."):
            references = search_poems_with_scores(
                request, reference_limit, max_distance
            )
        if not references:
            console.print("No matching references found. Writing without references.")
        for index, (document, distance) in enumerate(references, start=1):
            title = document.metadata.get("title", "Untitled poem")
            source = document.metadata.get("source", document.id or "generated")
            console.print(
                Text(f"Reference {index}: {title} ({source}), distance {distance:.4f}")
            )
            context += f"Reference {index}:\n{document.page_content}\n\n"

    planning_chain = planning_prompt | model | StrOutputParser()
    writing_chain = writing_prompt | model | StrOutputParser()
    revision_chain = revision_prompt | model | StrOutputParser()

    with console.status("Planning your poem...", spinner="dots"):
        plan = planning_chain.invoke({"topic": topic, "context": context})

    console.print(
        Align.center(
            Panel.fit(Text(plan.strip()), title="Plan", border_style="yellow")
        ),
    )

    with console.status("Writing your poem...", spinner="dots"):
        poem = writing_chain.invoke(
            {"topic": topic, "lines": lines, "plan": plan, "context": context}
        )

    if not poem.strip():
        console.print("[red]The model returned an empty poem. Please try again.[/red]")
        raise typer.Exit(code=1)

    if not validate_poem(poem, lines):
        with console.status("Shortening your poem...", spinner="dots"):
            poem = revision_chain.invoke({"poem": poem, "lines": lines})

        if not poem.strip():
            console.print(
                "[red]The model returned an empty revision. Please try again.[/red]"
            )
            raise typer.Exit(code=1)

        if not validate_poem(poem, lines):
            console.print(
                "[yellow]The revised poem still exceeds the line limit.[/yellow]"
            )

    console.print(
        Align.center(
            Panel.fit(
                Text(poem.strip()), title=Text(topic.capitalize()), border_style="cyan"
            )
        ),
    )

    if save:
        try:
            with console.status("Saving poem..."):
                poem_id, created = save_poem(
                    poem,
                    metadata={
                        "source_type": "generated",
                        "title": request,
                        "request": request,
                        "model": "gemma2:9b",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "line_limit": lines,
                        "within_line_limit": validate_poem(poem, lines),
                        "rag": rag,
                    },
                )
        except Exception as exc:
            console.print(Text(f"Poem displayed above, but saving failed: {exc}"))
            raise typer.Exit(code=1) from exc
        console.print(f"{'Saved' if created else 'Already saved'}: {poem_id}")


@app.command()
def ingest(
    path: Path = typer.Argument(..., exists=True, readable=True),
):
    """Import one TXT file or all TXT files under a folder."""
    console = Console()

    files = (
        sorted(
            file
            for file in path.rglob("*")
            if file.is_file() and file.suffix.lower() == ".txt"
        )
        if path.is_dir()
        else [path]
    )

    if not files:
        console.print("No TXT files found.")
        return

    added = skipped = failed = 0

    for file in files:
        if file.suffix.lower() != ".txt":
            console.print(Text(f"Unsupported file: {file}"))
            failed += 1
            continue

        try:
            with console.status(f"Embedding {file.name}..."):
                _, created = ingest_file(file)

            if created:
                added += 1
            else:
                skipped += 1
        except (OSError, UnicodeError, ValueError) as exc:
            failed += 1
            console.print(Text(f"Could not import {file}: {exc}"))

    console.print(f"Added: {added}, unchanged: {skipped}, failed: {failed}")

    if failed:
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str,
    limit: int = typer.Option(3, min=1),
    max_distance: float | None = typer.Option(
        None,
        min=0,
        callback=validate_distance,
        help="Maximum embedding distance; lower is closer. No cutoff by default.",
    ),
):
    """Find poems by meaning."""
    console = Console()

    if not query.strip():
        raise typer.BadParameter("Search query must not be blank.", param_hint="query")

    with console.status("Searching poems..."):
        poems = search_poems_with_scores(query, limit, max_distance)

    if not poems:
        console.print(
            "No poems matched the distance cutoff, or the library is empty."
            if max_distance is not None
            else "No poems found. Import or save some poems first."
        )
        return

    for poem, distance in poems:
        title = poem.metadata.get("title", "Poem")
        console.print(
            Panel(
                Text(poem.page_content),
                title=Text(title),
                subtitle=Text(f"Distance: {distance:.4f} (lower is closer)"),
            )
        )


if __name__ == "__main__":
    app()
