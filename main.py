import typer
from rich.align import Align
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from prompts import (
    explanation_prompt,
    planning_prompt,
    revision_prompt,
    writing_prompt,
    router_prompt,
)


def validate_poem(poem: str, limit: int) -> bool:
    return sum(1 for line in poem.splitlines() if line.strip()) <= limit


def main(
    request: str = typer.Option(
        ..., "--request", "--topic", help="Ask to write or explain a poem."
    ),
    lines: int = typer.Option(5, min=1, help="Maximum amount of lines."),
):
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
        explanation_chain = explanation_prompt | model | StrOutputParser()
        with console.status("Explaining your poem...", spinner="dots"):
            explanation = explanation_chain.invoke({"request": request})
        console.print(
            Align.center(
                Panel.fit(Text(explanation.strip()), title="Explanation", border_style="cyan")
            )
        )
        return

    topic = request
    planning_chain = planning_prompt | model | StrOutputParser()
    writing_chain = writing_prompt | model | StrOutputParser()
    revision_chain = revision_prompt | model | StrOutputParser()

    with console.status("Planning your poem...", spinner="dots"):
        plan = planning_chain.invoke({"topic": topic})

    console.print(
        Align.center(Panel.fit(Text(plan.strip()), title="Plan", border_style="yellow")),
    )

    with console.status("Writing your poem...", spinner="dots"):
        poem = writing_chain.invoke({"topic": topic, "lines": lines, "plan": plan})

    if not validate_poem(poem, lines):
        with console.status("Shortening your poem...", spinner="dots"):
            poem = revision_chain.invoke({"poem": poem, "lines": lines})

        if not validate_poem(poem, lines):
            console.print(
                "[yellow]The revised poem still exceeds the line limit.[/yellow]"
            )

    console.print(
        Align.center(
            Panel.fit(Text(poem.strip()), title=Text(topic.capitalize()), border_style="cyan")
        ),
    )


if __name__ == "__main__":
    typer.run(main)
