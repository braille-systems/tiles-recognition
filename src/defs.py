from typing import NewType, Tuple


Point = NewType('Point', Tuple[int, int])  # (x, y)
BoundingBox = NewType(
    'BoundingBox',
    Tuple[int, int, int, int]  # (x, y, w, h)
)
