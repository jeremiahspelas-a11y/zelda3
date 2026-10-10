#!/usr/bin/env python3
"""Browser-only compatibility patch. Applies AFTER native install.py."""
from pathlib import Path
import sys

def patch(text):
    mark = "/* ZELDA3_BROWSER_ASYNC_LOOP */"
    if mark in text:
        raise ValueError("Browser patch already applied")
    anchor = '#include <SDL.h>\n'
    assert text.count(anchor)==1, "SDL include anchor changed"
    text=text.replace(anchor,anchor+'#ifdef __EMSCRIPTEN__\n#include <emscripten.h>\n#endif\n',1)
    anchor='  if (g_config.autosave)\n    HandleCommand(kKeys_Save + 0, true);\n\n  // clean sdl'
    # Phase3 inserts cleanup immediately before // clean sdl; keep this anchor optional.
    # Yield to JS event loop on every video frame without restructuring SDL loop.
    start='    // if vsync isn\'t working, delay manually\n'
    assert text.count(start)==1, "frame throttle anchor changed"
    end='\n  }\n  if (g_config.autosave)'
    assert text.count(end)==1, "end of event loop anchor changed"
    text=text.replace(end, '\n#ifdef __EMSCRIPTEN__\n    emscripten_sleep(0);  /* ZELDA3_BROWSER_ASYNC_LOOP */\n#endif\n  }\n  if (g_config.autosave)',1)
    # The browser bundle previously shipped without zelda3.ini, which leaves
    # g_config.enable_audio=false. Force explicit browser-safe config at startup.
    init = '  ParseConfigFile(config_file);\n'
    assert text.count(init)==1, 'Config startup anchor changed'
    text=text.replace(init, init +
       '#ifdef __EMSCRIPTEN__\n'
       '  g_config.enable_audio = true;\n'
       '  g_config.audio_freq = 44100;\n'
       '  g_config.audio_channels = 2;\n'
       '  g_config.audio_samples = 1024;\n'
       '  g_config.output_method = kOutputMethod_SDL;\n'
       '  g_config.autosave = false;\n'
       '  EM_ASM({ console.log("[Zelda3] Native browser audio enabled in C config"); });\n'
       '#endif\n', 1)
    device_line = '    device = SDL_OpenAudioDevice(NULL, 0, &want, &have, 0);\n'
    assert text.count(device_line)==1, 'SDL device startup anchor changed'
    text=text.replace(device_line,device_line+
       '#ifdef __EMSCRIPTEN__\n'
       '    EM_ASM({ console.log("[Zelda3] SDL_OpenAudioDevice id:", $0, "error:", UTF8ToString($1)); }, (int)device, SDL_GetError());\n'
       '#endif\n',1)
    # Opt-in authenticity test: game code's existing Zelda follower (#1), not
    # an invented sprite. Refuses to overwrite an existing quest follower.
    include = '#include <SDL.h>\n'
    assert text.count(include)==1
    text=text.replace(include, include+'#include "tagalong.h"\n',1)
    state_anchor = '/* ZELDA3_NATIVE_SANDBOX_PHASE3 */'
    assert text.count(state_anchor)==1
    text=text.replace(state_anchor,state_anchor+'\n#ifdef __EMSCRIPTEN__\nstatic bool g_coop_spawned_zelda;\n#endif',1)
    # Browser START opens a DOM modal, but all choices affect native C state.
    start_guard = '  if (g_native_sandbox_menu_open) return false;'
    assert text.count(start_guard)==1, 'Native practice modal guard changed'
    text=text.replace(start_guard, start_guard+'\n#ifdef __EMSCRIPTEN__\n  EM_ASM({ if (typeof window.ZeldaBrowserMenuOpen === "function") window.ZeldaBrowserMenuOpen(); });\n  return false;\n#else',1)
    tail='  return choice == 0;\n}'
    assert text.count(tail)==1, 'Native practice modal tail changed'
    text=text.replace(tail,'  return choice == 0;\n#endif\n}',1)
    # Call the real native input handler, not a reimplementation of Zelda logic.
    anchor='void ZeldaApuLock() {'
    assert text.count(anchor)==1, "input bridge anchor changed"
    text=text.replace(anchor,
        '#ifdef __EMSCRIPTEN__\n'
        'EMSCRIPTEN_KEEPALIVE void ZeldaBrowserControl(int button, int down) {\n'
        '  if (button >= 0 && button < 12)\n'
        '    HandleCommand(kKeys_Controls + button, down != 0);\n'
        '}\n'
        'EMSCRIPTEN_KEEPALIVE int ZeldaBrowserSandboxChoice(int choice) {\n'
        '  if (choice == 0) { g_native_sandbox_start_pending = true; return 10; }\n'
        '  else if (choice == 1) {\n'
        '    if (follower_indicator == 0 && submodule_index == 0 && (main_module_index == 7 || main_module_index == 9)) {\n'
        '      follower_indicator = 1; Follower_Initialize(); g_coop_spawned_zelda = true;\n'
        '      return 1; /* actual native follower state successfully enabled */\n'
        '    } else {\n'
        '      return (follower_indicator != 0) ? 21 : (submodule_index != 0 ? 22 : 23);\n'
        '    }\n'
        '  }\n'
        '  else if (choice == 2) {\n'
        '    if (g_coop_spawned_zelda && follower_indicator == 1) follower_indicator = 0; g_coop_spawned_zelda = false;\n'
        '    return 2;\n'
        '  }\n'
        '}\n'
        '#endif\n\n'+anchor,1)
    return text

def main():
    root=Path(sys.argv[1])
    path=root/'src'/'main.c'
    original=path.read_text()
    path.write_text(patch(original))
    print('Browser event yield and native input bridge installed.')
if __name__=='__main__':
    main()
