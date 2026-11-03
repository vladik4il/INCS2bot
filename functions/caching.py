import json
import os
from pathlib import Path

import filelock

__all__ = ['load_cache', 'dump_cache', 'dump_cache_changes']


def get_filelock(path: Path, *, timeout: int = 10):
    return filelock.FileLock(path.with_suffix(path.suffix + '.lock'), timeout=timeout)


def _read(path: Path) -> dict[str, ...]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _write(path: Path, data: dict[str, ...]) -> None:
    # serialize first so a TypeError can't leave a half-written file behind
    data = json.dumps(data, indent=4, ensure_ascii=False)

    # fixed temp name is safe because the lock serializes all writers
    tmp = path.with_suffix(path.suffix + '.tmp')
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)  # atomic on POSIX
    finally:
        tmp.unlink(missing_ok=True)

def load_cache(path: Path, *, timeout: int = 10) -> dict[str, ...]:
    with get_filelock(path, timeout=timeout):
        return _read(path)


def dump_cache(path: Path, cache: dict[str, ...], *, timeout: int = 5):
    with get_filelock(path, timeout=timeout):
        _write(path, cache)


def dump_cache_changes(path: Path, changes: dict[str, ...], *, timeout: int = 10):
    with get_filelock(path, timeout=timeout):
        _write(path, _read(path) | changes)
