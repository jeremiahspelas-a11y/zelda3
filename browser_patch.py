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
    assert text.count(anchor)==1, "main-loop end anchor changed"
    # Yield to JS event loop on every video frame without restructuring SDL loop.
    start='    // if vsync isn\'t working, delay manually\n'
    assert text.count(start)==1, "frame throttle anchor changed"
    end='\n  }\n  if (g_config.autosave)'
    assert text.count(end)==1, "end of event loop anchor changed"
    text=text.replace(end, '\n#ifdef __EMSCRIPTEN__\n    emscripten_sleep(0);  /* ZELDA3_BROWSER_ASYNC_LOOP */\n#endif\n  }\n  if (g_config.autosave)',1)
    # Call the real native input handler, not a reimplementation of Zelda logic.
    anchor='void ZeldaApuLock() {'
    assert text.count(anchor)==1, "input bridge anchor changed"
    text=text.replace(anchor,
        '#ifdef __EMSCRIPTEN__\n'
        'EMSCRIPTEN_KEEPALIVE void ZeldaBrowserControl(int button, int down) {\n'
        '  if (button >= 0 && button < 12)\n'
        '    HandleCommand(kKeys_Controls + button, down != 0);\n'
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
