from dataclasses import dataclass
import random
from typing import Literal, get_args

StockMode = Literal[
    "Stable", "Slow Rise", "Slow Fall", "Fast Rise", "Fast Fall", "Chaotic"
]

FastMode = Literal["Fast Rise", "Fast Fall", "Chaotic"]


stock_modes: tuple[StockMode] = get_args(StockMode)


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
    stock_mode: StockMode = "Stable"
    remaining_mode_duration: int = 0
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

        self.val, self.delta = _apply_mode_tick(
            self.val,
            self.delta,
            self.resting_value,
            self.stock_mode,
        )

        self.val, self.delta, self.remaining_mode_duration = _maybe_instant_mode_change(
            globD, globP, self.val, self.delta, self.remaining_mode_duration
        )

        self.val, self.delta = _apply_fluctioations(
            self.val,
            self.delta,
            dragonBoost,
        )

        self.val, self.delta, self.mode = _apply_fast_mode_tick(
            self.val,
            self.delta,
            self.stock_mode,
            dragonBoost,
        )

        self.val, self.delta = _apply_high_value_dampening(
            self.val,
            self.delta,
            self.env.bank_level,
        )

        self.val += self.delta

        self.val, self.delta = _apply_low_value_dampening(self.val, self.delta)

        self.remaining_mode_duration -= 1
        if self.remaining_mode_duration <= 0:
            self.mode, self.remaining_mode_duration = _update_expired_mode(
                self.stock_mode, dragonBoost
            )


def _apply_mode_tick(
    value: float, delta: float, resting_value: float, mode: StockMode
) -> tuple[float, float]:
    """Applies the mode-specific tick adjustments to the value and delta."""

    if mode == "Stable":
        delta *= 0.95
        delta += 0.05 * (random.random() - 0.5)
    elif mode == "Slow Fall":
        delta *= 0.99
        delta -= 0.05 * (random.random() - 0.1)
    elif mode == "Fast Rise":
        delta += 0.15 * (random.random() - 0.1)
        value += random.random() * 5
    elif mode == "Fast Fall":
        delta -= 0.15 * (random.random() - 0.1)
        value -= random.random()
    elif mode == "Chaotic":
        delta += 0.3 * (random.random() - 0.5)

    value += (resting_value - value) * 0.01

    return value, delta


def _apply_fluctioations(
    value: float,
    delta: float,
    dragonBoost: float,
) -> tuple[float, float]:
    value += (random.random() - 0.5) ** 2 * 3
    delta += 0.1 * (random.random() - 0.5)
    if random.random() < 0.15:
        value += (random.random() - 0.5) * 3
    if random.random() < 0.03:
        value += (random.random() - 0.5) * (10 + 10 * dragonBoost)
    if random.random() < 0.1:
        delta += (random.random() - 0.5) * (0.3 + 0.2 * dragonBoost)

    return value, delta


def _apply_fast_mode_tick(
    value: float,
    delta: float,
    mode: StockMode,
    dragonBoost: float,
) -> tuple[
    float,
    float,
    StockMode,
]:
    if mode == "Chaotic":
        if random.random() < 0.5:
            value += (random.random() - 0.5) * 10
        if random.random() < 0.2:
            delta = (random.random() - 0.5) * (2 + 6 * dragonBoost)
    if mode == "Fast Rise" and random.random() < 0.3:
        delta += (random.random() - 0.5) * 0.1
        value += (random.random() - 0.7) * 10
    if mode == "Fast Rise" and random.random() < 0.03:
        mode = "Fast Fall"
    if mode == "Fast Rise" and random.random() < 0.3:
        delta += (random.random() - 0.5) * 0.1
        value += (random.random() - 0.3) * 10

    return value, delta, mode


def _maybe_instant_mode_change(globD: float, globP: float, value: float, delta: float, remaining_mode_duration: int) -> tuple[float , float, int]
    if globD != 0 and random.random() < globP:
        value -= (1 + delta * random.random() ** 3 * 7) * globD
        value -= globD * (1 + random.random() ** 3 * 7)
        delta += globD * (1 + random.random() * 4)
        remaining_mode_duration = 0

    return value, delta, remaining_mode_duration


def _update_expired_mode(mode: StockMode, dragonBoost: float) -> tuple[StockMode, int]:
    duration = int(10 + random.random() * (690 - 200 * dragonBoost))
    if random.random() < dragonBoost and random.random() < 0.5:
        mode_index = 5
    elif random.random() < 0.7 and (mode == 3 or mode == 4):
        mode_index = 5
    else:
        # Weighted random choice as in JS choose([0,1,1,2,2,3,4,5])
        choices = [0, 1, 1, 2, 2, 3, 4, 5]
        mode_index = random.choice(choices)

    return stock_modes[mode_index], duration


def _apply_high_value_dampening(
    value: float, delta: float, bank_level: int, threshold: float = 100.0
) -> tuple[float, float]:
    if value > (100 + (bank_level - 1) * 3) and delta > 0:
        delta *= 0.9

    return value, delta


def _apply_low_value_dampening(
    value: float, delta: float, threshold: float = 5.0
) -> tuple[float, float]:
    if value < threshold:
        value += (threshold - value) * 0.5
    if value < threshold and delta < 0:
        delta *= 0.95
    value = max(value, 1)

    return value, delta
