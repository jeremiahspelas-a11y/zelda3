# Zelda3 native sandbox: current-room practice

This project applies native C/SDL2 changes to `snesrev/zelda3`. Original engine rendering is retained. The current scope is a practice menu in the current room, not a new map, playable Zelda, multiplayer, or isolated save state.

## Build on Linux

The installer is versioned; `src/main.c` remains clean upstream in Git so changes are reviewable and compatibility is checked before installation. Apply it once per clean checkout.

```sh
sudo apt-get install build-essential libsdl2-dev python3
git config core.hooksPath .githooks
python3 scripts/check_no_game_assets.py
python3 test_install.py
python3 install.py . --dry-run
python3 install.py .
make zelda3 -j2
make -f sandbox.mk test-native-sandbox
```

Use `make zelda3`, not bare `make`, for the source-only build. No ROM is needed for any command above. The installer leaves an ignored `src/main.c.before_native_sandbox_phase3` backup and rejects double installation or incompatible source anchors. To replace the patch, first preserve any personal changes and restore a clean upstream `src/main.c`.

## Controls

- Mapped START (Enter by default) or F11 opens the native SDL menu.
- **Original START / inventory** delivers one START frame, including when invoked through F11.
- **Practice in current original room** mutes all audio and blocks save-state commands while practice is active.
- **Leave practice** restores the previous mixer volume. Volume shortcuts do not unmute active practice.
- **Cancel** resumes without a practice-state change.
- Default F1–F10 loading shortcuts are retained.

**Practice does not protect the game's SRAM writes or undo progress.** Use disposable saves. Native desktop dialog appearance, controller behavior, actual inventory behavior and gameplay still need a hands-on test with locally extracted game assets.

## GitHub Actions

`Build Zelda3 native sandbox (code only)` runs on pushes, pull requests and manual dispatch. It checks the Git index for common ROM/asset/save files, tests the installer, applies the patch, compiles the engine and runs native host behavior tests. Its artifact contains only `zelda3`, `zelda3.ini`, `LICENSE.txt` and this guide. It never extracts assets or requests a ROM/ROM secret.

The native tests use the real patched host code with spies for the dialog/window title and game save/audio I/O. They validate menu results, mute/restore, volume changes, save command blocking, buffer muting, START queuing, cancel/error and reentry handling. They do not emulate gameplay or test a real desktop dialog.

## ROM and assets stay local

Do not commit or upload a ROM, extracted `zelda3_assets.dat`, personal saves, or archives containing them. `.gitignore`, the optional pre-commit hook, and the CI check cover common game-data paths. Upstream's existing `saves/ref` demonstration snapshots and `assets/palette_usage.bin` remain part of upstream source history.

To play, follow upstream `BUILDING.md` and `assets/restool.py` locally using your compatible USA ROM. Keep extracted data on your own machine. The uploaded Linux executable requires `zelda3_assets.dat` next to it. This is a native Linux build, not an Android or browser build.

## Verified baseline

Upstream: https://github.com/snesrev/zelda3

Pinned source tested: `45a149d8b4bb8098f53d1009f76e76e7d8b79bbf`.

Local validation: Ubuntu 24.04 x86-64, GCC 13.3.0, SDL2 2.30.0. Full engine compilation and linking passed with `-O2 -Werror`; four installer tests and the native host test executable passed. No ROM was downloaded or used. GitHub Actions status is separate and must be checked on the remote repository.
