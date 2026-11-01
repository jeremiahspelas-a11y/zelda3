# LinkPast — authentic Zelda3 native orbit patch

This branch modifies the **real** `src/ancilla.c` boomerang projectile routine. It uses the existing Zelda3 tiles, original pixel sprites, object drawing, collision routines, sound and boomerang return logic. No separate JavaScript game, imitation graphics or canvas fighting scene has been substituted.

## Implementation in this branch

- Opt-in experimental orbit trajectory in the original C engine, behind `LinkPast_SetZeldaOrbitBoomerangEnabled(bool)`.
- Normal gameplay remains unchanged until a character controller explicitly enables this for Zelda; no permanent change to Link's sword/shield.
- Short outbound flight (12 simulation frames), then a 54-frame (0.9 seconds at 60fps), 12-pixel-radius orbit completing two revolutions, then normal homing return.
- Original SNES boomerang sprite and drawing unchanged; enemies can be checked throughout the sweep; walls interrupt the orbit and begin return.
- Orbital entry has no position teleport, regardless of throw direction.
- Pure integer math in `src/linkpast_orbit.h`, deterministic tests for all eight directions in `tests/test_linkpast_orbit.c`.

## Exact current status

This is a **native source integration / test branch**, **not yet a playable two-character build**. The existing repository currently includes an experimental Zelda follower, not two separately playable combatants. The new setter is disabled by default until that character system exists. A full Emscripten/Android compile and in-game collision test have not yet run. Do not present this as a completed Link-and-Zelda combat build.

## Next native tasks

1. Implement independent playable Zelda in the existing Zelda3 state machine, using existing extracted sprite data and original rendering.
2. Tie hero switch state to the orbit enable setter; only the currently equipped boomerang holder can throw it.
3. Implement Zelda's wand as a balanced primary weapon using native Zelda3 attack states, OAM sprites, collision, recovery and a timed ward. Link retains sword plus shield.
4. Build native browser artifacts through `.github/workflows/browser-package.yml` and test on Android.
5. Test multiple enemies, narrow passages, walls, boomerang interception, return catch, pause/reload and 60fps consistency.

Run orbital math tests: `cc -std=c11 -Wall -Wextra -Werror tests/test_linkpast_orbit.c -o /tmp/test_linkpast_orbit && /tmp/test_linkpast_orbit`.

Do **not** commit ROMs, extracted Nintendo game assets or proprietary artwork to this public repository. The authentic native game requires resources extracted locally from a legally held game copy.
