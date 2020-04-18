"""
Applies transformations on tiles.
Download set of images, use them as background for tiles to train object detection.
"""

import itertools
import os
import zipfile
from dataclasses import dataclass
from typing import List, Generator, Iterable

import wget
from PIL import Image

BACKGROUND_LINK = 'http://images.cocodataset.org/zips/val2017.zip'
Img = Image.Image


@dataclass
class Label:
    x: int
    y: int
    w: int
    h: int
    c: str


@dataclass
class Tile:
    img: Img
    label: Label


@dataclass
class DataImage:
    img: Img
    labels: List[Label]


GenTiles = Generator[Tile, None, None]


def write(data_images: Iterable[DataImage]) -> None:
    pass  # TODO


def generate_data_images(tiles: Iterable[Tile], bg_path: str = '') -> Generator[DataImage, None, None]:
    yield from (DataImage(tile.img, [tile.label]) for tile in tiles)  # TODO


def apply_perspective(tiles: Iterable[Tile]) -> GenTiles:
    yield from tiles  # TODO


def apply_rotations_helper(tile: Tile, angle: int) -> GenTiles:
    yield Tile(tile.img.rotate(angle), tile.label)
    yield Tile(tile.img.rotate(-angle), tile.label)
    # TODO edit labels
    # TODO padding


def apply_rotations(tiles: Iterable[Tile], angles: List[int]) -> GenTiles:
    for tile, angle in itertools.product(tiles, angles):
        yield from apply_rotations_helper(tile, angle)


def tmp_write(tiles: Iterable[Tile], path: str) -> None:
    for i, tile in enumerate(tiles):
        print(f'Image: {i}')
        tile.img.save(os.path.join(path, f'{tile.label.c}{i}.png'))


def apply_resize_helper(tile: Tile, size: int) -> GenTiles:
    transparent = (255, 255, 255, 0)

    old_size = max(tile.img.size)
    square = Image.new(tile.img.mode, (old_size, old_size), color=transparent)
    square.paste(tile.img, (0, 0))

    label = Label(
        x=0, y=0,
        w=int(size / old_size * tile.label.w),
        h=int(size / old_size * tile.label.h),
        c=tile.label.c
    )

    yield Tile(square.resize((size, size)), label)


def apply_resize(tiles: Iterable[Tile], sizes: List[int]) -> GenTiles:
    for tile, size in itertools.product(tiles, sizes):
        yield from apply_resize_helper(tile, size)


def read_tiles(path: str, *, infinite=False) -> GenTiles:
    let_one_iteration = True
    while let_one_iteration:
        let_one_iteration = infinite
        for name in (f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))):
            image = Image.open(os.path.join(path, name))
            w, h = image.size
            yield Tile(image, Label(x=0, y=0, w=w, h=h, c=name[0]))


def download_backgrounds(path: str) -> None:
    if os.path.isdir(path):
        print('Needed data has been already downloaded!')
        return

    os.makedirs(path)
    print('Downloading will take some time! 1GB approximately')
    zip_path = os.path.join(path, 'data.zip')
    wget.download(BACKGROUND_LINK, zip_path)
    print('Downloaded! Unzipping...')
    with zipfile.ZipFile(os.path.join(zip_path), 'r') as zf:
        zf.extractall(path)
    os.remove(zip_path)


def main() -> None:
    infinite = True  # True means no debug

    tiles_path = os.path.join('data', 'raw')
    sizes = [20, 50, 100, 150, 200, 300, 400]  # TODO tune
    angles = [5, 10, 15, 20, 30, 40]

    tiles = read_tiles(tiles_path, infinite=infinite)
    tiles = apply_resize(tiles, sizes)
    tiles = apply_rotations(tiles, angles)
    tiles = apply_perspective(tiles)
    if not infinite:
        tmp_write(tiles, os.path.join('data', 'tmp'))  # TODO

    download_backgrounds(os.path.join('data', 'background'))
    data_images = generate_data_images(tiles)
    write(data_images)


if __name__ == '__main__':
    main()
