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

    def resting_value(self) -> float:
        """Returns the resting value of the good.

        Returns:
            float: The resting value of the good.

        """
        return 10 + 10 * self.id + (self.env.bank_level - 1)

    def tick(self) -> None:
        self.delta = self.delta * 0.97

        if self.mode == 0:
            self.delta *= 0.95
            self.delta += 0.05 * (random.random() - 0.5)
