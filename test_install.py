"""Check the installer against pinned real upstream input, without a ROM."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from install import MARK, transform

UPSTREAM = '45a149d8b4bb8098f53d1009f76e76e7d8b79bbf'
ROOT = Path(__file__).resolve().parent

class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = subprocess.check_output(['git', 'show', f'{UPSTREAM}:src/main.c'], cwd=ROOT, text=True)

    def test_real_upstream_and_double_install(self):
        patched = transform(self.source)
        self.assertEqual(patched.count(MARK), 1)
        with self.assertRaisesRegex(ValueError, 'already installed'):
            transform(patched)

    def test_missing_or_duplicate_anchors_fail_closed(self):
        anchor = 'static int g_sdl_audio_mixer_volume = SDL_MIX_MAXVOLUME;'
        for source in (self.source.replace(anchor, ''), self.source + '\n' + anchor):
            with self.subTest(source_length=len(source)):
                with self.assertRaisesRegex(ValueError, 'Expected exactly one'):
                    transform(source)

    def test_older_patch_rejected(self):
        for marker in ('ZELDA3_NATIVE_SANDBOX_PHASE2', 'COOP_NATIVE_SANDBOX_PHASE1'):
            with self.assertRaisesRegex(ValueError, 'clean upstream'):
                transform(self.source + '\n/* ' + marker + ' */')

    def test_cli_dry_run_install_and_refusal_preserve_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'src/main.c'
            path.parent.mkdir()
            path.write_text(self.source)
            original = path.read_bytes()
            command = ['python3', str(ROOT / 'install.py'), tmp]
            subprocess.run(command + ['--dry-run'], check=True, capture_output=True)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(len(list(path.parent.iterdir())), 1)
            subprocess.run(command, check=True, capture_output=True)
            patched = path.read_bytes()
            backup = path.with_name('main.c.before_native_sandbox_phase3')
            self.assertEqual(backup.read_bytes(), original)
            self.assertIn(MARK.encode(), patched)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(path.read_bytes(), patched)
            self.assertEqual(backup.read_bytes(), original)

if __name__ == '__main__':
    unittest.main(verbosity=2)
