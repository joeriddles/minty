from __future__ import annotations

import bs4
from fake_useragent import UserAgent
import requests

from . import cache, files
from .links import Link


def get_headers():
    ua = UserAgent()
    user_agent = ua.firefox
    headers = { 'User-Agent': user_agent }
    return headers


def get(url: str):
    return requests.get(url, headers=get_headers())


def parse_hrefs(soup: bs4.BeautifulSoup):
    for link in soup.find_all('a'):
        attrs: dict = link.attrs
        href: str = attrs['href']
        if href.startswith('https://www.mintyteeth.com') and \
                not href.startswith('https://www.mintyteeth.com/wp-'):
            yield href


def parse_eggs(soup: bs4.BeautifulSoup):
    for image in soup.find_all('img'):
        attrs: dict = image.attrs
        src: str = attrs['src']
        if 'egg' in src.casefold():
            yield src


def find_sitemap_urls(sitemap_index: str) -> list[str]:
    content = cache.get_or_set_cache(sitemap_index, get)
    soup = bs4.BeautifulSoup(content, 'lxml')
    
    sitemap_urls = []
    for sitemap_loc in soup.find_all('loc'):
        contents = sitemap_loc.contents
        url = contents[0]
        sitemap_urls.append(url)

    urls = []
    for sitemap_url in sitemap_urls:
        content = cache.get_or_set_cache(sitemap_url, get)
        soup = bs4.BeautifulSoup(content, 'lxml')
        for loc in soup.find_all('loc'):
            contents = loc.contents
            url = contents[0]
            urls.append(url)

    return urls


def find_eggs(urls: list[str]) -> list[str]:
    links_by_url = {
        url: Link(url)
        for url
        in urls
    }

    not_visited = [
        link for
        link in
        links_by_url.values() 
        if not link.visited
    ]
    while not_visited:
        for link in not_visited:
            url = link.url
            content = cache.get_or_set_cache(url, get)
            soup = bs4.BeautifulSoup(content, features="html.parser")
            link.eggs = list(parse_eggs(soup))
            urls_for_link = parse_hrefs(soup)
            for url in urls_for_link:
                if url not in links_by_url:
                    sub_link = Link(url)
                    links_by_url[url] = sub_link
            link.visited = True

        not_visited = [
            link for
            link in
            links_by_url.values()
            if not link.visited
        ]

    eggs_set: set[str] = set()
    for link in links_by_url.values():
        eggs_set.update(link.eggs)
    eggs: list[str] = sorted(eggs_set)
    return eggs


def download_eggs(eggs: list[str]):
    for egg in eggs:
        response = requests.get(egg, headers=get_headers())
        name_parts = egg.split('/')
        egg_name = name_parts[len(name_parts) - 1]
        egg_path = files.to_path(f'eggs/{egg_name}')
        egg_exists = files.exists(egg_path)
        print(f'{egg_name} exists? {egg_exists}')
        if egg_exists:
            files.write_binary(egg_path, response.content)
    files.write('eggs.txt', eggs)
