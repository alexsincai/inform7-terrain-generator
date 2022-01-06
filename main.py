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

    array[-1] = f"{andor} {array[-1]}"
    out = ", ".join(array)

    return out.replace(f", {andor}", f" {andor}")


class Room:
    """
    A room prepresentation
    """

    def __init__(
        self,
        name: str = "Room",
        value: float = 0.0,
        attribute: str = "room attribute",
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
        self.attribute = attribute
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
        attribute = f"It is {self.attribute}."
        description = f'The description of {self.name} is "[{self.description}]".'
        printed = f'The printed name is "{self.printed_name}".'
        directions = (
            f"{self.name} is {pretty_list(array=neighbors, andor='and')}."
            if len(neighbors)
            else ""
        )

        return " ".join([name, attribute, description, printed, directions])


class TerrainMaker:
    """
    Creates a list of Inform7 rooms, all connected, which have related features.
    """

    def __init__(
        self,
        width: int = 6,
        height: int = 5,
        octaves: float = 3,
        seed: int = 3,
        name: str = "Room",
        description: str = "room description",
        initial: str = "Some initial description here",
        region: str = "Region",
        printed_name: str = "Room",
        attributes: Dict[str, str] = {
            "black": "The room is black",
            "grey": "The rrom is grey",
            "white": "The room is white",
        },
    ):
        self.width = max(1, width)
        self.height = max(1, height)
        self.octaves = octaves
        self.seed = seed
        self.name = name
        self.description = description
        self.initial = initial
        self.region = region
        self.printed_name = printed_name
        self.attributes = attributes

        self.noise = PerlinNoise(octaves=self.octaves, seed=self.seed)

    def __values(self) -> List[float]:
        out = []

        for height in range(1, self.height + 1):
            for width in range(1, self.width + 1):
                noise = (
                    self.noise(
                        [
                            width / self.width + 1,
                            height / self.height + 1,
                        ]
                    )
                    + 0.5
                )
                out.append(noise)

        return out

    def __rooms(self) -> List[Dict[str, Optional[str]]]:
        out = []
        index = 0

        values = self.__values()

        for height in range(1, self.height + 1):
            for width in range(1, self.width + 1):
                index += 1

                value = translate_value(
                    values[index - 1],
                    0,
                    1,
                    0,
                    len(self.attributes) - 1,
                )
                position = (width - 1, height - 1)
                keys = list(self.attributes.keys())
                count = (self.width * self.height) + 1

                out.append(
                    Room(
                        name=f"{self.name} {words(count - index)}".title(),
                        value=value,
                        attribute=keys[round(value)],
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

    def render(self, region: bool = True) -> str:
        """Outputs the list of generated rooms, with optional region

        Args:
            region (bool, optional): Generate a region as well? Defaults to True.

        Returns:
            str: The generated list of rooms, with attributes, connections and optional region.
        """
        keys = list(self.attributes.keys())
        out = []

        props = pretty_list(array=keys, andor="or")

        out.append(f"A room can be {props}. A room is usually {keys[0]}.")

        attributes = []
        attributes.append(f"To say {self.description}:")
        attributes.append(f'\tsay "{self.initial} [run paragraph on]";')

        for prop, desc in self.attributes.items():
            attributes.append(f'\tif the location is {prop}, say "{desc}";')

        attributes = "\n".join(attributes) + "."
        attributes = attributes.replace(";.", ".")

        out.append(attributes)

        for room in self.__rooms():
            out.append(room.render())

        if region:
            rooms = [r.name for r in self.__rooms()]
            isare = "is" if len(rooms) == 1 else "are"
            rooms = pretty_list(array=rooms, andor="and")
            out.append(f"{self.region} is a region. {rooms} {isare} in {self.region}.")

        return "\n\n".join(out)


def main():
    """
    Create a wilderness
    """
    terrain = TerrainMaker(
        width=5,
        height=4,
        name="Wilderness",
        region="Wilds",
        printed_name="Martian wilderness",
        description="wilderness-description",
        initial="[one of]Scrubland[or]Martian scrubland[or]Martian weeds[at random] [stretch] as far as the eye [can] see.",
        attributes={
            "flat": "The land here [are] flat.",
            "hilly": "The land [are] somewhat hilly.",
            "impacted": "[one of]A large[or]An eroded[or]A small[at random] crater [mar] the surface.",
            "treed": "A lone tree [dominate] the landscape.",
        },
    )
    print(terrain.render())


if __name__ == "__main__":
    main()
