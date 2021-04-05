from __future__ import annotations
import asyncio

import aiohttp
import bs4
import more_itertools

from . import cache, files
from .links import Link


class Minty():
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def find_sitemap_urls(self, sitemap_index: str) -> list[str]:
        get = self._generate_get(sitemap_index)
        content = await cache.get_or_set_cache(sitemap_index, get)
        soup = bs4.BeautifulSoup(content, 'lxml')
        
        sitemap_urls = []
        for sitemap_loc in soup.find_all('loc'):
            contents = sitemap_loc.contents
            url = contents[0]
            sitemap_urls.append(url)

        tasks = []
        for sitemap_url in sitemap_urls:
            get = self._generate_get(sitemap_url)
            task = cache.get_or_set_cache(sitemap_url, get)
            tasks.append(task)

        urls = []
        for task_chunk in more_itertools.chunked(tasks, 10):
            for content in await asyncio.gather(*task_chunk, return_exceptions=True):
                soup = bs4.BeautifulSoup(content, 'lxml')
                for loc in soup.find_all('loc'):
                    contents = loc.contents
                    url = contents[0]
                    urls.append(url)
        return urls

    async def find_eggs(self, urls: list[str]) -> list[str]:
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
            tasks = []
            for link in not_visited:
                url = link.url
                get = self._generate_get(url)
                async def get_for_link(link: Link):
                    content = await cache.get_or_set_cache(link.url, get)
                    return link, content
                task = get_for_link(link)
                tasks.append(task)

            for task_chunk in more_itertools.chunked(tasks, 10):
                for result in await asyncio.gather(*task_chunk, return_exceptions=True):
                    if isinstance(result, Exception):
                        raise result
                    link, content = result
                    soup = bs4.BeautifulSoup(content, features="html.parser")
                    link.eggs = list(self._parse_eggs(soup))
                    urls_for_link = self._parse_hrefs(soup)
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

    async def download_eggs(self, eggs: list[str]):
        breakpoint()
        for egg in eggs:
            name_parts = egg.split('/')
            egg_name = name_parts[len(name_parts) - 1]
            egg_path = files.to_path('eggs', 'cache', egg_name)
            egg_exists = files.exists(egg_path)
            if not egg_exists:
                get = self._generate_get(egg)
                content = await cache.get_or_set_cache(egg, get)
                files.write_binary(egg_path, content)

        eggs = [
            egg + '\n'
            for egg
            in eggs
        ]
        files.write('eggs.txt', eggs)

    def _generate_get(self, url: str):
        async def get():
            async with self.session.get(url) as response:
                content = await response.read()
                if not response.ok:
                    raise Exception(response.ok, content)
            return content
        return get

    def _parse_hrefs(self, soup: bs4.BeautifulSoup):
        for link in soup.find_all('a'):
            attrs: dict = link.attrs
            href: str = attrs['href']
            if href.startswith('https://www.mintyteeth.com') and \
                    not href.startswith('https://www.mintyteeth.com/wp-'):
                yield href

    def _parse_eggs(self, soup: bs4.BeautifulSoup):
        for image in soup.find_all('img'):
            attrs: dict = image.attrs
            src: str = attrs['src']
            if 'egg' in src.casefold():
                yield src
