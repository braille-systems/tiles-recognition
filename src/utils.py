import os
from math import sqrt
from pathlib import Path
from contextlib import contextmanager

from defs import Point, BoundingBox


def distance(p1: Point, p2: Point) -> float:
    x1, y1 = p1
    x2, y2 = p2
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def bb_in_bb(checked: BoundingBox, reference: BoundingBox) -> bool:
    x, y, w, h = checked
    xx = x + w
    yy = y + h

    rx, ry, rw, rh = reference
    rxx = rx + rw
    ryy = ry + rh

    xs_in = rx <= x <= rxx and rx <= xx <= rxx
    ys_in = ry <= y <= ryy and ry <= yy <= ryy
    return xs_in and ys_in


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
