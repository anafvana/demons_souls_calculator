from csv import DictWriter
from dataclasses import dataclass, fields, field
from itertools import product


@dataclass
class Armour:
    name: str
    physical: int
    fire: int
    bleed: int
    poison: int
    plague: int
    total: int = field(init=False)

    def __post_init__(self):
        self.total = sum(
            [
                self.__getattribute__(f.name)
                for f in fields(Armour)
                if f.type is int and f.name != "total"
            ]
        )


@dataclass
class ArmourSet(Armour):
    parts: list[Armour] = field(default_factory=list, repr=False)  # type: ignore
    weighted_total: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()


head = [
    Armour("Gold Mask", physical=2, fire=8, bleed=16, poison=16, plague=16),
    Armour("Three-Conered Hat", physical=10, fire=5, bleed=6, poison=6, plague=24),
    Armour("Imperial Spy Hood", physical=12, fire=10, bleed=8, poison=16, plague=0),
    Armour("Assassin's Mask", physical=10, fire=7, bleed=6, poison=24, plague=0),
]
torso = [
    Armour("Old Ragged Robes", physical=26, fire=13, bleed=15, poison=15, plague=62),
    Armour("Black Leather Garb", physical=25, fire=17, bleed=15, poison=62, plague=0),
    Armour("Imperial Spy Clothes", physical=26, fire=18, bleed=24, poison=46, plague=0),
]
arms = [
    Armour("Old Ragged Gloves", physical=16, fire=8, bleed=9, poison=9, plague=37),
    Armour("Black Gloves", physical=15, fire=10, bleed=9, poison=37, plague=0),
    Armour("Imperial Spy Gloves", physical=15, fire=14, bleed=14, poison=32, plague=0),
]
legs = [
    Armour("Old Ragged Boots", physical=16, fire=8, bleed=9, poison=9, plague=37),
    Armour("Black Boots", physical=15, fire=10, bleed=9, poison=37, plague=0),
    Armour(
        "Imperial Spy Leggings", physical=15, fire=14, bleed=14, poison=32, plague=0
    ),
]


def make_armourset_list() -> list[ArmourSet]:
    """
    Generates all valid armour set combinations.

    Returns:
        list[ArmourSet]: All possible armour combinations.
    """

    armours: list[ArmourSet] = []

    for combo in product(head, torso, arms, legs):
        name = " + ".join(part.name for part in combo)
        parts = [part for part in combo]
        physical_sum = sum(part.physical for part in combo)
        fire_sum = sum(part.fire for part in combo)
        bleed_sum = sum(part.bleed for part in combo)
        poison_sum = sum(part.poison for part in combo)
        plague_sum = sum(part.plague for part in combo)
        armours.append(
            ArmourSet(
                name=name,
                physical=physical_sum,
                fire=fire_sum,
                bleed=bleed_sum,
                poison=poison_sum,
                plague=plague_sum,
                parts=parts,
            )
        )

    # -- WEIGHTED TOTAL CALCULATIONS ------------------------------- #
    min_poison = min(a.poison for a in armours)
    max_poison = max(a.poison for a in armours)
    min_plague = min(a.plague for a in armours)
    max_plague = max(a.plague for a in armours)
    min_total = min(a.total for a in armours)
    max_total = max(a.total for a in armours)

    for armour in armours:
        armour.weighted_total = get_geometric_mean(
            armour=armour,
            min_plague=min_plague,
            min_poison=min_poison,
            max_plague=max_plague,
            max_poison=max_poison,
            min_total=min_total,
            max_total=max_total,
        )

    return armours


def get_geometric_mean(
    armour: ArmourSet,
    min_poison: int,
    max_poison: int,
    min_plague: int,
    max_plague: int,
    min_total: int,
    max_total: int,
    poison_weight: float = 1.0,
    plague_weight: float = 1.0,
) -> int:
    """
    Calculates normalized weighted geometric mean of poison and plague resistances.
    Resulting score is 50% mean, 50% total defence.

    Args:
        armour (ArmourSet): The armour set to score.
        min_poison (int): Minimum poison value across all sets.
        max_poison (int): Maximum poison value across all sets.
        min_plague (int): Minimum plague value across all sets.
        max_plague (int): Maximum plague value across all sets.
        min_total (int): Minimum total stat across all sets.
        max_total (int): Maximum total stat across all sets.
        alpha (float, optional): Weight for poison. Defaults to 1.0.
        beta (float, optional): Weight for plague. Defaults to 1.0.

    Returns:
        int: Final combined score based on normalized total and weighted geometric mean.
    """

    def normalise(value: int, min_val: int, max_val: int) -> float:
        if max_val == min_val:
            return 0.0
        return (value - min_val) / (max_val - min_val)

    # Normalise values
    norm_poison = normalise(armour.poison, min_poison, max_poison)
    norm_plague = normalise(armour.plague, min_plague, max_plague)
    norm_total = normalise(armour.total, min_total, max_total)

    total_weight: float = poison_weight + plague_weight

    # Calculate geometric mean
    weighted_score = (norm_poison**poison_weight * norm_plague**plague_weight) ** (
        1 / total_weight
    )

    # Final score of 50% total, 50% weighted_score
    return 0.5 * norm_total + 0.5 * weighted_score


def write_to_csv(armours: list[ArmourSet], path: str) -> None:
    """
    Writes a list of ArmourSet objects to a CSV file.

    Args:
        armours (list[ArmourSet]): List of armour sets.
        path (str): Output CSV file path.
    """

    field_names: list[str] = [f.name for f in fields(ArmourSet) if f.repr]

    with open(path, mode="w") as csvfile:
        writer = DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for armour in armours:
            row = {field: getattr(armour, field) for field in field_names}
            writer.writerow(row)


if __name__ == "__main__":
    options = make_armourset_list()
    write_to_csv(options, "out.csv")
