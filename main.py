import typer
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from prompts import planning_prompt, revision_prompt, writing_prompt


def validate_poem(poem: str, limit: int) -> bool:
    return sum(1 for line in poem.splitlines() if line.strip()) <= limit


def main(
    topic: str = typer.Option(help="Poem topic."),
    lines: int = typer.Option(5, min=1, help="Maximum amount of lines."),
):
    model = ChatOllama(model="gemma2:9b")
    planning_chain = planning_prompt | model | StrOutputParser()
    writing_chain = writing_prompt | model | StrOutputParser()
    revision_chain = revision_prompt | model | StrOutputParser()

    console = Console()
    with console.status("Planning your poem...", spinner="dots"):
        plan = planning_chain.invoke({"topic": topic})

    console.print(
        Panel(Text(plan.strip()), title="Plan", border_style="yellow"),
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
        Panel(Text(poem.strip()), title=Text(topic.capitalize()), border_style="cyan"),
    )


if __name__ == "__main__":
    typer.run(main)
