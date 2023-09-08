import typer
from rich import print
from typing_extensions import Annotated

from scrapy.crawler import CrawlerProcess
from yelptesttask.spider import YelpSpider


def main(
    query: Annotated[str, typer.Option(help="Query string to search for")],
    location: Annotated[str, typer.Option(help="Location to search in")],
):
    print(f"Searching for [bold]{query}[/bold] in [bold]{location}[/bold]...")

    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "items.json": {"format": "json"},
            },
        }
    )

    process.crawl(YelpSpider, query=query, location=location)
    process.start()


if __name__ == "__main__":
    typer.run(main)
