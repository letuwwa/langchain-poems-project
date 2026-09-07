import typer
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def main(
    topic: str = typer.Option(help="Poem topic."),
    lines: str = typer.Option(5, min=1, help="Maximum amount of lines."),
):
    prompt = ChatPromptTemplate.from_template(
        "Write a simple poem about {topic} in at most {lines} lines. "
        "Return only the poem."
    )
    model = ChatOllama(model="gemma2:9b")
    chain = prompt | model | StrOutputParser()

    poem = chain.invoke({"topic": topic, "lines": lines})
    typer.echo(poem)


if __name__ == "__main__":
    typer.run(main)
