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
    stock_value: float
    stock_delta: float
    mode: StockMode
    remaining_mode_duration: int


def _resting_stock_value(id: int, bank_level: int) -> float:
    """Returns the resting stock_value of the good.

    Returns:
        float: The resting stock_value of the good.

    """
    return 10.0 + 10.0 * id + (bank_level - 1.0)


def _tick(
    stock_value,
    stock_delta,
    resting_stock_value,
    stock_mode: StockMode,
    remaining_mode_duration: int,
    bank_level: int,
    global_delta: float,
    instant_mode_change_probability: float,
    dragon_boost: float,
) -> None:
    stock_delta = stock_delta * 0.97 + 0.01 * dragon_boost

    stock_value, stock_delta = _apply_mode_tick(
        stock_value,
        stock_delta,
        resting_stock_value,
        stock_mode,
    )

    stock_value, stock_delta, remaining_mode_duration = _maybe_instant_mode_change(
        global_delta,
        instant_mode_change_probability,
        stock_value,
        stock_delta,
        remaining_mode_duration,
    )

    stock_value, stock_delta = _apply_fluctioations(
        stock_value,
        stock_delta,
        dragon_boost,
    )

    stock_value, stock_delta, stock_mode = _apply_fast_mode_tick(
        stock_value,
        stock_delta,
        stock_mode,
        dragon_boost,
    )

    stock_value, stock_delta = _apply_high_stock_value_dampening(
        stock_value,
        stock_delta,
        bank_level,
    )

    stock_value += stock_delta

    stock_value, stock_delta = _apply_low_stock_value_dampening(
        stock_value, stock_delta
    )

    remaining_mode_duration -= 1
    if remaining_mode_duration <= 0:
        stock_mode, remaining_mode_duration = _update_expired_mode(
            stock_mode, dragon_boost
        )


def _apply_mode_tick(
    stock_value: float, stock_delta: float, resting_stock_value: float, mode: StockMode
) -> tuple[float, float]:
    """Applies the mode-specific tick adjustments to the stock_value and stock_delta."""

    if mode == "Stable":
        stock_delta *= 0.95
        stock_delta += 0.05 * (random.random() - 0.5)
    elif mode == "Slow Fall":
        stock_delta *= 0.99
        stock_delta -= 0.05 * (random.random() - 0.1)
    elif mode == "Fast Rise":
        stock_delta += 0.15 * (random.random() - 0.1)
        stock_value += random.random() * 5
    elif mode == "Fast Fall":
        stock_delta -= 0.15 * (random.random() - 0.1)
        stock_value -= random.random()
    elif mode == "Chaotic":
        stock_delta += 0.3 * (random.random() - 0.5)

    stock_value += (resting_stock_value - stock_value) * 0.01

    return stock_value, stock_delta


def _apply_fluctioations(
    stock_value: float,
    stock_delta: float,
    dragon_boost: float,
) -> tuple[float, float]:
    stock_value += (random.random() - 0.5) ** 2 * 3
    stock_delta += 0.1 * (random.random() - 0.5)
    if random.random() < 0.15:
        stock_value += (random.random() - 0.5) * 3
    if random.random() < 0.03:
        stock_value += (random.random() - 0.5) * (10 + 10 * dragon_boost)
    if random.random() < 0.1:
        stock_delta += (random.random() - 0.5) * (0.3 + 0.2 * dragon_boost)

    return stock_value, stock_delta


def _apply_fast_mode_tick(
    stock_value: float,
    stock_delta: float,
    mode: StockMode,
    dragon_boost: float,
) -> tuple[
    float,
    float,
    StockMode,
]:
    if mode == "Chaotic":
        if random.random() < 0.5:
            stock_value += (random.random() - 0.5) * 10
        if random.random() < 0.2:
            stock_delta = (random.random() - 0.5) * (2 + 6 * dragon_boost)
    if mode == "Fast Rise" and random.random() < 0.3:
        stock_delta += (random.random() - 0.5) * 0.1
        stock_value += (random.random() - 0.7) * 10
    if mode == "Fast Rise" and random.random() < 0.03:
        mode = "Fast Fall"
    if mode == "Fast Rise" and random.random() < 0.3:
        stock_delta += (random.random() - 0.5) * 0.1
        stock_value += (random.random() - 0.3) * 10

    return stock_value, stock_delta, mode


def _maybe_instant_mode_change(
    global_delta: float,
    instant_mode_change_probability: float,
    stock_value: float,
    stock_delta: float,
    remaining_mode_duration: int,
) -> tuple[float, float, int]:
    if global_delta != 0 and random.random() < instant_mode_change_probability:
        stock_value -= (1 + stock_delta * random.random() ** 3 * 7) * global_delta
        stock_value -= global_delta * (1 + random.random() ** 3 * 7)
        stock_delta += global_delta * (1 + random.random() * 4)
        remaining_mode_duration = 0

    return stock_value, stock_delta, remaining_mode_duration


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


def _apply_high_stock_value_dampening(
    stock_value: float, stock_delta: float, bank_level: int, threshold: float = 100.0
) -> tuple[float, float]:
    if stock_value > (100 + (bank_level - 1) * 3) and stock_delta > 0:
        stock_delta *= 0.9

    return stock_value, stock_delta


def _apply_low_stock_value_dampening(
    stock_value: float, stock_delta: float, threshold: float = 5.0
) -> tuple[float, float]:
    if stock_value < threshold:
        stock_value += (threshold - stock_value) * 0.5
    if stock_value < threshold and stock_delta < 0:
        stock_delta *= 0.95
    stock_value = max(stock_value, 1)

    return stock_value, stock_delta
