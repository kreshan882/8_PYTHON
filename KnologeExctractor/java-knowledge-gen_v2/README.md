# java-knowledge-gen
## Run
python main.py D:\3_JAVA_STRUCTS2_K\Startup_WEB -o knowledgeFile_v2.md

## what will analyz
Python tool that scans a Java project (100+ files of `.java`, `.xml`, `.properties`, `.js`) and generates a
single **`knowledgeFile.md`**: a structured map of the code base, ready to read, share, or paste into an LLM.

No third-party packages are needed (Python 3.8+ standard library only).

## Usage

```bash
python main.py /path/to/java-project                       # writes ./knowledgeFile.md
python main.py D:\3_JAVA_STRUCTS2_K\Startup_WEB -o knowledgeFile_v2.md --title "Acme Shop"
python -m knowledge_gen /path/to/java-project              # same thing
```

| Option | Meaning |
|---|---|
| `-o, --output FILE` | output file (default `knowledgeFile.md`) |
| `--title TEXT` | project title in the header |
| `--ext .java .xml ...` | extensions to scan (default: java xml properties js) |
| `--exclude GLOB ...` | extra patterns to skip, e.g. `'src/test/*' '*Generated*'` |
| `--include-private` | also list private methods |
| `--include-vendor-js` | analyse third-party / minified JS (skipped by default) |
| `--max-methods N` | methods listed per class (default 25) |
| `--max-props-rows N` | keys listed per `.properties` file (default 60) |
| `--no-index` | omit the per-file index table (shorter output) |

Always skipped: `target/`, `build/`, `out/`, `bin/`, `node_modules/`, `.git/` and other dot-directories.

## What the generated file contains

1. **Project overview**: file/line counts per extension, packages and their classes
2. **Technology stack and build**: frameworks detected from imports, Maven coordinates/dependencies
3. **Architecture layers**: Controller / Service / DAO-Mapper / Entity / Config / Util ... (by annotation, super type, name)
4. **Entry points and HTTP endpoints**: Spring MVC, JAX-RS, `@WebServlet`, `web.xml`, `main()`, `@Scheduled`, message listeners
5. **Data layer**: MyBatis mapper XML (statements, tables, SQL), JPA entities, Hibernate mappings, table index
6. **Configuration**: `.properties` keys (with which class reads them), Spring bean XML, `web.xml`, logging config
7. **Front-end JavaScript**: functions, classes, AJAX calls **linked to the Java endpoints they hit**
8. **Class catalog**: per class: annotations, extends/implements, Javadoc purpose, injected beans, key methods
   (with their endpoint), "Uses" / "Used by"
9. **Dependency insights**: most depended-on classes, classes nobody references
10. **File index** and **warnings**

Secrets are masked: values of keys such as `password`, `secret`, `token`, `api-key` and credentials inside URLs
are replaced with `***`.

## Production support / root-cause analysis

The knowledge file is built for people who diagnose production problems. Besides the structure it contains:

| Section | Helps you answer |
|---|---|
| Production support playbook | "I have X (stack trace, log line, failing URL...) - where do I look?" |
| Request flows | What runs for each endpoint / job / listener: services, SQL, external calls, `[TX]`, `[SWALLOWS EXCEPTION]` |
| Data layer → tables | Which entry points read or write a table (R/W) |
| Integrations | HTTP clients, DB, queues, mail, cache, files, with the config keys that hold their URLs |
| Error handling and exceptions | `@ExceptionHandler`s (what the caller receives) and custom exception types |
| Message index | Every log / thrown / error-response message with **When** it fires and **Triggered by**; message-bundle keys and constants are resolved to text |
| Configuration | Who reads each key, operational settings (timeouts, pools, cron) and **Environment differences** between `*-dev/-prod` property files (secrets never shown) |
| Risk hotspots | Swallowed exceptions, error logs without stack trace, shared state in singletons, `@Transactional` self-invocation, blocking calls, hard-coded URLs, complex methods, TODOs |
| Recent changes | `git log` of the last N days (skipped silently when git or a repository is missing) |
| Class catalog | Per method: calls, SQL, failure points; per class: last change, constants, field constraints |

### Investigation mode

```bash
python main.py /path/to/project -o knowledgeFile.md --investigate trace.txt --search "Payment gateway" ORDER_NOT_FOUND
```

writes `investigation.md` next to the knowledge file. For a pasted stack trace (use `--investigate -` for stdin) it
shows, per exception in the chain: the meaning and what to check, the failing source lines, callers, entry points
(and the JS that calls them), tables touched, configuration read by the class, matching log statements, known risks
and recent commits of the involved files. `--search` finds error texts, keys or names in code, messages and properties.

Useful options: `--detail brief|normal|full`, `--git-days N`, `--no-git`, `--include-debug-logs`, `--max-flows`, `--max-messages`.

All of this is static analysis (no compilation, calls resolved heuristically): it tells you what the code *can* do.
Confirm with real logs and data.

## How it works

Parsing is static and regex/brace-matching based (no compilation, no classpath needed). Comments and string
literals are blanked out first, so braces or keywords inside them cannot confuse the structure scan.
Treat the result as an accurate *map*, and verify details in the source for critical decisions.

```
knowledge_gen/
  scanner.py          walk tree, read files (UTF-8 / cp1252), skip vendor JS
  parsers/            java_parser, xml_parser, props_parser, js_parser, common
  analyzer.py         layers, endpoints, dependency graph, tables, JS -> Java links
  renderer.py         Markdown output
  cli.py              command line
tests/                python -m unittest discover -s tests
```

## Tests

```bash
python -m unittest discover -s tests -v
```
