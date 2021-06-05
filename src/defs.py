from typing import NewType, Tuple
import numpy as np


Image = NewType('Image', np.ndarray)
Contour = NewType('Contours', np.ndarray)
Point = NewType('Point', Tuple[int, int])  # (x, y)
BoundingBox = NewType(
    'BoundingBox',
    Tuple[int, int, int, int]  # (x, y, w, h)
)
