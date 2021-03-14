import os
from pathlib import Path, PurePath
from contextlib import contextmanager


@contextmanager
def cd(path):
    cwd = Path.cwd()
    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


def remove_file_extension(path):
    return os.path.splitext(path)[0]
