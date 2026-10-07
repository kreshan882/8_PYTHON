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


class SupportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = sample_project.build_support(Path(cls.tmp.name) / "shop")
        cls.k = build_knowledge(Config(root=cls.root, output=cls.root / "k.md", use_git=False))
        cls.md = render(cls.k)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_events_extracted(self):
        t = next(x for x in self.k.types if x.name == "PaymentService")
        charge = next(m for m in t.members if m.name == "charge")
        kinds = {(e.kind, e.level) for e in charge.events}
        self.assertIn(("log", "ERROR"), kinds)
        self.assertTrue(any(e.kind == "throw" and e.level == "PaymentException" for e in charge.events))
        err = next(e for e in charge.events if e.kind == "log" and e.level == "ERROR")
        self.assertFalse(err.exc_logged)
        self.assertIn("catch", err.context)

    def test_call_graph_entries_and_interfaces(self):
        cg = self.k.cg
        entries = cg.entries_of("com.acme.payment.PaymentService#charge", limit=5)
        self.assertTrue(any("/api/pay/charge" in e for e in entries))
        self.assertTrue(any("NightlyJob" in e for e in entries))
        # interface call resolves to implementation and mapper SQL
        self.assertEqual(cg.tables_reached("com.acme.web.UserController#create").get("app_user"), "W")

    def test_risks(self):
        r = self.k.risks
        self.assertEqual(len(r.swallowed), 1)
        self.assertTrue(any("refund" in w.owner for w in r.swallowed))
        self.assertTrue(any("retryCount" in w.owner for w in r.shared_state))
        self.assertTrue(any("same class" in w.text for w in r.proxy_pitfalls))
        self.assertNotIn("<h", self.md)

    def test_message_matching(self):
        from knowledge_gen.messages import match_text
        hits = match_text(self.k, "ERROR c.a.p.PaymentService - Gateway call failed for user Anna")
        self.assertTrue(hits and hits[0][1] == "exact" and hits[0][2].method == "charge")
        hits = match_text(self.k, "something totally unrelated happened today")
        self.assertEqual(hits, [])
        # constant resolved through message bundle
        site = next(s for s in self.k.messages if s.level == "IllegalArgumentException")
        self.assertIn("User is required for payment", site.resolved)

    def test_env_diff_and_secret_hidden(self):
        self.assertIn("Environment differences", self.md)
        self.assertIn("5000", self.md)
        self.assertNotIn("abc123", self.md)

    def test_sections(self):
        for title in ("Production support playbook", "Request flows", "Integrations", "Error handling and exceptions",
                      "Message index", "Risk hotspots"):
            self.assertIn(title, self.md)
        self.assertIn("ErrorAdvice.onPayment()", self.md)

    def test_stack_trace_mapping(self):
        from knowledge_gen.investigate import investigate, parse_trace
        trace = sample_project.sample_trace()
        chains = parse_trace(trace)
        self.assertEqual([c.exc.rsplit(".", 1)[-1] for c in chains],
                         ["PaymentException", "ResourceAccessException", "SocketTimeoutException"])
        out = investigate(self.k, trace, ["payment.user.missing"])
        src = sample_project.SUPPORT_FILES["src/main/java/com/acme/payment/PaymentService.java"]
        ln = sample_project.line_of(src, "throw new PaymentException")
        self.assertRegex(out, rf">>\s+{ln} \| ")
        self.assertIn("POST /api/pay/charge", out)
        self.assertIn("without stack trace", out)
        self.assertIn("payment.user.missing", out)
        self.assertIn("Read timed out", out)

    def test_cli_investigate(self):
        trace = Path(self.tmp.name) / "trace.txt"
        trace.write_text(sample_project.sample_trace(), encoding="utf-8")
        out = Path(self.tmp.name) / "o" / "knowledgeFile.md"
        self.assertEqual(main([str(self.root), "-o", str(out), "-q", "--no-git", "--investigate", str(trace),
                               "--search", "refund"]), 0)
        inv = (out.parent / "investigation.md").read_text(encoding="utf-8")
        self.assertIn("Investigation worksheet", inv)
        self.assertIn("Search: `refund`", inv)

    def test_detail_levels(self):
        full = render(build_knowledge(Config(root=self.root, output=self.root / "k.md", use_git=False, detail="full")))
        brief = render(build_knowledge(Config(root=self.root, output=self.root / "k.md", use_git=False, detail="brief")))
        self.assertGreater(len(full), len(brief))
        self.assertIn("Failure points", self.md)
        self.assertNotIn("Failure points", brief)


class GitTest(unittest.TestCase):
    def test_recent_changes(self):
        import shutil
        import subprocess
        if shutil.which("git") is None:
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as d:
            root = sample_project.build_support(Path(d) / "shop")
            env = {"GIT_AUTHOR_NAME": "Dev", "GIT_AUTHOR_EMAIL": "d@x", "GIT_COMMITTER_NAME": "Dev",
                   "GIT_COMMITTER_EMAIL": "d@x", "PATH": __import__("os").environ["PATH"], "HOME": d}
            for cmd in (["init", "-q"], ["add", "."], ["commit", "-q", "-m", "Fix gateway timeout"]):
                subprocess.run(["git", "-C", str(root)] + cmd, check=True, env=env, capture_output=True)
            k = build_knowledge(Config(root=root, output=root / "k.md"))
            self.assertIsNotNone(k.git)
            gf = k.git.files["src/main/java/com/acme/payment/PaymentService.java"]
            self.assertEqual(gf.last_subject, "Fix gateway timeout")
            self.assertIn("Recent changes", render(k))
