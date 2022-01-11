"""Creates connected Inform7 rooms"""
from typing import List, Union
from perlin_noise import PerlinNoise
from num2words import num2words as words


def translate_value(
    value: Union[int, float],
    from_min: Union[int, float] = 0,
    from_max: Union[int, float] = 1,
    to_min: Union[int, float] = 0,
    to_max: Union[int, float] = 1,
) -> float:
    """Maps value from one range to another

    Args:
        value (Union[int, float]): The value to be mapped
        from_min (Union[int, float], optional): Input minimum. Defaults to 0.
        from_max (Union[int, float], optional): Input maximum. Defaults to 1.
        to_min (Union[int, float], optional): Output minimum. Defaults to 0.
        to_max (Union[int, float], optional): Output maximum. Defaults to 1.

    Returns:
        float: Mapped value
    """
    from_span = from_max - from_min
    to_span = to_max - to_min

    ret = float(value - from_min) / float(from_span)

    return to_min + (ret * to_span)


class Room:
    """Creates Inform7 room"""

    def __init__(self, name, index, region):
        self._name = name
        self.index = words(index).title()
        self.name = f"{name} {words(index).title()}"
        self.region = region
        self.east = None
        self.north = None

    def __str__(self):
        out = []
        out.append(f"{self.name} is a room.")
        out.append(f"The printed name is '{self._name}'.")

        dirs = []
        dirs.append(f"east of {self.east}" if self.east else None)
        dirs.append(f"north of {self.north}" if self.north else None)
        dirs = [d for d in dirs if d]

        if len(dirs):
            out.append(f"It is { ' and '.join(dirs)}.")

        return " ".join(out)


class Terrain:
    """Creates a series of interconnected Inform7 rooms, assembled into several regions"""

    def __init__(
        self,
        width,
        height,
        seed,
        name,
        regions,
        parent,
        entry_index=None,
        entry_name=None,
    ):
        self.width = width
        self.height = height
        self.seed = seed
        self.name = name
        self.regions = regions
        self.parent = parent
        self.entry_index = entry_index
        self.entry_name = entry_name

        self.rooms = self.build_rooms()

    def noise(
        self,
        horizontal: Union[int, float] = 0.0,
        vertical: Union[int, float] = 0.0,
    ) -> int:
        """Generates Perlin Noise for given coordinates

        Args:
            horizontal (Union[int, float], optional): Horizontal offset. Defaults to 0.0.
            vertical (Union[int, float], optional): Vertical offset. Defaults to 0.0.

        Returns:
            int: Noise value at given coordinates
        """
        noise1 = PerlinNoise(octaves=2, seed=self.seed)
        noise2 = PerlinNoise(octaves=4, seed=self.seed)
        noise3 = PerlinNoise(octaves=8, seed=self.seed)
        noise4 = PerlinNoise(octaves=16, seed=self.seed)
        noise5 = PerlinNoise(octaves=32, seed=self.seed)

        ret = noise1([horizontal + 1 / self.width, vertical + 1 / self.height])
        ret += noise2([horizontal + 1 / self.width, vertical + 1 / self.height])
        ret += noise3([horizontal + 1 / self.width, vertical + 1 / self.height]) * 0.5
        ret += noise4([horizontal + 1 / self.width, vertical + 1 / self.height]) * 0.25
        ret += noise5([horizontal + 1 / self.width, vertical + 1 / self.height]) * 0.125
        ret += 0.5

        return round(translate_value(ret, 0, 1, 0, len(self.regions) - 1))

    def build_rooms(self)->List[Room]:
        """Generates list of Inform7 rooms

        Returns:
            List[Room]: List of Rooms for the terrain
        """
        index = 1
        out = []

        for height in range(self.height):
            for width in range(self.width):
                noise = self.noise(width, height)
                room = Room(self.name, index, self.regions[noise])

                if width >= 1:
                    room.east = f"{self.name} {words(index - 1).title()}"

                if height >= 1:
                    room.north = f"{self.name} {words(index - 5).title()}"

                if self.entry_index and index == self.entry_index:
                    room.north = self.entry_name

                out.append(room)
                index += 1

        return out

    def __str__(self):
        out = ["\n".join(str(r) for r in self.rooms)]

        for region in self.regions:
            desc = [f"{region} {self.name} is a region."]
            rooms = [room.name for room in self.rooms if room.region == region]

            if len(rooms):
                desc.append(f"{ ', '.join(rooms)} are in {region} {self.name}.")
                out.append(" ".join(desc))

        parent = [f"{self.parent} {self.name} is a region."]
        regions = ", ".join([f"{region} {self.name}" for region in self.regions])
        parent.append(f"{regions} are in {self.parent} {self.name}.")

        out.append(f"{' '.join(parent)}")

        return "\n".join(out)

    def test(self) -> str:
        """Outputs test map

        Returns:
            str: The test map
        """
        out = ""

        for index, room in enumerate(self.rooms):
            out += room.region[0]
            if not (index + 1) % self.width:
                out += "\n"

        return out


def main():
    """Main generator function"""
    terrain = Terrain(
        width=5,
        height=4,
        seed=7362,
        name="Wilderness",
        regions=["Rocky", "Impacted", "Flat", "Vegetated"],
        parent="Northern",
        entry_index=3,
        entry_name="the weed-choked street",
    )
    terrain = str(terrain).replace("'", '"')

    print(terrain)


if __name__ == "__main__":
    main()
