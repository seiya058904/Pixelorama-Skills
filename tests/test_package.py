import hashlib
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import package


class PackagingTests(unittest.TestCase):
    def test_reproducible_source(self):
        self.assertEqual(package.zip_bytes(ROOT),package.zip_bytes(ROOT))

    def test_reproducible_skill(self):
        self.assertEqual(package.zip_bytes(ROOT,True),package.zip_bytes(ROOT,True))

    def test_skill_is_self_contained(self):
        with zipfile.ZipFile(io.BytesIO(package.zip_bytes(ROOT,True))) as z:
            names=set(z.namelist())
            self.assertEqual(len(names),5)
            self.assertIn('pixelorama-skills/SKILL.md',names)
            self.assertIn('pixelorama-skills/references/setup.md',names)
            self.assertIn('pixelorama-skills/references/drawing.md',names)
            self.assertIn('pixelorama-skills/scripts/doctor.py',names)
            self.assertIn('pixelorama-skills/LICENSE',names)
            self.assertIsNone(z.testzip())

    def test_source_allowlist(self):
        with zipfile.ZipFile(io.BytesIO(package.zip_bytes(ROOT))) as z:
            self.assertEqual(set(z.namelist()),{'Pixelorama-Skills/'+p for p in package.PROJECT_FILES})
            self.assertTrue(all('..' not in Path(n).parts for n in z.namelist()))
            self.assertIsNone(z.testzip())

    def test_hashes_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'dist'
            hashes=package.build(out)
            for name,digest in hashes.items():
                self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),digest)
            sums=(out/'SHA256SUMS.txt').read_bytes()
            with self.assertRaises(FileExistsError):
                package.build(out)
            self.assertEqual((out/'SHA256SUMS.txt').read_bytes(),sums)

    def test_no_build_inside_skill(self):
        with self.assertRaises(ValueError):
            package.build(ROOT/'skills/pixelorama-skills/dist')


if __name__=='__main__':
    unittest.main()
