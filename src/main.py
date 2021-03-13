import os
from typing import NewType, List
from collections import defaultdict
from contextlib import contextmanager

import cv2 as cv
import imutils
import numpy as np

import utils


Image = NewType('Image', np.ndarray)
Contour = NewType('COntours', np.ndarray)


@contextmanager
def cd(path):
    if log:
        with utils.cd(path):
            yield
    else:
        yield


def save(filename: str, image: Image) -> None:
    if log:
        cv.imwrite(filename + '.png', image)


def detect_polygons(image: Image) -> List[Contour]:
    binary = cv.adaptiveThreshold(
        image,
        maxValue=255,
        adaptiveMethod=cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv.THRESH_BINARY,
        blockSize=3,
        C=1,
    )
    save('binary', binary)

    opening = cv.morphologyEx(
        binary, op=cv.MORPH_OPEN,
        kernel=cv.getStructuringElement(cv.MORPH_ELLIPSE, (2, 2))
    )
    save('opening', opening)

    contours, hierarchy = cv.findContours(
        opening, mode=cv.RETR_LIST, method=cv.CHAIN_APPROX_SIMPLE
    )

    polygons = [cv.approxPolyDP(contour, epsilon=3, closed=True)
                for contour in contours
                if 1000 <= cv.contourArea(contour) <= 50000]
    polygons = [polygon for polygon in polygons if 5 <= len(polygon) <= 9]
    print(f'\tpolygons found: {len(polygons)}')

    contours_image = cv.drawContours(
        image, polygons,
        contourIdx=-1,  # Draw all
        color=255
    )
    save(f'contours', contours_image)

    return polygons


def get_warped_tile(image: Image, contour: Contour) -> Image:

    # TODO
    pass


def classify(tile: Image) -> str:
    pass  # TODO


def run(image: Image) -> None:
    save('source', image)

    with cd('preprocessing'):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        save('gray', gray)

        blurred = cv.GaussianBlur(
            gray, ksize=(9, 9), sigmaX=1, borderType=cv.BORDER_REFLECT
        )
        save('blurred', blurred)

    with cd('detection'):
        polygons = detect_polygons(blurred)

    with cd('warping'):
        tiles = []  # [get_warped_tile(gray, polygon) for polygon in polygons]

    with cd('classification'):
        d = defaultdict(list)
        for tile in tiles:
            d[classify(tile)].append(tile)

        for c, tiles in d.items():
            with utils.cd(c):
                for i, tile in enumerate(tiles):
                    cv.imwrite(str(i) + '.png', tile)


if __name__ == '__main__':
    images_path = 'images'
    out_path = 'out'
    log = True

    for root, _, filenames in os.walk(images_path):
        for filename in filenames:
            print(f'In progress: {filename}')

            image = cv.imread(os.path.join(root, filename))
            if image is None:
                continue

            path = os.path.join(out_path, filename)
            with utils.cd(utils.remove_file_extension(path)):
                run(image)

    print('Done!')
else:
    raise RuntimeError('I am main!')
