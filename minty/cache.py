from __future__ import annotations
from typing import Any, Callable
import requests

from . import files


def get_or_set_cache(url: str, request: Callable[[str], requests.Response]):
    content = get_cache(url)
    if content is None:
        response = request(url)
        content = response.content
        set_cache(url, content)
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
    url = url.replace('https://', '')
    url = url.replace('.', '_')
    url = url.replace('/', '_')
    if not url.endswith('.html'):
        url = url + '.html'
    return url
