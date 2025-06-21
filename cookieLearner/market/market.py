from dataclasses import dataclass
import random


@dataclass
class GameEnvironment:
    bank_level: int
    num_brokers: int


class Good:
    """Represents a tradable good in the market.

    Attributes
    ----------
    id : int
        The unique identifier for the good.
    name : str
        The name of the good.
    symbol : str
        The symbol representing the good.
    company : str
        The company associated with the good.
    desc : str
        A description of the good.
    bank : Bank
        The bank associated with the good.

    """

    id: int
    hidden: bool = False
    active: bool = False
    last: float = 0.0
    building: str
    stock: int = 0
    mode: int = 0
    dur: int = 0
    prev: int = 0
    val: float = 1.0
    vals: list[float] = [1.0]
    delta: float = 0.0
    name: str
    company: str
    symbol: str

    def __init__(
        self,
        id: int,
        name: str,
        symbol: str,
        company: str,
        desc: str,
        env: GameEnvironment,
    ) -> None:
        self.id = id
        self.name = name
        self.symbol = symbol
        self.company = company
        self.desc = desc
        self.env = env

    @property
    def resting_value(self) -> float:
        """Returns the resting value of the good.

        Returns:
            float: The resting value of the good.

        """
        return 10 + 10 * self.id + (self.env.bank_level - 1)

    def tick(self, globD: float, globP: float, dragonBoost: float) -> None:
        self.delta = self.delta * 0.97 + 0.01 * dragonBoost

        # Mode based delta adjustments
        if self.mode == 0:
            self.delta *= 0.95
            self.delta += 0.05 * (random.random() - 0.5)
        elif self.mode == 2:
            self.delta *= 0.99
            self.delta -= 0.05 * (random.random() - 0.1)
        elif self.mode == 3:
            self.delta += 0.15 * (random.random() - 0.1)
            self.val += random.random() * 5
        elif self.mode == 4:
            self.delta -= 0.15 * (random.random() - 0.1)
            self.val -= random.random()
        elif self.mode == 5:
            self.delta += 0.3 * (random.random() - 0.5)

        self.val += (self.resting_value - self.val) * 0.01

        if globD != 0 and random.random() < globP:
            self.val -= (1 + self.delta * random.random() ** 3 * 7) * globD
            self.val -= globD * (1 + random.random() ** 3 * 7)
            self.delta += globD * (1 + random.random() * 4)
            self.dur = 0

        self.val += (random.random() - 0.5) ** 2 * 3
        self.delta += 0.1 * (random.random() - 0.5)
        if random.random() < 0.15:
            self.val += (random.random() - 0.5) * 3
        if random.random() < 0.03:
            self.val += (random.random() - 0.5) * (10 + 10 * dragonBoost)
        if random.random() < 0.1:
            self.delta += (random.random() - 0.5) * (0.3 + 0.2 * dragonBoost)
        if self.mode == 5:
            if random.random() < 0.5:
                self.val += (random.random() - 0.5) * 10
            if random.random() < 0.2:
                self.delta = (random.random() - 0.5) * (2 + 6 * dragonBoost)
        if self.mode == 3 and random.random() < 0.3:
            self.delta += (random.random() - 0.5) * 0.1
            self.val += (random.random() - 0.7) * 10
        if self.mode == 3 and random.random() < 0.03:
            self.mode = 4
        if self.mode == 4 and random.random() < 0.3:
            self.delta += (random.random() - 0.5) * 0.1
            self.val += (random.random() - 0.3) * 10

        if self.val > (100 + (self.env.bank_level - 1) * 3) and self.delta > 0:
            self.delta *= 0.9

        self.val += self.delta

        if self.val < 5:
            self.val += (5 - self.val) * 0.5
        if self.val < 5 and self.delta < 0:
            self.delta *= 0.95
        self.val = max(self.val, 1)

        self.vals.insert(0, self.val)
        if len(self.vals) > 65:
            self.vals.pop()

        self.dur -= 1
        if self.dur <= 0:
            self.dur = int(10 + random.random() * (690 - 200 * dragonBoost))
            if random.random() < dragonBoost and random.random() < 0.5:
                self.mode = 5
            elif random.random() < 0.7 and (self.mode == 3 or self.mode == 4):
                self.mode = 5
            else:
                # Weighted random choice as in JS choose([0,1,1,2,2,3,4,5])
                choices = [0, 1, 1, 2, 2, 3, 4, 5]
                self.mode = random.choice(choices)
