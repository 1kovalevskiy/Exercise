import sys
import argparse
import requests
from googleapiclient.discovery import build
import urllib.parse
import pprint

APIKEY = "AIzaSyAHn26JDpcxohkElf0vwrWJF20mByHk0M0"
APIKEY2 = "AIzaSyC0i5bRb8yoUAQl4iOo_WwWhovdQpJXEMU"

def google_search(query="Что такое backend", gl="ru", hl="ru"):
    service = build('customsearch', 'v1', developerKey=APIKEY2)
    res = service.cse().list(
        q=query,
        gl=gl,
        hl=hl,
        cx='85a7991e3aceaefa7',
    ).execute()
    service.close()
    return url_from_google(res)

def url_from_google(res):
    url_arr = []
    for i in range(len(res['items'])):
        url = res['items'][i]['link']
        url_arr.append(url)
    return url_arr

def links_from_url(url):
    url_arr = url.split("//")
    if url_arr[0].startswith('http'):
        url_arr2 = url_arr[1].split("/")
        base_url = url_arr[0] + "//" + url_arr2[0]
    else:
        url_arr2 = url_arr[0].split("/")
        base_url = url_arr2[0]
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return link_from_raw_page(response.text, base_url)
    except:
        return None

def link_from_raw_page(raw_page, base_url=None):
    link_arr = []
    link_arr2 = []
    from bs4 import BeautifulSoup
    soup = BeautifulSoup (raw_page, 'html.parser')
    for link in soup.find_all('a'):
        new_url = str(link.get('href'))
        if new_url.startswith("mailto") or new_url.startswith("tel") or new_url.startswith("tg://")\
                or new_url == "None" or new_url == "javascript:void(0)" or new_url == "javascript:void(0);":
            pass
        elif new_url.startswith("http"):
            link_arr.append(new_url)
        elif new_url.startswith("//"):
            link_arr.append(new_url[2:])
        elif base_url is not None:
            new_url = urllib.parse.urljoin(base_url, new_url)
            link_arr.append(new_url)
        else:
            pass
    return link_arr


def runner(query, limit=1000, recursion=1):
    max_result = limit
    linksfromgoogle = google_search(query=query)
    linkslib = []
    newlinkslib = linksfromgoogle
    input_iter = recursion
    iter = 0
    while iter < input_iter:
        linkslib += newlinkslib
        tmp = []
        for url in newlinkslib:
            newlinks = links_from_url(url)
            if newlinks is not None:
                tmp += newlinks
            if len(linkslib) + len(tmp) >= max_result:
                break
        newlinkslib = tmp
        iter += 1
    else:
        linkslib += newlinkslib
    pprint.pprint(linkslib[:max_result])


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?', default='Что такое Backend')

    parser.add_argument('-l', '--limit', default=1000)

    parser.add_argument('-r', '--recursion', default=1)

    return parser

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    runner(namespace.query, recursion=int(namespace.recursion), limit=int(namespace.limit))