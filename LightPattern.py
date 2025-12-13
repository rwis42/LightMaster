from dataclasses import dataclass, field
from typing import Tuple, Union

RGB = Tuple[int, int, int]

def _validate_rgb(value: Union[RGB, tuple, list]) -> RGB:
    if not (isinstance(value, (tuple, list)) and len(value) == 3 and all(isinstance(v, int) and 0 <= v <= 255 for v in value)):
        raise TypeError("color must be an RGB tuple (r, g, b) with 0-255 ints")
    return tuple(value)
from typing import List, Iterator, Optional


@dataclass
class Light:
    color: RGB = field(default_factory=lambda: (255, 255, 255), metadata={"validate": _validate_rgb})
    count: int = 1

    def __post_init__(self):
        if self.count < 0:
            raise ValueError("count must be non-negative")


class LightPattern:
    """
    Container for a list of lights. Each light has a color and a count.
    """

    def __init__(self, lights: Optional[List[Light]] = None):
        self._lights: List[Light] = []
        if lights:
            for l in lights:
                self.add_light(l.color, l.count)

    def as_list(self) -> List[Light]:
        return list(self._lights)

    def clear(self) -> None:
        self._lights.clear()

    def display(self) -> None:
        for light in self._lights:
            print(f"{light.color}({light.count})")

    def __iter__(self) -> Iterator[Light]:
        return iter(self._lights)

    def __len__(self) -> int:
        return len(self._lights)

    def __repr__(self) -> str:
        def __repr__(self) -> str:
            def _valid_rgb(c):
                return (
                    isinstance(c, (tuple, list))
                    and len(c) == 3
                    and all(isinstance(v, int) and 0 <= v <= 255 for v in c)
                )

            for l in self._lights:
                if not _valid_rgb(l.color):
                    raise ValueError("color must be an RGB tuple (r, g, b) with 0-255 ints")
            return f"LightPattern({self._lights!r})"
        