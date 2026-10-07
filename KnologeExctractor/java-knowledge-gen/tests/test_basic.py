import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import sample_project  # noqa: E402
from knowledge_gen.analyzer import build_knowledge  # noqa: E402
from knowledge_gen.cli import main  # noqa: E402
from knowledge_gen.config import Config  # noqa: E402
from knowledge_gen.parsers.java_parser import parse_java  # noqa: E402
from knowledge_gen.parsers.props_parser import parse_properties  # noqa: E402
from knowledge_gen.renderer import render  # noqa: E402


class SampleProjectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = sample_project.build(Path(cls.tmp.name) / "shop")
        cfg = Config(root=root, output=root / "knowledgeFile.md", title="Acme Shop")
        cls.k = build_knowledge(cfg)
        cls.md = render(cls.k)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_counts(self):
        self.assertEqual(len(self.k.java), 6)
        self.assertEqual(len(self.k.props), 1)
        self.assertEqual(len(self.k.js), 2)

    def test_endpoints_and_js_link(self):
        paths = {(e.http, e.path) for e in self.k.endpoints}
        self.assertIn(("GET", "/api/users/{id}"), paths)
        self.assertIn(("POST", "/api/users"), paths)
        self.assertIn(("ANY", "/legacy/*"), paths)
        self.assertIn("GET `/shop/api/users/` → `GET /api/users/{id}`", self.md)
        self.assertIn("POST `/shop/api/users` → `POST /api/users`", self.md)

    def test_vendor_js_skipped(self):
        self.assertTrue(self.k.js["src/main/webapp/js/jquery-3.6.0.min.js"].vendor)

    def test_layers_and_deps(self):
        layers = {t.name: self.k.type_layer[t.qualified] for t in self.k.types}
        self.assertEqual(layers["UserController"], "Controller / Web")
        self.assertEqual(layers["UserServiceImpl"], "Service")
        self.assertEqual(layers["UserMapper"], "Repository / DAO / Mapper")
        self.assertEqual(layers["User"], "Entity / Model / DTO")
        impl = "src/main/java/com/acme/service/UserServiceImpl.java"
        self.assertIn("src/main/java/com/acme/dao/UserMapper.java", self.k.file_deps[impl])

    def test_data_layer(self):
        self.assertIn("app_user", self.k.tables)
        self.assertIn("com.acme.dao.UserMapper", self.k.mapper_xml)
        self.assertIn("com.acme.service.UserServiceImpl", self.k.bean_refs)

    def test_secrets_masked(self):
        self.assertNotIn("hunter2", self.md)
        self.assertNotIn("s3cret", self.md)
        self.assertIn("***", self.md)

    def test_property_usage_and_unicode(self):
        self.assertIn("UserServiceImpl", self.k.prop_usage["app.default.role"])
        entries = dict(self.k.props["src/main/resources/app.properties"].entries)
        self.assertEqual(entries["greeting"], "குலிர்")
        self.assertEqual(entries["long.value"], "part one part two")

    def test_unreferenced_detected_and_strings_ignored(self):
        self.assertIn("Unused", self.md.split("Not referenced by other scanned Java files")[1])
        self.assertNotIn("Fake", self.md)

    def test_sections_present(self):
        for title in ("Project overview", "Technology stack and build", "Entry points and HTTP endpoints",
                      "Data layer", "Configuration", "Class catalog", "File index"):
            self.assertIn(title, self.md)

    def test_cli_writes_file(self):
        root = Path(self.tmp.name) / "shop"
        out = Path(self.tmp.name) / "out" / "knowledgeFile.md"
        self.assertEqual(main([str(root), "-o", str(out), "-q"]), 0)
        self.assertTrue(out.read_text(encoding="utf-8").startswith("# Knowledge file"))


class JavaParserTest(unittest.TestCase):
    def test_nested_enum_record_generics(self):
        src = """package p;
        public class Outer<T extends Comparable<T>> extends Base<T> implements A, B<String> {
            enum Color { RED, GREEN; int x; }
            record Pt(int x, int y) {}
            public <R> R map(java.util.function.Function<T, R> f) throws Exception { return null; }
            Outer() {}
        }"""
        jf = parse_java(src, "Outer.java")
        names = {t.display: t for t in jf.types}
        self.assertEqual(set(names), {"Outer", "Outer.Color", "Outer.Pt"})
        self.assertEqual(names["Outer"].extends, ["Base<T>"])
        self.assertEqual(names["Outer"].implements, ["A", "B<String>"])
        self.assertEqual(names["Outer.Color"].enum_constants, ["RED", "GREEN"])
        kinds = [(m.kind, m.name) for m in names["Outer"].members]
        self.assertIn(("method", "map"), kinds)
        self.assertIn(("constructor", "Outer"), kinds)

    def test_control_flow_not_methods(self):
        src = """class A { void run() { if (x) { foo(); } for (;;) { bar(); } new Thread(r) { }; } }"""
        jf = parse_java(src, "A.java")
        self.assertEqual([m.name for m in jf.types[0].members], ["run"])


class PropertiesTest(unittest.TestCase):
    def test_separators(self):
        info = parse_properties("a=1\nb : 2\nc 3\n! comment\n# x\nd=\n", "x.properties")
        self.assertEqual(dict(info.entries), {"a": "1", "b": "2", "c": "3", "d": ""})


if __name__ == "__main__":
    unittest.main()
