"""
Creates a list of Inform7 rooms, all connected, which have related features.
"""

from typing import Dict, List, Tuple, Optional, Union
from perlin_noise import PerlinNoise
from num2words import num2words as words


def translate_value(
    value: Union[int, float],
    from_min: Union[int, float] = 0,
    from_max: Union[int, float] = 1,
    to_min: Union[int, float] = 0,
    to_max: Union[int, float] = 1,
) -> float:
    """Maps a value from one range to another

    Args:
        value (Union[int, float]): The value to be mapped
        from_min (Union[int, float], optional): The minimum of the source range. Defaults to 0.
        from_max (Union[int, float], optional): The maximum of the source range. Defaults to 1.
        to_min (Union[int, float], optional): The minimum of the target range. Defaults to 0.
        to_max (Union[int, float], optional): The maximum of the target range. Defaults to 1.

    Returns:
        float: The value mapped to the [to_min, to_max] range
    """

    from_span = from_max - from_min
    to_span = to_max - to_min

    ret = float(value - from_min) / float(from_span)

    return to_min + (ret * to_span)


def pretty_list(
    array: List[str] = ["foo", "bar", "baz"],
    andor: str = "or",
) -> str:
    """Prettyfies a list

    Args:
        array (List[str], optional): A list of strings to join. Defaults to ["foo", "bar", "baz"].
        andor (str, optional): The last element conjunction. Defaults to "or".

    Returns:
        str: The resulting string
    """
    length = len(array)

    if not length:
        return ""

    if length == 1:
        return array[0]

    if length == 2:
        return f" {andor} ".join(array)

    temp = array[:-1] + [f"{andor} {array[-1]}"]
    out = ", ".join(temp)

    return out.replace(f", {andor}", f" {andor}")


class Room:
    """
    A room prepresentation
    """

    def __init__(
        self,
        name: str = "Room",
        value: float = 0.0,
        condition: str = "room condition",
        position: Tuple[int, int] = (0, 0),
        description: str = "The room description",
        printed_name: str = "Room",
        north: Optional[str] = None,
        south: Optional[str] = None,
        east: Optional[str] = None,
        west: Optional[str] = None,
    ):
        self.name = name
        self.value = value
        self.condition = condition
        self.position = position
        self.description = description
        self.printed_name = printed_name
        self.north = north
        self.south = south
        self.east = east
        self.west = west

    def render(self) -> str:
        """Generates an Inform7 room.

        Returns:
            str: The code for an Inform7 room.
        """
        north = f"north of {self.north}" if self.north else None
        south = f"south of {self.south}" if self.south else None
        east = f"east of {self.east}" if self.east else None
        west = f"west of {self.west}" if self.west else None

        neighbors = [north, south, east, west]
        neighbors = [d for d in neighbors if d]

        name = f"{self.name} is a room."
        condition = f"It is {self.condition}."
        description = f'The description of {self.name} is "[{self.description}]".'
        printed = f'The printed name is "{self.printed_name}".'
        directions = (
            f"{self.name} is {pretty_list(array=neighbors, andor='and')}."
            if len(neighbors)
            else ""
        )

        return " ".join([name, condition, description, printed, directions])


class Region:
    """
    A Region representation
    """

    def __init__(
        self,
        name: str = "Region",
        condition: str = "particular",
        rooms: List[str] = [],
    ):
        self.name = name
        self.condition = condition
        self.rooms = rooms

    def render(self) -> str:
        name = f"{self.name} is a region."
        rooms = pretty_list(array=[r for r in self.rooms], andor="and")
        isare = "is" if len(self.rooms) == 1 else "are"

        return " ".join([name, rooms, isare, f"in {self.name}."])


