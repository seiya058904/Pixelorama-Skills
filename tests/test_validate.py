import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate


class MetadataTests(unittest.TestCase):
    def test_repository_passes(self):
        self.assertEqual(validate.validate(ROOT), [])

    def test_real_metadata(self):
        result=validate.parse_frontmatter((ROOT/validate.SKILL).read_text())
        self.assertEqual(result['name'],'pixelorama-skills')
        self.assertEqual(result['metadata']['version'],'1.1.0')

    def test_missing_delimiters(self):
        for text in ('name: foo','---\nname: foo'):
            with self.subTest(text=text),self.assertRaises(ValueError):
                validate.parse_frontmatter(text)

    def test_duplicate_fields(self):
        with self.assertRaises(ValueError):
            validate.parse_frontmatter('---\nname: a\nname: b\n---')

    def test_nested_without_metadata(self):
        with self.assertRaises(ValueError):
            validate.parse_frontmatter('---\n  name: a\n---')

    def test_reject_non_string_metadata(self):
        with self.assertRaises(ValueError):
            validate.parse_frontmatter('---\nmetadata:\n  ready: true\n---')

    def test_reject_numeric_metadata(self):
        with self.assertRaises(ValueError):
            validate.parse_frontmatter('---\nmetadata:\n  version: 1.0\n---')

    def test_quoted_numeric_metadata(self):
        result=validate.parse_frontmatter('---\nmetadata:\n  version: "1.0"\n---')
        self.assertEqual(result['metadata']['version'],'1.0')

    def test_quoted_boolean_word_is_string(self):
        result=validate.parse_frontmatter('---\nmetadata:\n  ready: "true"\n---')
        self.assertEqual(result['metadata']['ready'],'true')

    def test_anchors(self):
        self.assertEqual(validate.anchors('# A title\n## A title\n## 中文标题'),{'a-title','a-title-1','中文标题'})

    def test_code_block_not_heading(self):
        self.assertEqual(validate.anchors('```sh\n# not a heading\n```\n# Real'),{'real'})


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.doc=self.root/'README.md'

    def tearDown(self):
        self.temp.cleanup()

    def check(self,text):
        self.doc.write_text(text)
        return validate.check_links(self.doc,self.root)

    def test_valid_local_link_and_anchor(self):
        (self.root/'target.md').write_text('# Target')
        self.assertEqual(self.check('[go](target.md#target)'),[])

    def test_missing_target(self):
        self.assertTrue(self.check('[missing](no.md)'))

    def test_missing_anchor(self):
        (self.root/'target.md').write_text('# Target')
        self.assertTrue(self.check('[go](target.md#no)'))

    def test_traversal_rejected(self):
        self.assertTrue(self.check('[escape](../outside.md)'))

    def test_dangerous_scheme(self):
        self.assertTrue(self.check('<a href="javascript:alert(1)">bad</a>'))

    def test_https_external_not_falsely_validated(self):
        self.assertEqual(self.check('[external](https://example.com)'),[])

    def test_code_example_ignored(self):
        self.assertEqual(self.check('```md\n[example](missing.md)\n```'),[])


if __name__=='__main__':
    unittest.main()
