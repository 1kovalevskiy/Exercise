import logging
from bs4 import BeautifulSoup
import re
import requests
from googleapiclient.discovery import build
import urllib.parse
import pprint
import typer
from settings import APIKEY

app = typer.Typer()
logger = logging.getLogger(__name__)


def search_google(query="Что такое backend", gl="ru", hl="ru"):
    service = build('customsearch', 'v1', developerKey=APIKEY)
    res = service.cse().list(
        q=query,
        gl=gl,
        hl=hl,
        cx='85a7991e3aceaefa7',
    ).execute()
    service.close()
    for item in res['items']:
        yield item['link']


def get_base_from_url(url):
    url_without_http = url.split("//")
    if url_without_http[0].startswith('http'):
        url_part2 = url_without_http[1].split("/")
        return url_without_http[0] + "//" + url_part2[0]
    else:
        url_part2 = url_without_http[0].split("/")
        return url_part2[0]


def get_urls_from_url(url):
    base_url = get_base_from_url(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception:
        logger.error("OOps", exc_info=True)
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            new_url = str(link.get('href'))
            if new_url.startswith('http'):
                yield new_url
            elif re.match("/(\w|\?)+", new_url):
                yield urllib.parse.urljoin(base_url, new_url)
            elif new_url.startswith('//'):
                yield new_url[2:]


def runner(query: str = typer.Argument(None, help="Your query"),
           max_count: int = typer.Option(1000, '--limit', '-l',
                                         help="maximum count of output_links to "
                                              "display"),
           recursion: int = typer.Option(1, '--recursion', '-r',
                                         help="level of recursion")):
    output_links = []
    work_links = list(search_google(query=query))
    iteration_counter = 0
    while iteration_counter < recursion:
        output_links += work_links
        temporary_links = []
        for url in work_links:
            temporary_links += list(get_urls_from_url(url))
            if len(output_links) + len(temporary_links) >= max_count:
                break
        work_links = temporary_links
        iteration_counter += 1
    else:
        output_links += work_links
    pprint.pprint(output_links[:max_count])
    typer.secho(f"Printed {len(output_links[:max_count])} URL's",
                fg=typer.colors.BRIGHT_GREEN)


if __name__ == '__main__':
    typer.run(runner)
