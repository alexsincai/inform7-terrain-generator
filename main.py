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
        description: str = "[room-description]",
        region: str = "Region",
        properties: List[str] = ["black", "grey", "white"],
    ):
        self.width = max(1, width)
        self.height = max(1, height)
        self.octaves = octaves
        self.seed = seed
        self.name = name
        self.description = description
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
                south = (
                    f"{self.name} {words(index - height - 1)}".title()
                    if height > 1
                    else None
                )

                out.append(
                    {
                        "name": f"{self.name} {words(index)}".title(),
                        "value": self.properties[round(value)],
                        "east": east,
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
        length = len(self.properties)

        if length > 2:
            props = ", ".join(
                self.properties[0:-1] + [f"or {self.properties[-1]}"]
                if length > 1
                else self.properties
            ).replace(", or", " or")

        elif length == 2:
            props = " or ".join(self.properties)

        else:
            props = "".join(self.properties)

        out.append(f"A room can be {props}. A room is usually {self.properties[0]}.")

        for room in self.__rooms():
            room = f"{room.get('name')} is a room. "
            room += f'The description is "{self.description}". '
            room += f"It is {room.get('value')}. "

            east = f"east of {room.get('east')}" if room.get("east") else None
            south = f"south of {room.get('south')}" if room.get("south") else None
            directions = [east, south]
            directions = [d for d in directions if d]

            if len(directions):
                room += f"{room.get('name')} is { ' and '.join(directions) }."

            out.append(f"{room.strip()}")

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

        return "\n\n".join([o.strip() for o in out if len(o.strip())])


def main():
    """
    Create a wilderness
    """
    terrain = TerrainMaker(
        width=5,
        height=4,
        name="Wilderness",
        region="Wilds",
        properties=["flat", "hilly", "impacted", "treed"],
    )
    print(terrain.print())


if __name__ == "__main__":
    main()
