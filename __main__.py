from __future__ import annotations
import os

import bs4
from fake_useragent import UserAgent
import requests


PATH = 'c:/users/josephriddle/Desktop/test_data/minty/'


class Link:
    url: str
    visited: bool
    eggs: list[str]
    def __init__(self, link: str) -> None:
        self.url = link
        self.visited = False
    def __str__(self) -> str:
        return self.url
    def __eq__(self, o) -> bool:
        return self.url == o.url
    def __hash__(self) -> int:
        return self.url.__hash__()


def get_headers():
    ua = UserAgent()
    user_agent = ua.firefox
    headers = { 'User-Agent': user_agent }
    return headers


def find_hrefs(soup: bs4.BeautifulSoup):
    for link in soup.find_all('a'):
        attrs: dict = link.attrs
        href: str = attrs['href']
        if href.startswith('https://www.mintyteeth.com') and 'wp-content' not in href:
            yield href


def find_eggs(soup: bs4.BeautifulSoup):
    for image in soup.find_all('img'):
        attrs: dict = image.attrs
        src: str = attrs['src']
        if 'egg' in src.casefold():
            yield src


def get_cache_url(url: str) -> str:
    url = url.replace('https://', '')
    url = url.replace('.', '_')
    url = url.replace('/', '_')
    if not url.endswith('.html'):
        url = url + '.html'
    return url


def cache(url: str, content):
    url = get_cache_url(url)
    with open(f'{PATH}cache/{url}', mode='wb') as fout:
        fout.write(content)


def get_cache(url: str):
    url = get_cache_url(url)
    content = None
    if os.path.exists(f'{PATH}cache/{url}'):
        with open(f'{PATH}cache/{url}', mode='rb') as fin:
            content = fin.read()
    return content


main_link = Link('https://www.mintyteeth.com')
links_by_url: dict[str, Link] = { main_link.url: main_link }

not_visited = [link for link in links_by_url.values() if not link.visited]
while not_visited:
    for link in not_visited:
        url = link.url

        content = get_cache(url)
        if content is None:
            print(f'visiting {url}')
            response = requests.get(link.url, headers=get_headers())
            content = response.content
            cache(url, content)
        else:
            print(f'used cache for {url}')
        soup = bs4.BeautifulSoup(content, features="html.parser")
        
        eggs_for_link = list(find_eggs(soup))
        link.eggs = eggs_for_link
        
        urls_for_link = find_hrefs(soup)
        for url in urls_for_link:
            if url not in links_by_url:
                sub_link = Link(url)
                links_by_url[url] = sub_link

        link.visited = True

    not_visited = [link for link in links_by_url.values() if not link.visited]

all_eggs = set()
for link in links_by_url.values():
    all_eggs.update(link.eggs)
all_eggs = list(all_eggs)

for egg in all_eggs:
    response = requests.get(egg, headers=get_headers())
    name_parts = egg.split('/')
    egg_name = name_parts[len(name_parts) - 1]
    egg_path = f'{PATH}eggs/{egg_name}'
    egg_exists = os.path.exists(egg_path)
    print(f'{egg_name} exists? {egg_exists}')
    if egg_exists:
        with open(egg_path, 'wb') as fout:
            fout.write(response.content)

with open(f'{PATH}eggs.txt', 'w') as fout:
    eggs = [
        egg + os.linesep
        for egg
        in all_eggs
    ]
    fout.writelines(eggs)
