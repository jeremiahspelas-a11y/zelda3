"""Fail CI or pre-commit if common ROMs, extracted assets, or personal saves are staged."""
from pathlib import PurePosixPath
import subprocess
import sys

paths = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
blocked = []
for name in filter(None, paths):
    path = PurePosixPath(name.lower())
    if (path.suffix in {'.sfc', '.smc', '.rom', '.srm'}
            or path.name in {'zelda3_assets.dat', 'sram.dat', 'sram.bak'}
            or str(path).startswith(('assets/img/', 'assets/dungeon/', 'assets/overworld/', 'assets/sound/'))
            or (path.suffix == '.sav' and not str(path).startswith('saves/ref/'))):
        blocked.append(name)
if blocked:
    sys.exit('Blocked game data in Git index:\n' + '\n'.join(blocked))
print('PASS: no ROMs, extracted assets, or personal saves in the Git index')
