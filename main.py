import typer
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main(
    topic: str = typer.Option(help="Poem topic."),
    lines: int = typer.Option(5, min=1, help="Maximum amount of lines."),
):
    prompt = ChatPromptTemplate.from_template(
        "Write a simple poem about {topic} in at most {lines} lines. "
        "Return only the poem."
    )

    model = ChatOllama(model="gemma2:9b")
    chain = prompt | model | StrOutputParser()

    console = Console()
    with console.status("Writing your poem...", spinner="dots"):
        poem = chain.invoke({"topic": topic, "lines": lines})

    console.print(Panel(Text(poem.strip()), title=Text(topic), border_style="cyan"))


if __name__ == "__main__":
    typer.run(main)
