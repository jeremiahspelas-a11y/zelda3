# LinkPast — native Zelda3 integration checkpoint (2026-11-01)

## Canonical project
**Actual** `jeremiahspelas-a11y/zelda3` C engine + original SNES game graphics, OAM, maps, enemy systems, sounds, and scrolling. Do not deliver a separately drawn HTML imitation as though it were the game.

- Branch: `feature/linkpast-native-zelda-orbit`
- Draft PR: https://github.com/jeremiahspelas-a11y/zelda3/pull/1
- Baseline: `master` — no merge until full native compile and Android runtime checks pass.
- Original licensed ROM and extracted Nintendo assets stay **private/local**.

## Native source integrated (experimental)

1. `src/linkpast_orbit.h`, `src/ancilla.c`: Zelda's boomerang uses original ancilla OAM sprite, hitbox, wall collision and homing return. Shorter outbound (12 engine frames), 54-frame orbit at 12px radius, two revolutions; then returns. Link's boomerang logic remains unchanged while the Zelda mode is disabled.
2. `src/ancilla.c`, `src/player.c`: Zelda's basic B wand uses original **Somaria** effect art and collision, close-range 14-tick lifetime, not the original Fire/Ice Rod. Held B can reach a separate 48-frame charge to release three lateral magic bursts. Zelda's charge no longer calls Link's sword-spin or sword-hit logic. The wand projectile lifetime pauses with native submodule state; newly allocated ancilla slots discard stale wand TTL.
3. `src/sprite.c`: Zelda cannot inherit Link's hidden shield deflection or invisible sword attack just because the single native player state is reused. Link retains original sword, spin and shield.
4. `browser_patch.py`, `browser/index.html`: Android-facing native C/Wasm PAIR and SWITCH button bridge. Switch requires a paired follower, safe idle state and nearby companion; refuses switches while boomerang is in flight. Native Zelda follower rendering + native Link OAM are reused; no JavaScript replacement world.
5. `.github/workflows/browser-package.yml`: native browser CI configured with source path triggers, C orbit test, Python structural guards and Emscripten package steps.
6. `tests/test_linkpast_orbit.c` + `tests/test_linkpast_native_guards.py`: regression coverage. Local independent C orbit geometry test was **executed**, including GCC `-fsanitize=undefined`, and passed 8 directions. Static source structure checks were also evaluated on fetched branch files.

## Validation status / limits

**Verified:** GitHub branch and PR reflect targeted native source modifications; baseline preserved. A local standalone C test of orbit math compiled and passed (normal and UBSan). The new branch contains test scripts; source-level structural assertions were examined.

**Not yet verified:** an Emscripten compile of this branch, original Zelda3 live gameplay, native enemy damage calibration, mobile touch latency, audiovisual effects or two-character combat in a real room. On this branch's newest GitHub commits the API returned zero Actions check runs, so workflow success is **not** established. Do not claim a playable native binary, Android live URL, or full balanced combat until tests run.

## 2026-11-01 continued integration — native party vitals and companion orders

This work is committed on the **same** draft PR #1, not merged into master.

- `src/linkpast_party.h`: independent Link/Zelda HP and MP snapshots; pairing copies the *current* vitals to both, not a free heal; switching saves the active hero's HP/MP and restores the target hero's previously saved values, clamped to the game's current heart capacity; no ROM, sprite, map or persistent save-format changes.
- `tests/test_linkpast_party.c`: invalid-target guards, no initial healing exploit, health/magic persistence, clamping, stop/restart transitions. An equivalent local C test harness was compiled with GCC `-Wall -Wextra -Werror -fsanitize=undefined` and **passed**. This is a standalone unit test, not an Emscripten integration success.
- `browser_patch.py`: native `ZeldaBrowserSwitchCharacter` now checks for pending heal/magic refill, saves/loads vitals, updates game HUD with `Hud_Rebuild()`, and keeps the current hero active in the original engine. New `ZeldaBrowserSetCompanionHold` C export toggles a real engine follower behavior.
- `src/tagalong.c/.h`: `LinkPast_SetCompanionHold` tells the original Zelda follower to remain stationary after its route-history capture, while keeping original sprite rendering. FOLLOW resumes the game's own follower movement; **this does not yet give the companion independent combat AI**.
- `browser/index.html`: native Android PAIR, SWITCH, HOLD/FOLLOW and LEAVE buttons; explicitly restores button state on exit. No separately rendered combat scene or fake sprites.
- `.github/workflows/browser-package.yml`, `tests/test_linkpast_native_guards.py`: C unit test and structural smoke checks are incorporated into CI source definitions. No current Actions result was accessible; **a native WebAssembly build has not been verified**.
- `master` remains untouched. Room/dungeon boundary switching, autonomous teammate combat, wand ward/healing and persistent dual-character save data are still unimplemented.

**Safety limit:** the switching routine currently requires the heroes to be within 32 in-game pixels so it cannot blindly switch to an unloaded map region. HOLD can leave a hero farther away, but switching back requires getting near the companion until safe cross-room switching is implemented.

## Remaining non-negotiable requirements

- Fully **autonomous** opponent-targeting and sword/wand attacks by the inactive hero, with follow/stay/guard commands: current tagalong primarily follows and renders, **not combat AI**.
- Zelda timed ward and healing with an explicit magic economy; distinct Link shield vs Zelda ward.
- Separate per-hero health, magic, damage and equipment ownership. The legacy inventory is still shared; the one equipped boomerang must be allocated exclusively to one hero.
- Validate player animation sprite bank changes, story follower conflicts, dungeon transitions, save/restore, boss/edge cases and simultaneous attacks.
- Build native Wasm and physically verify on Android using the user's privately extracted Zelda3 game resources.

## Required next execution

1. Launch `Native Zelda3 browser package (no game data)` Actions workflow on the feature branch; inspect every compile/test log. Fix failures on branch only.
2. After successful compile, locally load original game resources, enter a disposable save, test wand+charge+orbit+switch against original enemies, tile collisions, shield and sprite rendering.
3. Only then implement robust autonomous companion attack state and keep the same code/data/rendering.
4. Preserve a known-good rollback; **do not merge PR #1 or archive source assets** before real playtesting.

Command for the standalone C path test:

```sh
cc -std=c11 -O2 -Wall -Wextra -Werror -fsanitize=undefined -fno-sanitize-recover=all tests/test_linkpast_orbit.c -o /tmp/linkpast-orbit-test
/tmp/linkpast-orbit-test
python3 tests/test_linkpast_native_guards.py
```
