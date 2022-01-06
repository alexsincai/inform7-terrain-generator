"""
Creates a list of Inform7 rooms, all connected, which have related features.
"""

from typing import Dict, List, Optional, Union
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
        properties: Dict[str, str] = {
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
        self.properties = properties

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
        index = 1

        values = self.__values()

        for height in range(1, self.height + 1):
            for width in range(1, self.width + 1):
                value = translate_value(
                    values[index - 1],
                    0,
                    1,
                    0,
                    len(self.properties) - 1,
                )
                east = f"{self.name} {words(index - 1)}".title() if width > 1 else None
                west = (
                    f"{self.name} {words(index + 1)}".title()
                    if width <= self.width
                    else None
                )
                north = (
                    f"{self.name} {words(index - height + 1)}".title()
                    if height > 1
                    else None
                )
                south = (
                    f"{self.name} {words(index - height - 1)}".title()
                    if height > 1
                    else None
                )

                keys = list(self.properties.keys())

                out.append(
                    {
                        "name": f"{self.name} {words(index)}".title(),
                        "value": keys[round(value)],
                        "east": east,
                        "west": west,
                        "north": north,
                        "south": south,
                    }
                )
                index += 1

        return out

    def print(self, region: bool = True) -> str:
        """Outputs the list of generated rooms, with optional region

        Args:
            region (bool, optional): Generate a region as well? Defaults to True.

        Returns:
            str: The generated list of rooms, with properties, connections and optional region.
        """
        out = []
        length = len(self.properties.keys())
        keys = list(self.properties.keys())

        if length > 2:
            props = ", ".join(
                keys[0:-1] + [f"or {keys[-1]}"] if length > 1 else keys
            ).replace(", or", " or")

        elif length == 2:
            props = " or ".join(keys)

        else:
            props = "".join(keys)

        out.append(f"A room can be {props}. A room is usually {keys[0]}.")

        properties = []
        properties.append(f"To say {self.description}:")
        properties.append(f'\tsay "{self.initial}[run paragraph on]";')

        for prop, desc in self.properties.items():
            properties.append(f'\tif the location is {prop}, say "{desc}";')

        properties = "\n".join(properties) + "."
        properties = properties.replace(";.", ".")

        out.append(properties)

        for room in self.__rooms():
            this_room = f"{room.get('name')} is a room. "
            this_room += f'The description is "[{self.description}]". '
            this_room += f"It is {room.get('value')}. "

            east = f"east of {room.get('east')}" if room.get("east") else None
            west = f"west of {room.get('west')}" if room.get("west") else None
            north = f"north of {room.get('north')}" if room.get("north") else None
            south = f"south of {room.get('south')}" if room.get("south") else None

            directions = [east, west, north, south]
            directions = [d for d in directions if d]

            if len(directions):
                this_room += f"{room.get('name')} is { ' and '.join(directions) }."

            out.append(f"{this_room.strip()}")

        if region:
            rooms = [r.get("name") for r in self.__rooms()]
            length = len(rooms)

            if length > 1:
                rooms[-1] = f"and {rooms[-1]}"

            rooms = ", ".join(rooms).replace(", and", " and")

            out.append(
                f"\n{self.region} is a region. "
                + f"{rooms} {'are' if length > 1 else 'is'} in {self.region}."
            )

        return "\n\n".join(out)


def main():
    """
    Create a wilderness
    """
    terrain = TerrainMaker(
        width=2,
        height=2,
        name="Wilderness",
        region="Wilds",
        description="wilderness-description",
        initial="[one of]Scrubland[or]Martian scrubland[or]Martian weeds[at random] [stretch] as far as the eye [can] see.",
        properties={
            "flat": "The land here is flat.",
            "hilly": "The land is somewhat hilly",
            "impacted": "A [one of]large[or]eroded[or]small[at random] crater mars the surface.",
            "treed": "A lone tree dominates the landscape.",
        },
    )
    print(terrain.print())


if __name__ == "__main__":
    main()
