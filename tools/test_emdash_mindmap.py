"""Tests for emdash-mindmap."""
import os
import subprocess
import tempfile
import unittest
import xml.dom.minidom

TOOL = os.path.join(os.path.dirname(__file__), "emdash-mindmap.py")
DOC = "# Root\n## A\n- one\n- two\n## B\n### B1\ntext\n"


class TestMindmap(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.md = os.path.join(self.d, "doc.md")
        open(self.md, "w").write(DOC)
        self.svg = os.path.join(self.d, "map.svg")

    def test_svg(self):
        r = subprocess.run(["python3", TOOL, self.md, "--out", self.svg],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        dom = xml.dom.minidom.parse(self.svg)
        texts = [n.firstChild.data for n in dom.getElementsByTagName("text")]
        for want in ["Root", "A", "one", "B", "B1"]:
            self.assertIn(want, texts, texts)

    def test_depth(self):
        r = subprocess.run(["python3", TOOL, self.md, "--out", self.svg, "--depth", "1"],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        dom = xml.dom.minidom.parse(self.svg)
        texts = [n.firstChild.data for n in dom.getElementsByTagName("text")]
        self.assertIn("Root", texts)
        self.assertNotIn("B1", texts)


if __name__ == "__main__":
    unittest.main()
