#!/usr/bin/env python3
"""Static regression checks for Android buttons and the native SNES bridge.

These fail CI if START is conflated with LAUNCH, SELECT is omitted, or the
JavaScript/native SNES bit masks drift apart. Runtime handset testing is
still necessary; these checks do not claim to emulate Android or game logic.
"""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = (root / "browser" / "index.html").read_text()
patch = (root / "browser_patch.py").read_text()

buttons = [(int(n), name) for n, name in re.findall(
    r'<button[^>]*data-b="(\\d+)"[^>]*>([^<]+)</button>', page)]
assert len(buttons) == 12, buttons
assert sorted(n for n, _ in buttons) == list(range(12))
assert dict(buttons)[5] == "START"
assert dict(buttons)[4] == "SELECT"
assert page.count('id="launch-engine"') == 1
assert page.count('id="snes-start"') == 1
assert page.count('id="snes-select"') == 1
assert page.count('id="start"') == 0  # No ambiguous engine/START identity

# Native bit mapping follows src/main.c's kKbdRemap command offset.
native_bits = re.search(r'kNativeSnesBits\\[12\\] = \\{([^}]+)\\}', patch)
assert native_bits, "Expected explicit native SNES input table"
parsed = [int(v.strip()) for v in native_bits.group(1).split(',')]
expected = [4, 5, 6, 7, 2, 3, 8, 0, 9, 1, 10, 11]
assert parsed == expected, (parsed, expected)
assert len(set(parsed)) == 12
assert parsed[5] == 3  # START -> SNES 0x0008
assert parsed[4] == 2  # SELECT -> SNES 0x0004
assert 'return g_input1_state' in patch
assert "Module._ZeldaBrowserControl(id,on?1:0)" in page
assert "const nativeMask=Module._ZeldaBrowserControl(id,on?1:0)" in page

print("PASS: all 12 controls have unique native bits")
print("PASS: START=0x0008, SELECT=0x0004")
print("PASS: blue LAUNCH is separate from green START and SELECT")
