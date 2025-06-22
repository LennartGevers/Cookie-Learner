# Stock simulation

## Implement stock simulation script (minigameMarket.js)

- [X] Convert .js to .py code

- [X] Refactor code into logical steps (see https://cookieclicker.wiki.gg/wiki/Stock_Market)

- [X] Namespace enhancements
    - [X] Use Enums for modes, 
    - [X] use more expressive variale names.

- [X] Express code as pure functions

# Implement simulations with jax

- [ ] Define current `dataclass` instances as `jax.pytree` objects.

- [ ] Write conditional logic of `_tick` (mode and random events) as `jax`-compliant expressions

    For instance, use `jax.lax.select` or `jax.lax.switch`.
- [ ] Compile all steps with `jax`

- [ ] Run timeseries iteration with `jax.lax.scan`