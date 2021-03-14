from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class BrailleDots:
    d1: bool = False
    d2: bool = False
    d3: bool = False
    d4: bool = False
    d5: bool = False
    d6: bool = False

    def copy(
        self,
        d1: bool = False, d2: bool = False, d3: bool = False,
        d4: bool = False, d5: bool = False, d6: bool = False,
    ) -> 'BrailleDots':
        return BrailleDots(
            d1=self.d1 or d1,
            d2=self.d2 or d2,
            d3=self.d3 or d3,
            d4=self.d4 or d4,
            d5=self.d5 or d5,
            d6=self.d6 or d6,
        )

    def to_list(self) -> List[bool]:
        return [self.d1, self.d2, self.d3, self.d4, self.d5, self.d6]

    def __str__(self) -> str:
        return ''.join('F' if d else 'E' for d in self.to_list())

    @staticmethod
    def of_str(dots: str) -> 'BrailleDots':
        return BrailleDots(
            **{f'd{i}': d == 'F' for i, d in enumerate(dots.split(', '), 1)}
        )


symbols = [
    ('А', BrailleDots.of_str('F, E, E, E, E, E')),
    ('Б', BrailleDots.of_str('F, F, E, E, E, E')),
    ('В', BrailleDots.of_str('E, F, E, F, F, F')),
    ('Г', BrailleDots.of_str('F, F, E, F, F, E')),
    ('Д', BrailleDots.of_str('F, E, E, F, F, E')),
    ('Е', BrailleDots.of_str('F, E, E, E, F, E')),
    ('Ё', BrailleDots.of_str('F, E, E, E, E, F')),
    ('Ж', BrailleDots.of_str('E, F, E, F, F, E')),
    ('З', BrailleDots.of_str('F, E, F, E, F, F')),
    ('И', BrailleDots.of_str('E, F, E, F, E, E')),
    ('Й', BrailleDots.of_str('F, F, F, F, E, F')),
    ('К', BrailleDots.of_str('F, E, F, E, E, E')),
    ('Л', BrailleDots.of_str('F, F, F, E, E, E')),
    ('М', BrailleDots.of_str('F, E, F, F, E, E')),
    ('Н', BrailleDots.of_str('F, E, F, F, F, E')),
    ('О', BrailleDots.of_str('F, E, F, E, F, E')),
    ('П', BrailleDots.of_str('F, F, F, F, E, E')),
    ('Р', BrailleDots.of_str('F, F, F, E, F, E')),
    ('С', BrailleDots.of_str('E, F, F, F, E, E')),
    ('Т', BrailleDots.of_str('E, F, F, F, F, E')),
    ('У', BrailleDots.of_str('F, E, F, E, E, F')),
    ('Ф', BrailleDots.of_str('F, F, E, F, E, E')),
    ('Х', BrailleDots.of_str('F, F, E, E, F, E')),
    ('Ц', BrailleDots.of_str('F, E, E, F, E, E')),
    ('Ч', BrailleDots.of_str('F, F, F, F, F, E')),
    ('Ш', BrailleDots.of_str('F, E, E, E, F, F')),
    ('Щ', BrailleDots.of_str('F, E, F, F, E, F')),
    ('Ъ', BrailleDots.of_str('F, F, F, E, F, F')),
    ('Ы', BrailleDots.of_str('E, F, F, F, E, F')),
    ('Ь', BrailleDots.of_str('E, F, F, F, F, F')),
    ('Э', BrailleDots.of_str('E, F, E, F, E, F')),
    ('Ю', BrailleDots.of_str('F, F, E, E, F, F')),
    ('Я', BrailleDots.of_str('F, F, E, F, E, F')),
]

dots_to_chars = {dots: char for char, dots in symbols}
