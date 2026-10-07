# java-knowledge-gen

Python tool that scans a Java project (100+ files of `.java`, `.xml`, `.properties`, `.js`) and generates a
single **`knowledgeFile.md`**: a structured map of the code base, ready to read, share, or paste into an LLM.

No third-party packages are needed (Python 3.8+ standard library only).

## Usage

```bash
python main.py /path/to/java-project                       # writes ./knowledgeFile.md
python main.py /path/to/java-project -o docs/knowledgeFile.md --title "Acme Shop"
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
