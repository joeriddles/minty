import asyncio

import aiohttp
from fake_useragent import UserAgent

from .minty import Minty


def get_headers():
    ua = UserAgent()
    user_agent = ua.firefox
    headers = { 'User-Agent': user_agent }
    return headers


async def main():
    mint_sitemap_index = 'https://www.mintyteeth.com/sitemap_index.xml'
    async with aiohttp.ClientSession(headers=get_headers()) as session:
        minty = Minty(session)
        urls = await minty.find_sitemap_urls(mint_sitemap_index)
        eggs = await minty.find_eggs(urls)
        await minty.download_eggs(eggs)


if __name__ == '__main__':
    # asyncio.run(main()) # see: https://github.com/aio-libs/aiohttp/issues/4324
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main())
