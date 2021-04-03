from __future__ import annotations
import re

from . import files


cache_folder_path = files.to_path('cache')
cache_folder_exists = files.exists(cache_folder_path)
if not cache_folder_exists:
    files.mkdir(cache_folder_path)


async def get_or_set_cache(
    url: str,
    request,
):
    content = get_cache(url)
    if content is None:
        content = await request()
        set_cache(url, content)
        print(f'requesting: {url}')
    else:
        print(f'from cache: {url}')
    return content


def set_cache(url: str, content):
    url = _get_cache_url(url)
    path = files.to_path('cache', url)
    files.write_binary(path, content)


def get_cache(url: str):
    url = _get_cache_url(url)
    content = None
    path = files.to_path('cache', url)
    if files.exists(path):
        content = files.read_binary(path)
    return content


def _get_cache_url(url: str) -> str:
    url = re.sub(r'https?:\/\/', '', url)
    url = url.replace('www.mintyteeth.com/', '')
    if not re.match(r'.*\.\w+$', url):
        url = url + '.html' # default to html if no file extension
    url = url.replace('/', '_')
    return url


def _ensure_cache_exists():
    cache_folder_path = files.to_path('cache')
    cache_folder_exists = files.exists(cache_folder_path)
    if not cache_folder_exists:
        files.mkdir(cache_folder_path)
    egg_cache_folder_path = files.to_path('cache', 'eggs')
    egg_cache_folder_exists = files.exists(egg_cache_folder_path)
    if not egg_cache_folder_exists:
        files.mkdir(egg_cache_folder_path)

_ensure_cache_exists()
