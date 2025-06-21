# Stock simulation

Implement stock simulation script (minigameMarket.js) with jax.

- [ ] Define current `dataclass` instances as `jax.pytree` objects.
- [ ] Write conditional logic of `_tick` (mode and random events) as `jax`-compliant expressions

    For instance, use `jax.lax.select` or `jax.lax.switch`.
- [ ] Compile all steps with `jax`
- [ ] Run timeseries iteration with `jax.lax.scan`