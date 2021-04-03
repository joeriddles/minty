from __future__ import annotations
from typing import Iterable
import os
import pathlib


PATH = pathlib.Path(__file__).parent.parent.absolute()
print(f'PATH: {PATH}')


def mkdir(path: str):
    os.mkdir(path)


def to_path(*args: str) -> str:
    return os.path.join(PATH, *args)


def exists(path: str) -> bool:
    return os.path.exists(path)


def write(path: str, data: Iterable[str]):
    with open(path, 'w') as fout:
        fout.writelines(data)


def write_binary(path: str, data: bytes):
    with open(path, 'wb') as fout:
        fout.write(data)


def read(path: str) -> list[str]:
    with open(path, mode='r') as fin:
        data = fin.readlines()
    return data


def read_binary(path: str) -> bytes:
    with open(path, mode='rb') as fin:
        data = fin.read()
    return data

