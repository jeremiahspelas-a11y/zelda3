#!/usr/bin/env python3
"""Install a conservative SDL-host native sandbox menu into a clean Zelda3 checkout.

This works on snesrev/zelda3's C host input path, not the SNES ROM.
It does NOT create an isolated sandbox scene or a second hero.
"""
from pathlib import Path
import argparse
import sys

MARK = '/* ZELDA3_NATIVE_SANDBOX_PHASE3 */'


def replace_exact(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f'Expected exactly one source anchor: {old[:90]!r}; found {source.count(old)}')
    return source.replace(old, new, 1)


def transform(source):
    if MARK in source:
        raise ValueError('Phase 3 is already installed')
    if 'ZELDA3_NATIVE_SANDBOX_PHASE2' in source or 'COOP_NATIVE_SANDBOX_PHASE1' in source:
        raise ValueError('Restore a clean upstream main.c before installing Phase 3')
    code = r'''/* ZELDA3_NATIVE_SANDBOX_PHASE3 */
/* SDL host menu -- all scene pixels are still rendered by the original Zelda3 engine.
 * This is CURRENT-ROOM PRACTICE ONLY; it is not a separate safe save-state. */
static bool g_native_sandbox_active;
static bool g_native_sandbox_menu_open;
static bool g_native_sandbox_start_pending;
static SDL_mutex *g_audio_mutex;
static int g_native_sandbox_saved_volume = SDL_MIX_MAXVOLUME;
static bool NativeSandboxShowMenu(void);

static void NativeSandboxSetActive(bool enabled) {
  if (g_native_sandbox_active == enabled) return;
  SDL_LockMutex(g_audio_mutex);
  if (enabled) {
    g_native_sandbox_saved_volume = g_sdl_audio_mixer_volume;
    g_sdl_audio_mixer_volume = 0;
  } else {
    g_sdl_audio_mixer_volume = g_native_sandbox_saved_volume;
  }
  g_native_sandbox_active = enabled;
  SDL_UnlockMutex(g_audio_mutex);
  SDL_SetWindowTitle(g_window, enabled ? "Zelda3 | PRACTICE - CURRENT ROOM" : kWindowTitle);
  fprintf(stderr, "[native sandbox] %s - current original room; NO snapshot isolation.\n",
          enabled ? "entered" : "left");
}

/* Return true only if user explicitly chose the original START action. */
static bool NativeSandboxShowMenu(void) {
  if (g_native_sandbox_menu_open) return false;
  const SDL_MessageBoxButtonData buttons[] = {
    { SDL_MESSAGEBOX_BUTTON_RETURNKEY_DEFAULT, 0, "Original START / inventory" },
    { 0, 1, "Practice in current original room" },
    { 0, 2, "Leave practice" },
    { SDL_MESSAGEBOX_BUTTON_ESCAPEKEY_DEFAULT, 3, "Cancel" },
  };
  const SDL_MessageBoxData data = {
    SDL_MESSAGEBOX_INFORMATION, g_window, "A Link to the Past - Native practice menu",
    "This uses Zelda3's ORIGINAL room, tiles, enemies and animation.\n"
    "Practice temporarily mutes all audio (including effects).\n"
    "This is NOT isolated: game state may change! Use a disposable save.\n"
    "Choose Original START to open the normal inventory.",
    4, buttons, NULL
  };
  int choice = -1;
  g_native_sandbox_menu_open = true;
  int ok = SDL_ShowMessageBox(&data, &choice);
  g_native_sandbox_menu_open = false;
  if (ok != 0) {
    fprintf(stderr, "[native sandbox] SDL dialog: %s\n", SDL_GetError());
    return false;
  }
  if (choice == 1) NativeSandboxSetActive(true);
  if (choice == 2) NativeSandboxSetActive(false);
  return choice == 0;
}
'''
    source = replace_exact(source,
        'static SDL_mutex *g_audio_mutex;\n', '')
    source = replace_exact(source,
        'static int g_sdl_audio_mixer_volume = SDL_MIX_MAXVOLUME;',
        'static int g_sdl_audio_mixer_volume = SDL_MIX_MAXVOLUME;\n' + code)
    # Intercept the actual mapped START command. This handles both keyboards and
    # SDL controllers regardless of the configured key bindings.
    source = replace_exact(source,
        'static void HandleCommand(uint32 j, bool pressed) {\n  if (j <= kKeys_Controls_Last) {',
        '''static void HandleCommand(uint32 j, bool pressed) {
  /* kKeys_Controls+5 is START in upstream config.c controls order. */
  if (j == kKeys_Controls + 5 && pressed && !g_native_sandbox_menu_open) {
    g_native_sandbox_start_pending |= NativeSandboxShowMenu();
    return;
  }
  if (j <= kKeys_Controls_Last) {''')
    # Preserve default F10 load-state mapping; use F11 as a secondary menu hotkey.
    source = replace_exact(source,
        '      case SDL_KEYDOWN:\n        HandleInput(event.key.keysym.sym, event.key.keysym.mod, true);',
        '''      case SDL_KEYDOWN:
        if (event.key.keysym.sym == SDLK_F11) {
          if (!event.key.repeat)
            g_native_sandbox_start_pending |= NativeSandboxShowMenu();
          break;
        }
        if (event.key.repeat &&
            FindCmdForSdlKey(event.key.keysym.sym, event.key.keysym.mod) == kKeys_Controls + 5)
          break;
        HandleInput(event.key.keysym.sym, event.key.keysym.mod, true);''')
    source = replace_exact(source,
        '      case SDL_KEYUP:\n        HandleInput(event.key.keysym.sym, event.key.keysym.mod, false);',
        '''      case SDL_KEYUP:
        if (event.key.keysym.sym == SDLK_F11) break;
        HandleInput(event.key.keysym.sym, event.key.keysym.mod, false);''')
    source = replace_exact(source,
        '    inputs |= g_gamepad_buttons;',
        '''    inputs |= g_gamepad_buttons;
    /* The modal dialog can consume key-up. Deliver START for exactly one frame. */
    if (g_native_sandbox_start_pending) {
      inputs |= 1 << 3;
      g_native_sandbox_start_pending = false;
    }''')
    source = replace_exact(source,
        '    if (g_sdl_audio_mixer_volume == SDL_MIX_MAXVOLUME) {',
        '''    if (g_sdl_audio_mixer_volume == 0) {
      SDL_memset(stream, 0, n); /* Audio simulation keeps running. */
    } else if (g_sdl_audio_mixer_volume == SDL_MIX_MAXVOLUME) {''')
    # Save slots accessed via SDL's save-state hotkeys are disabled when sandbox is
    # active. This does NOT protect the game's own SRAM writes.
    source = replace_exact(source,
        'static void HandleCommand_Locked(uint32 j, bool pressed) {\n  if (!pressed)\n    return;',
        '''static void HandleCommand_Locked(uint32 j, bool pressed) {
  if (!pressed) return;
  if (g_native_sandbox_active && j >= kKeys_Save && j <= kKeys_Save_Last) {
    fprintf(stderr, "[native sandbox] save-state shortcut blocked during practice.\\n");
    return;
  }''')
    source = replace_exact(source,
        'static void HandleVolumeAdjustment(int volume_adjustment) {',
        '''static void HandleVolumeAdjustment(int volume_adjustment) {
  /* Called with the audio mutex held. Keep practice muted on every platform. */
  if (g_native_sandbox_active) return;''')
    source = replace_exact(source,
        '  // clean sdl\n',
        '  if (g_native_sandbox_active) NativeSandboxSetActive(false);\n  // clean sdl\n')
    return source


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repo', help='Path to clean snesrev/zelda3 checkout')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    path = Path(a.repo) / 'src/main.c'
    try:
        original = path.read_text()
        modified = transform(original)
    except (OSError, ValueError) as e:
        sys.exit(f'NOT PATCHED: {e}')
    if a.dry_run:
        print('PASS: patch anchors compatible; no source changed')
        return
    backup = path.with_name('main.c.before_native_sandbox_phase3')
    if backup.exists():
        sys.exit('NOT PATCHED: backup already exists; review before trying again')
    backup.write_text(original)
    try:
        path.write_text(modified)
    except OSError:
        path.write_text(original)
        raise
    print(f'PATCHED: {path}\nBACKUP: {backup}\nSTART: native menu; F11: extra menu shortcut')


if __name__ == '__main__':
    main()
