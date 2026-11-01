# LinkPast — native Zelda3 integration status

## Project identity

Work happens in the actual Zelda3 C/WebAssembly game engine. **Do not replace it with a separate custom-drawn game or fake Zelda3 canvas demo.** Original SNES maps, characters, animations, OAM tile drawing, scrolling, collisions, and combat implementation remain authoritative. User's legally extracted data stays local and is never committed.

Working branch: `feature/linkpast-native-zelda-orbit`; draft pull request #1; original `master` is preserved.

## Implemented source code (not yet Android-playtested)

- **Real native Zelda wand B attack:** The existing SNES B timing triggers a short-range Somaria-effect pulse instead of Link's sword or Fire/Ice Rod, using the game's original magic pixels and collision code. A charged release creates a three-part fan. Extra pulses use the original ancillary slot limit; 14 simulation frames (~42 px) before expiry. Native Link B still uses original sword logic.
- **Zelda-specific boomerang:** Changes native `src/ancilla.c` boomerang handling. Short outbound distance (12 frames), then 54 frames / two rotations of 12px radius; original boomerang sprite, tile checks and homing return retained. Link's throw remains original.
- **Native character switching:** Browser touch PAIR TEST and SWITCH invoke exported C methods. Pair refuses to overwrite story followers. Switch requires normal exploration, safe ground, an idle player, and nearby companion; swaps active player and follower coordinates. The original game's existing Zelda follower animator and Link OAM are reused, not redrawn in JS.
- The existing Zelda skin patch is already in `browser_patch.py` and initializes Zelda as rendered hero; switching controls which native art and primary weapon apply.
- Browser build workflow includes source-path triggers, source checks, and an eight-direction deterministic C orbit test.
- Original line endings retained in existing C files for reviewable diffs.

## Verification

- Local native C math test passed for eight directions, 54 frames, continuous entry and two revolutions.
- Source was fetched back from GitHub and key C function, browser hook and workflow markers verified; GitHub compare shows compact targeted edits.
- **A current WebAssembly build, real enemy collision playback and Android test have NOT been verified.** Connector-created commits did not cause new GitHub Actions runs to appear, so CI remains pending. Do not call this a complete game or provide a fake "play" link.

## Known gaps to address next

1. Run the native browser package workflow on the feature branch and fix any compile/link errors. Tests only check the deterministic orbit math until live validation.
2. Finish companion autonomous attack/defense AI: existing follower logic is primarily visual/pathing, not a second full combat actor.
3. Add Zelda's timed defensive ward, healing and magic economy, and rigorous balance against Link's shield and spin attack.
4. Confirm level transitions, saving/loading, follower story events, multiple enemy hits, collision walls, sprites and animation at 60 Hz.
5. Test genuine Android touch controls. Require privately extracted Zelda3 assets from a legally owned ROM; never commit protected game files.

**Do not merge draft PR #1 into master without native CI passing and in-game playtest.**
