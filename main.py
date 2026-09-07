import typer
from langchain_ollama import ChatOllama


def main():
    model = ChatOllama(model="gemma2:9b")
    response = model.invoke("Write a simple poem of up to 5 lines. Return only the poem.")
    typer.echo(response.content)


if __name__ == "__main__":
    typer.run(main)
