import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import publish


class PublishingTests(unittest.TestCase):
    def test_plan_target(self):
        result=publish.plan()
        self.assertEqual(result['repository'],'seiya058904/Pixelorama-Skills')
        self.assertEqual(result['visibility'],'public')

    def test_default_dry_run_never_publishes(self):
        with patch.object(sys,'argv',['publish.py']),patch.object(publish,'publish') as execute,patch('sys.stdout',new_callable=io.StringIO) as out:
            self.assertEqual(publish.main(),0)
            execute.assert_not_called()
            self.assertEqual(json.loads(out.getvalue())['mode'],'DRY_RUN_NO_WRITES')

    def test_missing_tools_refuses_write(self):
        with patch.object(publish,'validate',return_value=[]),patch.object(publish.shutil,'which',return_value=None),patch.object(publish,'run') as execute:
            with self.assertRaises(RuntimeError):
                publish.publish()
            execute.assert_not_called()

    def test_invalid_repository_refuses_write(self):
        with patch.object(publish,'validate',return_value=['bad skill']),patch.object(publish,'run') as execute:
            with self.assertRaises(RuntimeError):
                publish.publish()
            execute.assert_not_called()


if __name__=='__main__':
    unittest.main()
