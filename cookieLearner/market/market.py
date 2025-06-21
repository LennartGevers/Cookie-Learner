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
    dragon_boost: float

@dataclass
class Good:
    id: int
    value: float
    delta: float
    mode: StockMode
    remaining_mode_duration: int


def _resting_value(id: int, bank_level: int) -> float:
    """Returns the resting value of the good.

    Returns:
        float: The resting value of the good.

    """
    return 10.0 + 10.0 * id + (bank_level - 1.0)

def _tick(value, delta, resting_value, stock_mode: StockMode, remaining_mode_duration: int, bank_level: int, globD: float, globP: float, dragon_boost: float) -> None:
    delta = delta * 0.97 + 0.01 * dragon_boost

    value, delta = _apply_mode_tick(
        value,
        delta,
        resting_value,
        stock_mode,
    )

    value, delta, remaining_mode_duration = _maybe_instant_mode_change(
        globD, globP, value, delta, remaining_mode_duration
    )

    value, delta = _apply_fluctioations(
        value,
        delta,
        dragon_boost,
    )

    value, delta, stock_mode = _apply_fast_mode_tick(
        value,
        delta,
        stock_mode,
        dragon_boost,
    )

    value, delta = _apply_high_value_dampening(
        value,
        delta,
        bank_level,
    )

    value += delta

    value, delta = _apply_low_value_dampening(value, delta)

    remaining_mode_duration -= 1
    if remaining_mode_duration <= 0:
        stock_mode, remaining_mode_duration = _update_expired_mode(
            stock_mode, dragon_boost
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
    dragon_boost: float,
) -> tuple[float, float]:
    value += (random.random() - 0.5) ** 2 * 3
    delta += 0.1 * (random.random() - 0.5)
    if random.random() < 0.15:
        value += (random.random() - 0.5) * 3
    if random.random() < 0.03:
        value += (random.random() - 0.5) * (10 + 10 * dragon_boost)
    if random.random() < 0.1:
        delta += (random.random() - 0.5) * (0.3 + 0.2 * dragon_boost)

    return value, delta


def _apply_fast_mode_tick(
    value: float,
    delta: float,
    mode: StockMode,
    dragon_boost: float,
) -> tuple[
    float,
    float,
    StockMode,
]:
    if mode == "Chaotic":
        if random.random() < 0.5:
            value += (random.random() - 0.5) * 10
        if random.random() < 0.2:
            delta = (random.random() - 0.5) * (2 + 6 * dragon_boost)
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


def _update_expired_mode(mode: StockMode, dragon_boost: float) -> tuple[StockMode, int]:
    duration = int(10 + random.random() * (690 - 200 * dragon_boost))
    if random.random() < dragon_boost and random.random() < 0.5:
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
