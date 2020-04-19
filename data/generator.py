"""
Applies transformations on tiles.
Download set of images, use them as background for tiles to train object detection.
"""

import itertools
import os
import random
import zipfile
from dataclasses import dataclass
from typing import List, Generator, Iterable

import wget
from PIL import Image

Img = Image.Image
transparent = (255, 255, 255, 0)
background_size = 1000
n_images = 5000


@dataclass
class Label:
    x: int
    y: int
    w: int
    h: int
    c: str

    def __str__(self):
        return f'{self.x} {self.y} {self.w} {self.h} {self.c}'


@dataclass
class Tile:
    img: Img
    label: Label


@dataclass
class DataImage:
    img: Img
    labels: List[Label]


GenTiles = Generator[Tile, None, None]


def write(data_images: Iterable[DataImage], path: str) -> None:
    os.makedirs(path, exist_ok=True)
    for i, data_image in enumerate(data_images):
        print(f'Image: {i} of {n_images}')
        data_image.img.save(os.path.join(path, f'{i}.png'))
        with open(os.path.join(path, f'{i}.txt'), 'w') as f:
            for label in data_image.labels:
                f.write(str(label) + '\n')


def take(xs: Iterable, n) -> Generator:
    for _, x in zip(range(n), xs):
        yield x


def generate_data_image_helper(tiles: Iterable[Tile], background: Img) -> Generator[DataImage, None, None]:
    labels = []
    for tile in tiles:
        w, h = background.size
        x = random.randrange(w)
        y = random.randrange(h)
        background.paste(tile.img, (x, y), tile.img)
        labels.append(
            Label(x=x, y=y, w=tile.label.w, h=tile.label.h, c=tile.label.c)
        )

    yield DataImage(
        background,
        labels
    )


def generate_data_images(tiles: Iterable[Tile], bg_path: str) -> Generator[DataImage, None, None]:
    for filename in (f for f in os.listdir(bg_path)
                     if os.path.isfile(os.path.join(bg_path, f))):
        n_tiles = random.randrange(1, 10)
        background = Image.open(os.path.join(bg_path, filename))
        size = min(background.size)
        square_background = Image.new(background.mode, (size, size))
        square_background.paste(background, (0, 0))
        yield from generate_data_image_helper(
            take(tiles, n_tiles),
            square_background.resize((background_size, background_size))
        )


def apply_perspective(tiles: Iterable[Tile]) -> GenTiles:
    yield from tiles  # TODO


def apply_rotations_helper(tile: Tile, angle: int) -> GenTiles:
    for a in [angle, -angle]:
        rotated = tile.img.rotate(a, expand=True)
        w, h = rotated.size
        yield Tile(rotated, Label(x=0, y=0, w=w, h=h, c=tile.label.c))


def apply_rotations(tiles: Iterable[Tile], angles: List[int]) -> GenTiles:
    for tile, angle in zip(tiles, itertools.cycle(angles)):
        yield from apply_rotations_helper(tile, angle)


def tmp_write(tiles: Iterable[Tile], path: str) -> None:
    for i, tile in enumerate(tiles):
        print(f'Image: {i}')
        tile.img.save(os.path.join(path, f'{tile.label.c}{i}.png'))
        with open(os.path.join(path, f'{tile.label.c}{i}.txt'), 'w') as f:
            f.write(f'{tile.label}\n')


def apply_resize_helper(tile: Tile, size: int) -> GenTiles:
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
    for tile, size in zip(tiles, itertools.cycle(sizes)):
        yield from apply_resize_helper(tile, size)


def read_tiles(path: str, *, infinite=False) -> GenTiles:
    while True:
        for name in (f for f in os.listdir(path)
                     if os.path.isfile(os.path.join(path, f))):
            image = Image.open(os.path.join(path, name))
            w, h = image.size
            yield Tile(image, Label(x=0, y=0, w=w, h=h, c=name[0]))

            if not infinite:
                return


def download_backgrounds(path: str, link: str) -> None:
    if os.path.isdir(path):
        print('Needed data has been already downloaded!')
        return

    os.makedirs(path)
    print('Downloading will take some time! 1GB approximately')
    zip_path = os.path.join(path, 'data.zip')
    wget.download(link, zip_path)
    print('Downloaded! Unzipping...')
    with zipfile.ZipFile(os.path.join(zip_path), 'r') as zf:
        zf.extractall(path)
    os.remove(zip_path)


def main() -> None:
    tiles_path = os.path.join('data', 'raw')
    bg_path = os.path.join('data', 'background', 'val2017')
    res_path = os.path.join('data', 'dataset')
    sizes = [100, 120, 150, 180, 190, 200, 200]  # TODO tune
    angles = [5, 10, 15, 20, 30, 35]

    debug = False

    tiles = read_tiles(tiles_path, infinite=not debug)
    tiles = apply_rotations(tiles, angles)
    tiles = apply_resize(tiles, sizes)
    tiles = apply_perspective(tiles)
    if debug:
        tmp_write(tiles, os.path.join('data', 'tmp'))

    download_backgrounds(
        bg_path,
        'http://images.cocodataset.org/zips/val2017.zip'
    )
    data_images = generate_data_images(tiles, bg_path)
    write(data_images, res_path)


if __name__ == '__main__':
    main()
