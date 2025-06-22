import random
from dataclasses import dataclass
from typing import Literal, get_args

StockMode = Literal[
    "Stable",
    "Slow Rise",
    "Slow Fall",
    "Fast Rise",
    "Fast Fall",
    "Chaotic",
]

FastMode = Literal["Fast Rise", "Fast Fall", "Chaotic"]


@dataclass
class Config:
    """Configuration parameters for the stock market simulation."""

    fluctuation_probability_primary: float = 0.15
    fluctuation_range_primary: float = 3.0
    fluctuation_probability_secondary: float = 0.03
    fluctuation_range_secondary: float = 10.0
    fluctuation_range_secondary_dragon_boost: float = 10.0
    fluctuation_probability_tertiary: float = 0.1
    fluctuation_range_tertiary: float = 0.3
    fluctuation_range_tertiary_dragon_boost: float = 0.2
    chaotic_probability_with_dragon_boost: float = 0.5
    chaotic_probability_after_fast_mode: float = 0.7
    duration_min: int = 10
    duration_max: int = 690
    duration_max_dragon_boost: int = 200
    high_stock_value_threshold: float = 100.0
    high_stock_value_dampening: float = 0.9
    high_stock_value_bank_level_factor: float = 3.0
    low_stock_value_threshold: float = 5.0
    low_stock_value_delta_dampening: float = 0.95
    min_stock_value: float = 1.0
    fast_mode_tick_chaotic_probability_primary: float = 0.5
    fast_mode_tick_chaotic_probability_secondary: float = 0.2
    fast_mode_tick_fast_rise_probability: float = 0.3
    fast_mode_tick_fast_rise_to_fast_fall_probability: float = 0.03
    fast_mode_tick_fast_fall_probability: float = 0.3


@dataclass
class GameEnvironment:
    """Represents the game environment (user progress) for the stock market simulation."""

    bank_level: int
    num_brokers: int
    dragon_boost: float


@dataclass
class Good:
    """Represents a good in the stock market."""

    stock_id: int
    stock_value: float
    stock_delta: float
    mode: StockMode
    remaining_mode_duration: int


DEFAULT_CONFIG = Config()
STOCK_MODES: tuple[StockMode] = get_args(StockMode)


def resting_stock_value(stock_id: int, bank_level: int) -> float:
    """Returns the resting stock_value of the good.

    Returns:
        float: The resting stock_value of the good.

    """
    return 10.0 + 10.0 * stock_id + (bank_level - 1.0)


def tick(
    stock_value: float,
    stock_delta: float,
    stock_mode: StockMode,
    remaining_mode_duration: int,
    resting_stock_value: float,
    bank_level: int,
    global_delta: float,
    instant_mode_change_probability: float,
    dragon_boost: float,
) -> tuple[float, float, StockMode, int]:
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

    stock_value, stock_delta = _apply_fluctuations(
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
        stock_value,
        stock_delta,
    )

    remaining_mode_duration -= 1
    if remaining_mode_duration <= 0:
        stock_mode, remaining_mode_duration = _update_expired_mode(
            stock_mode,
            dragon_boost,
        )

    return stock_value, stock_delta, stock_mode, remaining_mode_duration


def _apply_mode_tick(
    stock_value: float,
    stock_delta: float,
    resting_stock_value: float,
    mode: StockMode,
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


def _apply_fluctuations(
    stock_value: float,
    stock_delta: float,
    dragon_boost: float,
    config: Config = DEFAULT_CONFIG,
) -> tuple[float, float]:
    stock_value += (random.random() - 0.5) ** 2 * 3
    stock_delta += 0.1 * (random.random() - 0.5)
    if random.random() < config.fluctuation_probability_primary:
        stock_value += (random.random() - 0.5) * config.fluctuation_range_primary
    if random.random() < config.fluctuation_probability_secondary:
        stock_value += (random.random() - 0.5) * (
            config.fluctuation_range_secondary
            + config.fluctuation_range_secondary_dragon_boost * dragon_boost
        )
    if random.random() < config.fluctuation_probability_tertiary:
        stock_delta += (random.random() - 0.5) * (
            config.fluctuation_range_tertiary
            + config.fluctuation_range_tertiary_dragon_boost * dragon_boost
        )

    return stock_value, stock_delta


def _apply_fast_mode_tick(
    stock_value: float,
    stock_delta: float,
    mode: StockMode,
    dragon_boost: float,
    config: Config = DEFAULT_CONFIG,
) -> tuple[
    float,
    float,
    StockMode,
]:
    if mode == "Chaotic":
        if random.random() < config.fast_mode_tick_chaotic_probability_primary:
            stock_value += (random.random() - 0.5) * 10
        if random.random() < config.fast_mode_tick_chaotic_probability_secondary:
            stock_delta = (random.random() - 0.5) * (2 + 6 * dragon_boost)
    if (
        mode == "Fast Rise"
        and random.random() < config.fast_mode_tick_fast_rise_probability
    ):
        stock_delta += (random.random() - 0.5) * 0.1
        stock_value += (random.random() - 0.7) * 10
    if (
        mode == "Fast Rise"
        and random.random() < config.fast_mode_tick_fast_rise_to_fast_fall_probability
    ):
        mode = "Fast Fall"
    if (
        mode == "Fast Fall"
        and random.random() < config.fast_mode_tick_fast_fall_probability
    ):
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


def _update_expired_mode(
    mode: StockMode,
    dragon_boost: float,
    config: Config = DEFAULT_CONFIG,
) -> tuple[StockMode, int]:
    duration = int(
        config.duration_min
        + random.random()
        * (config.duration_max - 200 * config.duration_max_dragon_boost),
    )

    # Higher Chance of Chaotic mode if dragon_boost is high
    # or if the mode was in Fast Rise or Fast Fall.
    if (
        random.random() < dragon_boost
        and random.random() < config.chaotic_probability_with_dragon_boost
    ) or (
        random.random() < config.chaotic_probability_after_fast_mode
        and (mode in ("Fast Rise", "Fast Fall"))
    ):
        mode_index = STOCK_MODES.index("Chaotic")
    else:
        # Weighted random choice as in JS choose([0,1,1,2,2,3,4,5])
        choices = [0, 1, 1, 2, 2, 3, 4, 5]
        mode_index = random.choice(choices)

    return STOCK_MODES[mode_index], duration


def _apply_high_stock_value_dampening(
    stock_value: float,
    stock_delta: float,
    bank_level: int,
    config: Config = DEFAULT_CONFIG,
) -> tuple[float, float]:
    if (
        stock_value
        > (
            config.high_stock_value_threshold
            # bank_level starts at 1, so we subtract 1 to make it zero-based
            + (bank_level - 1) * config.high_stock_value_bank_level_factor
        )
        and stock_delta > 0
    ):
        stock_delta *= config.high_stock_value_dampening

    return stock_value, stock_delta


def _apply_low_stock_value_dampening(
    stock_value: float,
    stock_delta: float,
    config: Config = DEFAULT_CONFIG,
) -> tuple[float, float]:
    if stock_value < config.low_stock_value_threshold:
        stock_value += (config.low_stock_value_threshold - stock_value) * 0.5
    if stock_value < config.low_stock_value_threshold and stock_delta < 0:
        stock_delta *= config.low_stock_value_delta_dampening
    stock_value = max(stock_value, config.min_stock_value)

    return stock_value, stock_delta
