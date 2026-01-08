import os
from typing import List


def read_lines(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
