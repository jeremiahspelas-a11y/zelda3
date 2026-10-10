# Authentic Zelda3 browser prototype

This folder hosts the **original snesrev/zelda3 C engine**, compiled with Emscripten. It is not the separate HTML mock-up that was rejected during development.

## GitHub Actions

The `Native Zelda3 browser package (no game data)` workflow:
1. Checks that no Zelda ROM, SRAM, or extracted Nintendo assets enter the public repository.
2. Applies the native sandbox SDL patch and browser-only event-loop/input bridge.
3. Compiles the actual Zelda3 C sources to JavaScript + WebAssembly.
4. Packages `index.html`, `zelda3.js`, `zelda3.wasm` for download.

## Running locally

Download the workflow artifact from GitHub Actions and unzip it. Serve the directory over HTTP (not `file://`), such as `python -m http.server 8000` on a computer, then open that address in a browser. The browser must support WebAssembly.

The page needs **`zelda3_assets.dat`** extracted from your own USA Link to the Past ROM using the upstream `assets/restool.py --extract-from-rom` procedure. The resource file is chosen on the local device at runtime. Never upload it, the ROM, or save files to this public GitHub repository. It is not extracted by this browser page.

## Current technical limitations

* The new browser build pipeline is experimental. A successful Emscripten link does **not** verify live Android gameplay.
* The native SDL practice menu uses SDL_ShowMessageBox and may need a browser-specific replacement using the same native engine state.
* This still uses the current actual Zelda3 room. A dedicated practice dungeon, game-state isolation, and playable Princess Zelda are not implemented.
* The browser path yields using Emscripten Asyncify. Frame pacing, SDL events, and audio need device testing.
* The touchscreen buttons use an exported C function to call Zelda3's native input handler; the on-screen sprites, maps, collisions, and enemies are rendered by Zelda3 itself.
* If the build fails, inspect the workflow log and fix the error. Do not substitute a JavaScript game simulation.

No ROM or extracted game resources are tracked in git or uploaded to Actions artifacts.