class TerrainMaker:
    """
    Creates a list of Inform7 rooms, all connected, which have related features.
    """

    def __init__(
        self,
        width: int = 6,
        height: int = 5,
        seed: int = 3,
        name: str = "Room",
        description: str = "room description",
        initial: str = "Some initial description here",
        region: str = "Region",
        printed_name: str = "Room",
        conditions: Dict[str, str] = {
            "black": "The room is black",
            "grey": "The room is grey",
            "white": "The room is white",
        },
    ):
        self.width = max(1, width)
        self.height = max(1, height)
        self.seed = seed
        self.name = name
        self.description = description
        self.initial = initial
        self.region = region
        self.printed_name = printed_name
        self.conditions = conditions

    def __str__(self):
        return self.render()

    def noise(self, horizontal: float = 0.0, vertical: float = 0.0):
        noise1 = PerlinNoise(octaves=3, seed=self.seed)
        noise2 = PerlinNoise(octaves=6, seed=self.seed)
        noise3 = PerlinNoise(octaves=12, seed=self.seed)
        noise4 = PerlinNoise(octaves=24, seed=self.seed)

        out = noise1([horizontal, vertical])
        out += noise2([horizontal, vertical]) * 0.5
        out += noise3([horizontal, vertical]) * 0.25
        out += noise4([horizontal, vertical]) * 0.125

        return out + 0.5

    def __values(self) -> List[float]:
        out = []

        for height in range(1, self.height + 1):
            for width in range(1, self.width + 1):
                noise = self.noise(width / self.width + 1, height / self.height + 1)
                out.append(noise)

        return out

    def __rooms(self) -> List[Dict[str, Optional[str]]]:
        out = []
        index = 0

        values = self.__values()
        conditions = self.conditions

        for height in range(1, self.height + 1):
            for width in range(1, self.width + 1):
                index += 1

                value = translate_value(values[index - 1], 0, 1, 0, len(conditions) - 1)
                position = (width - 1, height - 1)
                keys = list(conditions.keys())
                count = (self.width * self.height) + 1

                out.append(
                    Room(
                        name=f"{self.name} {words(count - index)}".title(),
                        value=value,
                        condition=keys[round(value)],
                        position=position,
                        description=self.description,
                        printed_name=self.printed_name,
                    )
                )

        for room in out:
            pos_x, pos_y = room.position

            if pos_y < self.height:
                to_south = [r for r in out if r.position == (pos_x, pos_y + 1)]
                room.north = to_south.pop().name if len(to_south) else None

            if pos_y > 0:
                to_north = [r for r in out if r.position == (pos_x, pos_y - 1)]
                room.south = to_north.pop().name if len(to_north) else None

            if pos_x < self.width:
                to_east = [r for r in out if r.position == (pos_x + 1, pos_y)]
                room.west = to_east.pop().name if len(to_east) else None

            if pos_x > 0:
                to_west = [r for r in out if r.position == (pos_x - 1, pos_y)]
                room.east = to_west.pop().name if len(to_west) else None

        return out

    def __regions(self):
        out = []

        for key in list(self.conditions.keys()):
            name = f"The {key} {self.region}".title()
            rooms = [r.name for r in self.__rooms() if r.condition == key]

            if len(rooms):
                out.append(
                    Region(
                        name=name,
                        condition=key,
                        rooms=rooms,
                    )
                )

        return out

    def __conditions(self):
        regions = [r.condition for r in self.__regions()]
        conditions = [c for c in list(self.conditions.keys()) if c in regions]

        out = []

        if len(conditions):
            intro = []
            intro.append(f"A room can be {pretty_list(array=conditions, andor='or')}.")
            intro.append(f"A room is usually {conditions[0]}.")

            out.append(" ".join(intro))
            out.append("")

        out.append(f"To say {self.description}:")
        out.append(f'\tsay "{self.initial} [run paragraph on]";')

        for index, condition in enumerate(conditions):
            description = self.conditions.get(condition)
            last = "." if index == len(conditions) - 1 else ";"

            out.append(f'\tif the location is {condition}, say "{description}"{last}')

        return "\n".join(out).strip()

    def render(self) -> str:
        """Outputs the list of generated rooms, as well as the regions

        Returns:
            str: The generated list of rooms, with conditions and connections as well as the regions
        """
        out = []

        out.append(self.__conditions())

        for room in self.__rooms():
            out.append(room.render())

        for region in self.__regions():
            out.append(region.render())

        return "\n\n".join(out)


def main():
    """
    Create a wilderness
    """
    terrain = TerrainMaker(
        width=5,
        height=4,
        seed=123,
        name="Wilderness",
        region="Wilds",
        printed_name="Martian wilderness",
        description="wilderness-description",
        initial="[one of]Scrubland[or]Martian scrubland[or]Martian weeds[at random] [stretch] as far as the eye [can] see.",
        conditions={
            "flat": "The land here [are] flat.",
            "bouldered": "A [if a random chance of 1 in 3 succeeds]large[end if] boulder [dominate] the landscape.",
            "cratered": "[one of]A large[or]An eroded[or]A small[at random] crater [mar] the surface.",
            "treed": "A [one of]lone[or]single[or]withered[or][at random] tree [dominate] the landscape.",
        },
    )
    print(terrain)


if __name__ == "__main__":
    main()
