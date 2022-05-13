import configparser
import typer
import os
import sys

app = typer.Typer()

@app.command()
def build():
    pass



def main():
    """
    Main function.
    """
    print('Hello World!')


if __name__ == "__main__":
    main()