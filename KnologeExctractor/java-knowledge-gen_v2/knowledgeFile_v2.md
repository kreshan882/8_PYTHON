# Knowledge file — Startup_WEB

> Auto-generated on 2026-10-07 17:49 from `Startup_WEB` by java-knowledge-gen. Structure is extracted statically (regex based, no compilation) — treat it as a map, and verify details in the source.

## Contents

- [1. Project overview](#1-project-overview)
- [2. Technology stack and build](#2-technology-stack-and-build)
- [3. Production support playbook](#3-production-support-playbook)
- [4. Architecture layers](#4-architecture-layers)
- [5. Entry points and HTTP endpoints](#5-entry-points-and-http-endpoints)
- [6. Request flows](#6-request-flows)
- [7. Data layer](#7-data-layer)
- [8. Integrations](#8-integrations)
- [9. Configuration](#9-configuration)
- [10. Risk hotspots](#10-risk-hotspots)
- [11. Front-end JavaScript](#11-front-end-javascript)
- [12. Class catalog](#12-class-catalog)
- [13. Dependency insights](#13-dependency-insights)
- [14. File index](#14-file-index)

## 1. Project overview

| Extension | Files | Lines |
|---|---|---|
| `.java` | 57 | 10,195 |
| `.js` | 13 | 41,470 |
| `.properties` | 3 | 211 |
| `.xml` | 7 | 2,061 |
| **Total** | **80** | **53,937** |

- Java types: **57** (56 class, 1 interface) in **17** packages

### Packages

| Package | Types | Classes |
|---|---|---|
| `com.shop.db` | 1 | DBConnection |
| `com.shop.global` | 1 | ContextListener |
| `com.shop.init` | 8 | Cast, InitConfigValue, InitConfigValueReader, Module, Operation, PageVarList, Status, TaskVarList |
| `com.shop.interceptor` | 1 | AccessControlInterceptor |
| `com.shop.inv.member.action` | 3 | ChildrenManagement, EditAndViewMemberManagement, MemberManagement |
| `com.shop.inv.member.bean` | 4 | ChildrenBean, ChildrenInputBean, MemberBean, MemberManagementInputBean |
| `com.shop.inv.member.service` | 2 | ChildrenService, MemberManagementService |
| `com.shop.inv.report.action` | 2 | MemberReport, MemberSummary |
| `com.shop.inv.report.bean` | 4 | MemberReportBean, MemberReportInputBean, MemberSummaryBean, MemberSummaryInputBean |
| `com.shop.inv.report.service` | 2 | MemberReportService, MemberSummaryService |
| `com.shop.inv.user.action` | 2 | UserManagement, UsrProfileManagement |
| `com.shop.inv.user.bean` | 4 | UserBean, UserManagementInputBean, UsrProfileBean, UsrProfileManagementInputBean |
| `com.shop.inv.user.service` | 2 | UserManagementService, UsrProfileManagementService |
| `com.shop.login.action` | 1 | UserLogin |
| `com.shop.login.bean` | 8 | ConfigurationBean, HomeValues, ModuleBean, PageBean, SessionUserBean, TaskBean, UserLoginBean, UserProfileModuleBean |
| `com.shop.login.service` | 1 | LoginService |
| `com.shop.util` | 11 | AccessControlService, Common, EswitchEchoTest, ExcelCommon, LogFileCreator, ModuleComparator, PasswordValidator, Sessio… |

## 2. Technology stack and build

| Technology (from imports) | Files using it |
|---|---|
| Servlet API | 11 |
| JDBC | 9 |
| Struts 2 | 9 |
| Apache POI | 1 |

**Front-end libraries/frameworks detected in JS:** jQuery

## 3. Production support playbook

Use this file as a map. Start from the evidence you have:

| You have | Go to |
|---|---|
| A stack trace | Run `--investigate trace.txt`: it maps every frame to code, callers, SQL, config and recent changes. Or look the class up in **Class catalog**. |
| A log line or an error text shown to users | Search the exact words in **Message index**. For UI texts also check the message bundles in **Configuration**. |
| A failing URL / API / screen | **Entry points** → **Request flows** shows everything that runs for that request (services, SQL, external calls). |
| Wrong, missing or duplicated data | **Data layer** → *Database tables*: which entry points read or write the table, and the SQL used. |
| Works in one environment but not another | **Configuration** → *Environment differences* lists keys that differ or are missing per environment. |
| Started after a release | **Recent changes**: files and commits of the last days, then open those classes in the catalog. |
| Intermittent, slow, or only under load | **Risk hotspots**: shared mutable state, blocking calls, async jobs, complex methods; **Integrations** for timeouts and external systems. |
| An external system is failing | **Integrations**: who calls it, with which URL/queue, from which flow. |
| Errors that never show up in logs | **Risk hotspots**: swallowed exceptions and error logs without stack trace. |

**Root-cause checklist**

1. Identify the exact failing code (Message index / stack trace) and the *condition* that leads to it (`When` column).
2. Follow **Triggered by** to the entry point, then read its request flow to see which data and systems are involved.
3. Check what the failing code depends on: SQL/tables, configuration keys, external calls.
4. Compare configuration between environments and look at recent changes of the involved files.
5. Check the risk list for the involved classes (swallowed exceptions, shared state, transaction pitfalls).

_Everything here is derived statically from source: it shows what the code *can* do. Confirm with real logs/data before concluding._

## 4. Architecture layers

| Layer | Types | Examples |
|---|---|---|
| Entity / Model / DTO | 19 | ChildrenBean, ChildrenInputBean, ConfigurationBean, MemberBean, MemberManagementInputBean, MemberReportBean, MemberReportInputBean, MemberSummaryBean, MemberSu… |
| Other | 17 | Cast, Common, DBConnection, ExcelCommon, HomeValues, InitConfigValue, InitConfigValueReader, LogFileCreator, Module, ModuleComparator, Operation, PageVarList … |
| Controller / Web | 8 | ChildrenManagement, EditAndViewMemberManagement, MemberManagement, MemberReport, MemberSummary, UserLogin, UserManagement, UsrProfileManagement |
| Service | 8 | AccessControlService, ChildrenService, LoginService, MemberManagementService, MemberReportService, MemberSummaryService, UserManagementService, UsrProfileManag… |
| Filter / Listener / Interceptor | 2 | AccessControlInterceptor, ContextListener |
| Test | 2 | EswitchEchoTest, Test |
| Utility | 1 | Util |

## 5. Entry points and HTTP endpoints

### Other entry points

| Kind | Where | File |
|---|---|---|
| main() | `Test` | `src/java/com/shop/util/Test.java` |

## 6. Request flows

For each entry point: the methods it calls (interfaces resolved to implementations), SQL it runs and external systems it touches. `[TX]` = transactional, `[SWALLOWS EXCEPTION]` = an exception is silently ignored.
Call resolution is heuristic: reflection, events and dynamic dispatch are not followed.

#### main()
`src/java/com/shop/util/Test.java:35`
- `Test.main()`
  - `Util.encryptionPass()`
  - `Util.decryptionPass()`

## 7. Data layer

### Database tables referenced

_Access = read/write as seen in SQL reachable from the entry points; use it to find who can change a table._

| Table | Access | Defined/used in | Reached from |
|---|---|---|---|

## 8. Integrations

| Kind | Type | Used in | Targets / calls |
|---|---|---|---|
| Database | `Connection` | `DBConnection.dbConnectionClose()`, `ChildrenService.loadData()`, `ChildrenService.findData()`, `ChildrenService.updateData()`, `ChildrenService.deleteData()`,… | close(); prepareStatement(); setAutoCommit(); commit() |
| Database | `PreparedStatement` | `ChildrenService.loadData()`, `ChildrenService.findData()`, `ChildrenService.updateData()`, `ChildrenService.deleteData()`, `ChildrenService.addData()`, `Child… | setString(); executeQuery(); close(); executeUpdate() |
| File / FTP | `FileInputStream` | `ExcelCommon.zipFiles()` | read(); close() |

**Configured hosts / URLs / queues**

| Key | Value | File | Read by |
|---|---|---|---|
| `j2ee.server.type` | gfv3ee6 | `project.properties` |  |

## 9. Configuration

### `nbproject/genfiles.properties`
6 keys

| Key | Value | Read by |
|---|---|---|
| `build.xml.data.CRC32` | af9bd166 |  |
| `build.xml.script.CRC32` | 9dd262a7 |  |
| `build.xml.stylesheet.CRC32` | 651128d4@1.68.1.1 |  |
| `nbproject/build-impl.xml.data.CRC32` | af9bd166 |  |
| `nbproject/build-impl.xml.script.CRC32` | 375cfafb |  |
| `nbproject/build-impl.xml.stylesheet.CRC32` | 99ea4b56@1.68.1.1 |  |

### `nbproject/project.properties`
122 keys
- Key groups: `file`×39, `javadoc`×12, `j2ee`×11, `build`×9, `javac`×9, `auxiliary`×7, `annotation`×5, `dist`×5, `war`×3, `debug`×2, `source`×2, `client`×1

| Key | Value | Read by |
|---|---|---|
| `annotation.processing.enabled` | true |  |
| `annotation.processing.enabled.in.editor` | true |  |
| `annotation.processing.processors.list` |  |  |
| `annotation.processing.run.all.processors` | true |  |
| `annotation.processing.source.output` | ${build.generated.sources.dir}/ap-source-output |  |
| `auxiliary.org-netbeans-modules-css-prep.less_2e_compiler_2e_options` |  |  |
| `auxiliary.org-netbeans-modules-css-prep.less_2e_enabled` | false |  |
| `auxiliary.org-netbeans-modules-css-prep.less_2e_mappings` | /less:/css |  |
| `auxiliary.org-netbeans-modules-css-prep.sass_2e_compiler_2e_options` |  |  |
| `auxiliary.org-netbeans-modules-css-prep.sass_2e_enabled` | false |  |
| `auxiliary.org-netbeans-modules-css-prep.sass_2e_mappings` | /scss:/css |  |
| `auxiliary.org-netbeans-modules-web-clientproject-api.js_2e_libs_2e_folder` | js/libs |  |
| `build.classes.dir` | ${build.web.dir}/WEB-INF/classes |  |
| `build.classes.excludes` | **/*.java,**/*.form |  |
| `build.dir` | build |  |
| `build.generated.dir` | ${build.dir}/generated |  |
| `build.generated.sources.dir` | ${build.dir}/generated-sources |  |
| `build.test.classes.dir` | ${build.dir}/test/classes |  |
| `build.test.results.dir` | ${build.dir}/test/results |  |
| `build.web.dir` | ${build.dir}/web |  |
| `build.web.excludes` | ${build.classes.excludes} |  |
| `client.urlPart` |  |  |
| `compile.jsps` | false |  |
| `conf.dir` | ${source.root}/conf |  |
| `debug.classpath` | ${build.classes.dir}:${javac.classpath} |  |
| `debug.test.classpath` | ${run.test.classpath} |  |
| `display.browser` | true |  |
| `dist.archive.excludes` |  |  |
| `dist.dir` | dist |  |
| `dist.ear.war` | ${dist.dir}/${war.ear.name} |  |
| `dist.javadoc.dir` | ${dist.dir}/javadoc |  |
| `dist.war` | ${dist.dir}/${war.name} |  |
| `endorsed.classpath` | ${libs.javaee-endorsed-api-6.0.classpath} |  |
| `excludes` |  |  |
| `file.reference.antlr-2.7.7.jar` | libs/antlr-2.7.7.jar |  |
| `file.reference.asm-3.3.jar` | libs/asm-3.3.jar |  |
| `file.reference.asm-commons-3.3.jar` | libs/asm-commons-3.3.jar |  |
| `file.reference.asm-tree-3.3.jar` | libs/asm-tree-3.3.jar |  |
| `file.reference.commons-collections-3.2.1.jar` | libs/commons-collections-3.2.1.jar |  |
| `file.reference.commons-digester-1.7.jar` | libs/commons-digester-1.7.jar |  |
| `file.reference.commons-fileupload-1.2.2.jar` | libs/commons-fileupload-1.2.2.jar |  |
| `file.reference.commons-io-2.0.1.jar` | libs/commons-io-2.0.1.jar |  |
| `file.reference.commons-lang-2.4.jar` | libs/commons-lang-2.4.jar |  |
| `file.reference.commons-lang3-3.1.jar` | libs/commons-lang3-3.1.jar |  |
| `file.reference.commons-logging-1.1.1.jar` | libs/commons-logging-1.1.1.jar |  |
| `file.reference.DBPool-5.0.jar` | libs/DBPool-5.0.jar |  |
| `file.reference.dom4j-1.6.1.jar` | libs/dom4j-1.6.1.jar |  |
| `file.reference.e24pki_v1.12.jar` | libs/e24pki_v1.12.jar |  |
| `file.reference.freemarker-2.3.19.jar` | libs/freemarker-2.3.19.jar |  |
| `file.reference.groovy-1.7-beta-2.jar` | libs/groovy-1.7-beta-2.jar |  |
| `file.reference.itext-2.1.7.jar` | libs/itext-2.1.7.jar |  |
| `file.reference.jasperreports-5.0.1.jar` | libs/jasperreports-5.0.1.jar |  |
| `file.reference.javassist-3.11.0.GA.jar` | libs/javassist-3.11.0.GA.jar |  |
| `file.reference.jprov.jar` | libs/jprov.jar |  |
| `file.reference.json-lib-2.3-jdk15.jar` | libs/json-lib-2.3-jdk15.jar |  |
| `file.reference.mysql-connector-java-5.1.44.jar` | libs/mysql-connector-java-5.1.44.jar |  |
| `file.reference.ognl-3.0.5.jar` | libs/ognl-3.0.5.jar |  |
| `file.reference.poi-3.10-FINAL-20140208.jar` | libs/poi-3.10-FINAL-20140208.jar |  |
| `file.reference.poi-examples-3.10-FINAL-20140208.jar` | libs/poi-examples-3.10-FINAL-20140208.jar |  |
| `file.reference.poi-excelant-3.10-FINAL-20140208.jar` | libs/poi-excelant-3.10-FINAL-20140208.jar |  |

… +62 more keys

### `src/java/log4j.properties`
7 keys

| Key | Value | Read by |
|---|---|---|
| `log4j.rootLogger` | WARN, stdout |  |
| `log4j.appender.stdout` | org.apache.log4j.ConsoleAppender |  |
| `log4j.appender.stdout.layout` | org.apache.log4j.PatternLayout |  |
| `log4j.appender.stdout.layout.ConversionPattern` | %d %5p (%c:%L) - %m%n |  |
| `log4j.logger.noModule` | ERROR |  |
| `log4j.logger.com.opensymphony` | INFO |  |
| `log4j.logger.org.apache.struts2` | INFO |  |

### `build.xml`
Ant build `Startup_WEB` default target `default`

### `nbproject/ant-deploy.xml`
Ant build `` default target `-deploy-ant`

**Targets**
- `-init-cl-deployment-env`
- `-parse-sun-web`
- `-parse-glassfish-web`
- `-no-parse-sun-web`
- `-add-resources`
- `-deploy-ant`
- `-deploy-without-pw`
- `-deploy-with-pw`
- `-undeploy-ant`
- `-undeploy-without-pw`
- `-undeploy-with-pw`

### `nbproject/build-impl.xml`
Ant build `Startup_WEB-impl` default target `default`

**Targets**
- `default`
- `-pre-init`
- `-init-private`
- `-init-user`
- `-init-project`
- `-do-ear-init`
- `-do-init`
- `-init-cos`
- `-post-init`
- `-init-check`
- `-init-macrodef-property`
- `-init-macrodef-javac-with-processors`
- `-init-macrodef-javac-without-processors`
- `-init-macrodef-javac`
- `-init-macrodef-junit-init`
- `-init-test-properties`
- `-init-macrodef-junit-single`
- `-init-macrodef-junit-batch`
- `-init-macrodef-junit`
- `-init-macrodef-testng`
- `-init-macrodef-test-impl`
- `-init-macrodef-junit-impl`
- `-init-macrodef-testng-impl`
- `-init-macrodef-test`
- `-init-macrodef-junit-debug`
- `-init-macrodef-junit-debug-batch`
- `-init-macrodef-junit-debug-impl`
- `-init-macrodef-testng-debug`
- `-init-macrodef-testng-debug-impl`
- `-init-macrodef-test-debug-junit`
- `-init-macrodef-test-debug-testng`
- `-init-macrodef-test-debug`
- `-init-macrodef-java`
- `-init-macrodef-nbjsdebug`
- `-init-macrodef-nbjpda`
- `-init-debug-args`
- `-init-macrodef-debug`
- `-init-taskdefs`
- `-init-ap-cmdline-properties`
- `-init-ap-cmdline-supported`
- `-init-ap-cmdline`
- `profile-init`
- `-profile-pre-init`
- `-profile-post-init`
- `-profile-init-check`
- `init`
- `deps-module-jar`
- `deps-ear-jar`
- `deps-jar`
- `-pre-pre-compile`
- `-pre-compile`
- `-copy-webdir`
- `-do-compile`
- `-copy-manifest`
- `-copy-persistence-xml`
- `-post-compile`
- `compile`
- `-pre-compile-single`
- `-do-compile-single`
- `-post-compile-single`
- `compile-single`
- `compile-jsps`
- `-do-compile-single-jsp`
- `compile-single-jsp`
- `-pre-dist`
- `-do-dist-without-manifest`
- `-do-dist-with-manifest`
- `-do-tmp-dist-without-manifest`
- `-do-tmp-dist-with-manifest`
- `do-dist`
- `library-inclusion-in-manifest`
- `library-inclusion-in-archive`
- `-clean-webinf-lib`
- `do-ear-dist`
- `-post-dist`
- `dist`
- `dist-ear`
- `run`
- `-pre-run-deploy`
- `-post-run-deploy`
- `-pre-nbmodule-run-deploy`
- `-post-nbmodule-run-deploy`
- `-run-deploy-am`
- `run-deploy`
- `-run-deploy-nb`
- `-init-deploy-ant`
- `run-undeploy`
- `-run-undeploy-nb`
- `verify`
- `run-display-browser`
- `-init-display-browser`
- `-display-browser-nb-old`
- `-display-browser-nb`
- `-get-browser`
- `-display-browser-cl`
- `run-main`
- `run-test-with-main`
- `-do-update-breakpoints`
- `debug`
- `connect-debugger`
- `debug-display-browser-old`
- `debug-display-browser`
- `connect-client-debugger`
- `-debug-start-debuggee-main-test`
- `debug-test-with-main`
- `debug-single`
- `-debug-start-debugger-main-test`
- `-debug-start-debugger`
- `-debug-start-debuggee-single`
- `debug-single-main`
- `-pre-debug-fix`
- `-do-debug-fix`
- `debug-fix`
- `-profile-pre72`
- `start-profiled-server`
- `start-profiled-server-extraargs`
- `-profile-test-single-pre72`
- `-profile-check`
- `-do-profile`
- `profile`
- `profile-test-single`
- `profile-test`
- `-profile-start-loadgen`
- `javadoc-build`
- `javadoc-browse`
- `javadoc`
- `-pre-pre-compile-test`
- `-pre-compile-test`
- `-do-compile-test`
- `-post-compile-test`
- `compile-test`
- `-pre-compile-test-single`
- `-do-compile-test-single`
- `-post-compile-test-single`
- `compile-test-single`
- `-pre-test-run`
- `-do-test-run`
- `-post-test-run`
- `test-report`
- `-test-browse`
- `test`
- `-pre-test-run-single`
- `-do-test-run-single`
- `-post-test-run-single`
- `test-single`
- `-do-test-run-single-method`
- `-post-test-run-single-method`
- `test-single-method`
- `-debug-start-debuggee-test`
- `-debug-start-debuggee-test-method`
- `-debug-start-debugger-test`
- `debug-test`
- `debug-test-method`
- `-do-debug-fix-test`
- `debug-fix-test`
- `deps-clean`
- `do-clean`
- `check-clean`
- `undeploy-clean`
- `-post-clean`
- `clean`
- `clean-ear`

### `nbproject/project.xml`
<project> document (129 elements; library×39, file×39, path-in-war×39, root×2, project×1, type×1)

### `src/java/struts.xml`
<struts> document (88 elements; result×44, param×15, action×11, interceptor-ref×6, package×5, struts×1)

**Struts actions**
- `DefLogin` → `com.shop.login.action.UserLogin`
- `*loginCall` → `com.shop.login.action.UserLogin`
- `homeCall` → `com.shop.login.action.UserLogin`
- `statusCgecking` → `com.shop.login.action.UserLogin`
- `*usrMng` → `com.shop.inv.user.action.UserManagement`
- `*usrprofileMng` → `com.shop.inv.user.action.UsrProfileManagement`
- `*addMember` → `com.shop.inv.member.action.MemberManagement`
- `*editViewMember` → `com.shop.inv.member.action.EditAndViewMemberManagement`
- `*childMng` → `com.shop.inv.member.action.ChildrenManagement`
- `*totMemReport` → `com.shop.inv.report.action.MemberReport`
- `*totMemSummary` → `com.shop.inv.report.action.MemberSummary`

### `web/META-INF/context.xml`
<Context> document (1 elements; Context×1)

### `web/WEB-INF/web.xml`
Servlet deployment descriptor: 0 servlets, 1 filters, 1 listeners

**Filters**
- `struts2` → `org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter` on `/*`

**Listeners**
- `com.shop.global.ContextListener`

**Operational settings** (timeouts, pools, limits, schedules): wrong values here cause slowness and timeouts under load.

| Key | Value | File | Read by |
|---|---|---|---|
| `build.generated.dir` | ${build.dir}/generated | `project.properties` |  |
| `build.generated.sources.dir` | ${build.dir}/generated-sources | `project.properties` |  |
| `file.reference.DBPool-5.0.jar` | libs/DBPool-5.0.jar | `project.properties` |  |

## 10. Risk hotspots

Patterns that frequently explain production incidents. These are *leads to check*, not proven defects.

#### Swallowed / ignored exceptions
_A failure here leaves no trace and the flow continues with wrong or missing data._

| Where | File | Catch block |
|---|---|---|
| `ChildrenManagement.Find()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:105` | catch (Exception) - swallowed - no log, no rethrow; broad catch |
| `EditAndViewMemberManagement.Find()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:110` | catch (Exception) - swallowed - no log, no rethrow; broad catch |
| `UserManagement.Find()` | `src/java/com/shop/inv/user/action/UserManagement.java:101` | catch (Exception) - swallowed - no log, no rethrow; broad catch |
| `LogFileCreator.writeInfoToLog()` | `src/java/com/shop/util/LogFileCreator.java:45` | catch (IOException) - EMPTY catch - exception swallowed silently |
| `LogFileCreator.writeErrorToLog()` | `src/java/com/shop/util/LogFileCreator.java:76` | catch (IOException) - EMPTY catch - exception swallowed silently |

#### Shared mutable state
_Singleton beans and statics are shared by all requests: a classic cause of intermittent, load-dependent wrong results._

| Where | File | Detail |
|---|---|---|
| `DBConnection.pool` | `src/java/com/shop/db/DBConnection.java:13` | static mutable field `ConnectionPool pool` - shared by every request/thread |
| `InitConfigValue.DBUSERNAME` | `src/java/com/shop/init/InitConfigValue.java:17` | static mutable field `String DBUSERNAME` - shared by every request/thread |
| `InitConfigValue.DBPASSWORD` | `src/java/com/shop/init/InitConfigValue.java:18` | static mutable field `String DBPASSWORD` - shared by every request/thread |
| `InitConfigValue.DBDRIVER` | `src/java/com/shop/init/InitConfigValue.java:19` | static mutable field `String DBDRIVER` - shared by every request/thread |
| `InitConfigValue.DBURL` | `src/java/com/shop/init/InitConfigValue.java:20` | static mutable field `String DBURL` - shared by every request/thread |
| `InitConfigValue.MINPOOL` | `src/java/com/shop/init/InitConfigValue.java:21` | static mutable field `int MINPOOL` - shared by every request/thread |
| `InitConfigValue.MAXPOOL` | `src/java/com/shop/init/InitConfigValue.java:22` | static mutable field `int MAXPOOL` - shared by every request/thread |
| `InitConfigValue.MAXCON` | `src/java/com/shop/init/InitConfigValue.java:23` | static mutable field `int MAXCON` - shared by every request/thread |
| `InitConfigValue.DBCONNECTIONTIMEOUT` | `src/java/com/shop/init/InitConfigValue.java:24` | static mutable field `int DBCONNECTIONTIMEOUT` - shared by every request/thread |
| `InitConfigValue.DBCONEXPIRTIMEOUT` | `src/java/com/shop/init/InitConfigValue.java:25` | static mutable field `int DBCONEXPIRTIMEOUT` - shared by every request/thread |
| `InitConfigValue.SCONFIGPATH` | `src/java/com/shop/init/InitConfigValue.java:28` | static mutable field `String SCONFIGPATH` - shared by every request/thread |
| `InitConfigValue.LOGPATH` | `src/java/com/shop/init/InitConfigValue.java:29` | static mutable field `String LOGPATH` - shared by every request/thread |
| `InitConfigValue.IMAGE_UPLOAD_PATH` | `src/java/com/shop/init/InitConfigValue.java:31` | static mutable field `String IMAGE_UPLOAD_PATH` - shared by every request/thread |
| `LogFileCreator.path` | `src/java/com/shop/util/LogFileCreator.java:19` | static mutable field `String path` - shared by every request/thread |

#### Most complex methods
_Many branches = many ways to fail; review these first when logic is suspected._

| Method | File | Complexity | Lines |
|---|---|---|---|
| `MemberManagement.doValidation()` | `src/java/com/shop/inv/member/action/MemberManagement.java:136` | 45 | 157 |
| `EditAndViewMemberManagement.doValidation()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:200` | 43 | 157 |
| `UserManagement.doValidation()` | `src/java/com/shop/inv/user/action/UserManagement.java:180` | 20 | 55 |
| `UserManagement.doValidationUpdate()` | `src/java/com/shop/inv/user/action/UserManagement.java:236` | 15 | 41 |
| `UsrProfileManagement.checkAccess()` | `src/java/com/shop/inv/user/action/UsrProfileManagement.java:301` | 13 | 37 |
| `MemberManagement.checkAccess()` | `src/java/com/shop/inv/member/action/MemberManagement.java:324` | 11 | 33 |
| `UserLogin.Logout()` | `src/java/com/shop/login/action/UserLogin.java:145` | 11 | 44 |
| `LoginService.getModulePageByUser()` | `src/java/com/shop/login/service/LoginService.java:87` | 11 | 96 |
| `ChildrenManagement.checkAccess()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:271` | 10 | 31 |
| `EditAndViewMemberManagement.checkAccess()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:399` | 10 | 34 |
| `MemberReport.checkAccess()` | `src/java/com/shop/inv/report/action/MemberReport.java:155` | 10 | 34 |
| `MemberSummary.checkAccess()` | `src/java/com/shop/inv/report/action/MemberSummary.java:125` | 10 | 34 |
| `UserManagement.checkAccess()` | `src/java/com/shop/inv/user/action/UserManagement.java:306` | 10 | 31 |
| `LoginService.getAllPageTask()` | `src/java/com/shop/login/service/LoginService.java:225` | 10 | 101 |

#### Longest methods
_Large methods hide side effects._

| Method | File | Lines | Complexity |
|---|---|---|---|
| `EditAndViewMemberManagement.doValidation()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:200` | 157 | 43 |
| `MemberManagement.doValidation()` | `src/java/com/shop/inv/member/action/MemberManagement.java:136` | 157 | 45 |
| `MemberManagementService.updateData()` | `src/java/com/shop/inv/member/service/MemberManagementService.java:243` | 140 | 8 |
| `MemberManagementService.addData()` | `src/java/com/shop/inv/member/service/MemberManagementService.java:454` | 136 | 7 |
| `MemberManagementService.findData()` | `src/java/com/shop/inv/member/service/MemberManagementService.java:112` | 130 | 8 |
| `MemberManagementService.loadReportData()` | `src/java/com/shop/inv/member/service/MemberManagementService.java:720` | 123 | 7 |
| `LoginService.getAllPageTask()` | `src/java/com/shop/login/service/LoginService.java:225` | 101 | 10 |
| `LoginService.getModulePageByUser()` | `src/java/com/shop/login/service/LoginService.java:87` | 96 | 11 |
| `MemberManagementService.loadData()` | `src/java/com/shop/inv/member/service/MemberManagementService.java:30` | 81 | 9 |

#### Hard-coded URLs, IPs and paths
_These do not change with configuration, so they break when an environment differs._

| Where | File | Detail |
|---|---|---|
| `ContextListener.contextInitialized()` | `src/java/com/shop/global/ContextListener.java:33` | path: C:/my_sys_k/conf/ |
| `ContextListener.contextInitialized()` | `src/java/com/shop/global/ContextListener.java:35` | path: /opt/my_sys_k/conf/ |

#### Console output (System.out / printStackTrace)
_Often missing from application logs, so evidence can be lost._

| Where | File | Detail |
|---|---|---|
| `DBConnection.createDbPool()` | `src/java/com/shop/db/DBConnection.java:22` | stdout: Creating a non-expiring icbs database connection pool |
| `DBConnection.createDbPool()` | `src/java/com/shop/db/DBConnection.java:24` | stdout: Creating an expiring icbs database connection pool with expir timeout [{InitConfigValue.DBCONEXPIRTIM…}] (s) |
| `DBConnection.createDbPool()` | `src/java/com/shop/db/DBConnection.java:50` | stdout: Establish the database connection.... |
| `ContextListener.contextInitialized()` | `src/java/com/shop/global/ContextListener.java:40` | stdout: Create Db Pool:{InitConfigValue.DBPASSWORD} |
| `ContextListener.contextInitialized()` | `src/java/com/shop/global/ContextListener.java:43` | stdout: Create Db Pool sucess.. |
| `ContextListener.contextInitialized()` | `src/java/com/shop/global/ContextListener.java:47` | printStackTrace |
| `ContextListener.contextDestroyed()` | `src/java/com/shop/global/ContextListener.java:56` | printStackTrace |
| `AccessControlInterceptor.intercept()` | `src/java/com/shop/interceptor/AccessControlInterceptor.java:86` | stdout: Class:{className} Method:{method} Msg:{DBConnection.checkDBPoolStatus()} |
| `AccessControlInterceptor.intercept()` | `src/java/com/shop/interceptor/AccessControlInterceptor.java:90` | printStackTrace |
| `ChildrenManagement.getModel()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:60` | printStackTrace |
| `ChildrenManagement.List()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:94` | printStackTrace |
| `ChildrenManagement.Find()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:102` | stdout: getChildId::{inputBean.getChildId()} |
| `ChildrenManagement.Update()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:114` | stdout: getChildId::{inputBean.getChildId()} |
| `ChildrenManagement.Update()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:130` | printStackTrace |
| `ChildrenManagement.Delete()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:151` | printStackTrace |
| `ChildrenManagement.Add()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:173` | printStackTrace |
| `ChildrenManagement.doValidation()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:182` | stdout: >1:{userBean.getChildName()} |
| `ChildrenManagement.doValidationUpdate()` | `src/java/com/shop/inv/member/action/ChildrenManagement.java:213` | stdout: >1:{userBean.getUpchildName()} |
| `EditAndViewMemberManagement.execute()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:48` | stdout: calling....1 |
| `EditAndViewMemberManagement.getModel()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:55` | stdout: calling....2 |
| `EditAndViewMemberManagement.getModel()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:63` | printStackTrace |
| `EditAndViewMemberManagement.List()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:99` | printStackTrace |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:119` | stdout: Update...getMemId:{inputBean.getMemId()} |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:120` | stdout: Update...getMemIdDes:{inputBean.getMemIdDes()} |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:121` | stdout: Update...getMemIdUp:{inputBean.getMemIdUp()} |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:124` | stdout: update validation sucess |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:127` | stdout: me_img :{me_img} |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:128` | stdout: fam_img :{fam_img} |
| `EditAndViewMemberManagement.Update()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:141` | printStackTrace |
| `EditAndViewMemberManagement.Delete()` | `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java:162` | printStackTrace |

… +86 more

#### Blocking calls
_Blocks a request thread; under load this exhausts the pool._

| Where | File | Detail |
|---|---|---|
| `DBConnection.createDbPool()` | `src/java/com/shop/db/DBConnection.java:47` | Thread.sleep() blocks the request thread |

_98 `catch (Exception/Throwable)` blocks exist; they can mask the real error type._

## 11. Front-end JavaScript

### `web/resources/js/TreeMenu.js`
- Purpose: TreeMenu v1.4 Copyright (c) 2006 Mackley F. Pexton. All rights reserved. This is free software for individual, educational, and non-profit use provided that this copyright notice appears on all copie…
- Functions (25): `make_tree_menu(id,omit_symbols,no_save_state,singular,no_setup)` (L146), `TreeMenu(ul_id)` (L161), `TreeMenu.toggle(e)` (L184), `TreeMenu.show(ul)` (L200), `TreeMenu.hide(ul)` (L209), `TreeMenu.show_all(ul)` (L218), `TreeMenu.hide_all(ul)` (L227), `TreeMenu.save_state(ul)` (L236), `TreeMenu.reset(ul)` (L243), `TreeMenu.get_ref(id)` (L251), `TreeMenu.get_top_ul(e)` (L256), `TreeMenu.get_li(e)` (L261), `TreeMenu.prototype.configure()` (L271), `TreeMenu.prototype.setup_symbols()` (L284), `symbol.onclick()` (L305), `TreeMenu.prototype.is_last_item(e)` (L334), `TreeMenu.prototype.get_menu_states()` (L342), `TreeMenu.prototype.save_menu_states()` (L348), `TreeMenu.prototype.reset_menu_states()` (L367), `TreeMenu.prototype.add_remove_class(e,add_class,remove_class)` (L375), `TreeMenu.prototype.show_menu(ul,li,e)` (L385), `TreeMenu.prototype.hide_menu(ul,li,e)` (L400), `TreeMenu.prototype.hide_menus_except(li)` (L415), `setCookie(name, value, expires, path, domain, secure)` (L430), `getCookie(name)` (L438)

### `web/resources/js/div.js`
- Uses: jQuery
- Functions (3): `loadXMLDoc(id)` (L1), `xmlhttp.onreadystatechange()` (L19), `searchUsersISA()` (L32)

### `web/resources/js/login.js`
- Functions (2): `showPopUp(el)` (L2), `closePopUp(el)` (L12)

**Third-party / minified JS (not analysed):** `web/resources/js/amcharts.js`, `web/resources/js/jquery-2.1.js`, `web/resources/js/jquery.blockUI.js`, `web/resources/js/jquery.cookie.js`, `web/resources/js/jquery.flot.js`, `web/resources/js/jquery.flot.pie.js`, `web/resources/js/jquery.js`, `web/resources/js/pie.js`, `web/resources/template/themes/mytheme/external/jquery/jquery.js`, `web/resources/template/themes/mytheme/jquery-ui.js`

## 12. Class catalog

### Package `com.shop.db`

#### DBConnection — class
- File: `src/java/com/shop/db/DBConnection.java` (L12)
- Methods:
  - `static void createDbPool()`
    - Calls: `Class.forName`, `<chain>.newInstance`, `DriverManager.registerDriver`, `Thread.sleep`, `dbConnectionClose`
    - Declares throws: `Exception`
  - `static void dbConnectionClose(Connection con)`
    - Calls: `con.close`
    - Declares throws: `Exception`
  - `static String checkDBPoolStatus()`
    - Declares throws: `Exception`
- Plus 3 trivial accessor/boilerplate methods
- Uses (1): `InitConfigValue`
- Used by (10): `AccessControlInterceptor`, `ChildrenService`, `ContextListener`, `LoginService`, `MemberManagementService`, `MemberReportService`, `MemberSummaryService`, `UserManagementService`, `UsrProfileManagementService`, `Util`

### Package `com.shop.global`

#### ContextListener — class · Filter / Listener / Interceptor
- File: `src/java/com/shop/global/ContextListener.java` (L21)
- Implements `ServletContextListener`
- Methods:
  - `void contextInitialized(ServletContextEvent sce)`
    - Calls: `<chain>.startsWith`, `InitConfigValueReader.readConfigValues`, `DBConnection.createDbPool`, `<chain>.log`, `e.printStackTrace`
  - `void contextDestroyed(ServletContextEvent sce)`
    - Calls: `e.printStackTrace`
- Uses (5): `DBConnection`, `InitConfigValue`, `InitConfigValueReader`, `LogFileCreator`, `SessionUserBean`

### Package `com.shop.init`

#### Cast — class
- File: `src/java/com/shop/init/Cast.java` (L12)
- Constants: `KALAR="01"`, `MARAV="02"`, `AGAMU="03"`

#### InitConfigValue — class
- File: `src/java/com/shop/init/InitConfigValue.java` (L13)
- Used by (9): `ContextListener`, `DBConnection`, `InitConfigValueReader`, `LogFileCreator`, `MemberManagement`, `MemberManagementService`, `Test`, `UserLogin`, `UserManagement`

#### InitConfigValueReader — class
- File: `src/java/com/shop/init/InitConfigValueReader.java` (L7)
- Methods:
  - `static void readConfigValues()`
    - Calls: `<chain>.trim`, `Integer.parseInt`
    - Declares throws: `Exception`
- Uses (1): `InitConfigValue`
- Used by (1): `ContextListener`

#### Module — class
- File: `src/java/com/shop/init/Module.java` (L17)
- Purpose: Title :Module Description : Company :Epic Lanka (pvt) Ltd
- Constants: `USER_MANAGEMENT="01"`, `SALE_MANAGEMENT="02"`, `LOGIN_MANAGEMENT="13"`
- Used by (2): `UserManagement`, `UsrProfileManagement`

#### Operation — class
- File: `src/java/com/shop/init/Operation.java` (L12)
- Constants: `ADD="01"`, `DELETE="02"`, `UPDATE="03"`, `VIEW="04"`, `CANCEL="05"`, `APPROVE="06"`, `REJECT="07"`, `SAVE="09"`

#### PageVarList — class
- File: `src/java/com/shop/init/PageVarList.java` (L13)
- Constants: `USER_MANAGEMENT="0101"`, `USER_PROFILE_MANAGEMENT="0102"`, `ADD_MEMBER_MANAGEMENT="0201"`, `EDITVIEW_MEMBER_MANAGEMENT="0202"`, `CHILDREN_MANAGEMENT="0203"`, `MEMBER_REPORT_DETAIL="0301"`, `MEMBER_SUMMARY="0302"`
- Used by (7): `ChildrenManagement`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserManagement`, `UsrProfileManagement`

#### Status — class
- File: `src/java/com/shop/init/Status.java` (L11)
- Constants: `ACTIVE=1`, `INACTIVE=2`, `DELETED=3`
- Used by (8): `ChildrenService`, `EswitchEchoTest`, `MemberManagementService`, `MemberReportService`, `UserLogin`, `UserManagementService`, `UsrProfileManagementService`, `Util`

#### TaskVarList — class
- File: `src/java/com/shop/init/TaskVarList.java` (L13)
- Constants: `VIEW="01"`, `ADD="02"`, `UPDATE="03"`, `DELETE="04"`, `DOWNLOAD="05"`, `PWRESET="06"`
- Used by (7): `ChildrenManagement`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserManagement`, `UsrProfileManagement`

### Package `com.shop.interceptor`

#### AccessControlInterceptor — class · Filter / Listener / Interceptor
- File: `src/java/com/shop/interceptor/AccessControlInterceptor.java` (L25)
- Implements `Interceptor`
- Methods:
  - `void destroy()`
  - `void init()`
  - `String intercept(ActionInvocation ai)`
    - Calls: `ai.invoke`, `<chain>.checkAccess`, `DBConnection.checkDBPoolStatus`, `ex.printStackTrace`
    - Declares throws: `Exception`
- Uses (6): `AccessControlService`, `DBConnection`, `LogFileCreator`, `SessionUserBean`, `SessionVarlist`, `UserLogin`

### Package `com.shop.inv.member.action`

#### ChildrenManagement — class · Controller / Web
- File: `src/java/com/shop/inv/member/action/ChildrenManagement.java` (L33)
- Extends `ActionSupport` · implements `ModelDriven<ChildrenInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `ChildrenInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `String List()`
    - Calls: `service.loadData`, `Math.ceil`, `ex.printStackTrace`
  - `String Find()`
    - Calls: `service.findData`
    - Failure points: ⚠ swallows exceptions (L105)
  - `String Update()`
    - Calls: `doValidationUpdate`, `service.updateData`, `ex.printStackTrace`
  - `String Delete()`
    - Calls: `service.deleteData`, `ex.printStackTrace`
  - `String Add()`
    - Calls: `doValidation`, `ex.printStackTrace`
  - `boolean checkAccess(String method, int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 10, 31 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (13): `AccessControlService`, `ChildrenBean`, `ChildrenInputBean`, `ChildrenService`, `Common`, `LogFileCreator`, `PageVarList`, `PasswordValidator`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`, `Util`

#### EditAndViewMemberManagement — class · Controller / Web
- File: `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java` (L34)
- Extends `ActionSupport` · implements `ModelDriven<MemberManagementInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `MemberManagementInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `String List()`
    - Calls: `service.loadData`, `Math.ceil`, `ex.printStackTrace`
  - `String Find()`
    - Calls: `service.findData`
    - Failure points: ⚠ swallows exceptions (L110)
  - `String Update()`
    - Calls: `doValidation`, `MemberManagement.imageUpload`, `service.updateData`, `ex.printStackTrace`
  - `String Delete()`
    - Calls: `service.deleteData`, `ex.printStackTrace`
  - `String Download()`
    - Calls: `service.loadReportData`, `service.loadReportDataChildrens`, `ISOUtil.zeropad`, `e.printStackTrace`
    - Declares throws: `Exception`
  - `boolean checkAccess(String method, int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 10, 34 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (14): `AccessControlService`, `Common`, `LogFileCreator`, `MemberBean`, `MemberManagement`, `MemberManagementInputBean`, `MemberManagementService`, `PageVarList`, `PasswordValidator`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`, `Util`

#### MemberManagement — class · Controller / Web
- File: `src/java/com/shop/inv/member/action/MemberManagement.java` (L43)
- Extends `ActionSupport` · implements `ModelDriven<MemberManagementInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `MemberManagementInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `String Add()`
    - Calls: `doValidation`, `MemberManagement.imageUpload`, `ex.printStackTrace`
  - `static boolean imageUpload(File Img_file,String outFile)`
    - Calls: `ImageIO.read`, `resized.createGraphics`, `g2d.drawImage`, `g2d.dispose`, `ImageIO.write`
  - `boolean checkAccess(String method, int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 11, 33 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (14): `AccessControlService`, `Common`, `InitConfigValue`, `LogFileCreator`, `MemberBean`, `MemberManagementInputBean`, `MemberManagementService`, `PageVarList`, `PasswordValidator`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`, `Util`
- Used by (1): `EditAndViewMemberManagement`

### Package `com.shop.inv.member.bean`

#### ChildrenBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/member/bean/ChildrenBean.java` (L12)
- Fields: `chile_id: String`, `mem_id: String`, `mem_id_des: String`, `child_name: String`, `child_dob: String`, `child_gender: String`, `child_merrid_status: String`, `childEdu: String`, `childAddr: String`, `childPhone: String`, `childMobile: String`, `childEmail: String`, `fullCount: long`
- Plus 26 trivial accessor/boilerplate methods
- Used by (5): `ChildrenInputBean`, `ChildrenManagement`, `ChildrenService`, `MemberManagementInputBean`, `MemberManagementService`

#### ChildrenInputBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/member/bean/ChildrenInputBean.java` (L20)
- Fields: `searchname: String`, `search: boolean`, `memberload: String`, `memberloadList: TreeMap<Integer,String>`, `childName: String`, `childDob: String`, `childGender: String`, `childGenderList: Map<String,String>`, `childMerStatus: String`, `childMerStatusList: Map<String,String>`, `childEdu: String`, `childAddr: String`, `childPhone: String`, `childMobile: String`, `childEmail: String`, `message: String`, `success: boolean`, `childId: String`, `upmemberload: String`, `upchildName: String`, `upchildDob: String`, `upchildGender: String`, `upchildMerStatus: String`, `upchildEdu: String`, `upchildAddr: String` …
- Plus 86 trivial accessor/boilerplate methods
- Uses (2): `ChildrenBean`, `Util`
- Used by (2): `ChildrenManagement`, `ChildrenService`

#### MemberBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/member/bean/MemberBean.java` (L12)
- Fields: `memId: String`, `memIdDes: String`, `memName: String`, `memNic: String`, `memDob: String`, `phoneNo: String`, `memBornPlace: String`, `memCast: String`, `CUS_NAME: String`, `status: String`, `regDate: String`, `fullCount: long`
- Plus 24 trivial accessor/boilerplate methods
- Used by (4): `EditAndViewMemberManagement`, `MemberManagement`, `MemberManagementInputBean`, `MemberManagementService`

#### MemberManagementInputBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/member/bean/MemberManagementInputBean.java` (L19)
- Fields: `searchname: String`, `search: boolean`, `memIdUp: String`, `memId: String`, `memIdDes: String`, `memName: String`, `memNic: String`, `memDob: String`, `phoneNo: String`, `mobileNo: String`, `email: String`, `qualification: String`, `perAddress: String`, `temAddress: String`, `memBornPlace: String`, `memCast: String`, `memCastList: HashMap<String,String>`, `memSubCast: String`, `memIslife: String`, `memIslifeList: Map<String,String>`, `memExpdate: String`, `noOfBrother: String`, `noOfSister: String`, `jobTitle: String`, `jobAddress: String` …
- Plus 182 trivial accessor/boilerplate methods
- Uses (3): `ChildrenBean`, `MemberBean`, `Util`
- Used by (4): `EditAndViewMemberManagement`, `MemberManagement`, `MemberManagementService`, `Util`

### Package `com.shop.inv.member.service`

#### ChildrenService — class · Service
- File: `src/java/com/shop/inv/member/service/ChildrenService.java` (L26)
- Methods:
  - `List<ChildrenBean> loadData(ChildrenInputBean bean, String orderBy, int from, int rows)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`, `ISOUtil.zeropad`
    - Declares throws: `Exception`
    - SQL: R dma_member_children; R dma_member_children
    - Failure points: throws `e`
  - `void findData(ChildrenInputBean inputBean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R dma_member_children
    - Failure points: throws `e`
  - `boolean updateData(ChildrenInputBean inputBean)`
    - Calls: `con.prepareStatement`, `preStat.executeUpdate`, `res.close`
    - Declares throws: `Exception`
    - SQL: W dma_member_children
    - Failure points: throws `e`
  - `boolean deleteData(ChildrenInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeUpdate`, `con.commit`, `con.rollback`, `prepSt.close`
    - Declares throws: `Exception`
    - SQL: W dma_member_children
    - Failure points: throws `e`
  - `boolean addData(ChildrenInputBean inputBean)`
    - Calls: `con.prepareStatement`, `preStat.executeUpdate`, `con.commit`, `preStat.close`
    - Declares throws: `Exception`
    - SQL: W dma_member_children
    - Failure points: throws `e`
  - `void getmemberloadList(ChildrenInputBean inputBean)`
    - Calls: `connection.prepareStatement`, `ps.executeQuery`, `result.next`, `ISOUtil.zeropad`, `result.close`
    - Declares throws: `Exception`
    - SQL: R dma_member
    - Failure points: throws `ex`
- Uses (5): `ChildrenBean`, `ChildrenInputBean`, `DBConnection`, `Status`, `Util`
- Used by (1): `ChildrenManagement`

#### MemberManagementService — class · Service
- File: `src/java/com/shop/inv/member/service/MemberManagementService.java` (L28)
- Methods:
  - `List<MemberBean> loadData(MemberManagementInputBean bean, String orderBy, int from, int rows)`
    - Calls: `con.prepareStatement`, `<chain>.toUpperCase`, `prepSt.executeQuery`, `res.next`, `res.close` …
    - Declares throws: `Exception`
    - SQL: R dma_member; R dma_member
    - Failure points: throws `e`
  - `void findData(MemberManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `ISOUtil.zeropad`, `res.close`
    - Declares throws: `Exception`
    - Failure points: throws `e`
  - `boolean updateData(MemberManagementInputBean inputBean,boolean mem_img,boolean fam_img)`
    - Calls: `con.prepareStatement`, `prepSt.executeUpdate`, `res.close`
    - Declares throws: `Exception`
    - SQL: W dma_member
    - Failure points: throws `e`
  - `boolean deleteData(MemberManagementInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeUpdate`, `con.commit`, `con.rollback`, `prepSt.close`
    - Declares throws: `Exception`
    - SQL: W dma_member
    - Failure points: throws `e`
  - `boolean checkUserName(String username)`
    - Calls: `connection.prepareStatement`, `ps.executeQuery`, `result.next`, `result.close`
    - Declares throws: `Exception`
    - SQL: R web_user
    - Failure points: throws `ex`
  - `boolean addData(MemberManagementInputBean inputBean,boolean mem_img,boolean fam_img)`
    - Calls: `con.prepareStatement`, `Util.convertStringToDBDate`, `Integer.parseInt`, `preStat.executeUpdate`, `con.commit` …
    - Declares throws: `Exception`
    - SQL: W dma_member
    - Failure points: throws `e`
  - `void getCastList(MemberManagementInputBean inputBean)`
    - Calls: `connection.prepareStatement`, `ps.executeQuery`, `result.next`, `result.close`
    - Declares throws: `Exception`
    - SQL: R DMA_CAST
    - Failure points: throws `ex`
  - `String getlastMemId()`
    - Calls: `connection.prepareStatement`, `ps.executeQuery`, `result.next`, `lastMemIdStr.concat`, `ISOUtil.zeropad` …
    - Declares throws: `Exception`
    - SQL: R dma_member
    - Failure points: throws `ex`
  - `List<ChildrenBean> loadReportDataChildrens(MemberManagementInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `SQLException`, `Exception`
    - SQL: R dma_member_children
    - Failure points: throws `e`
  - `void loadReportData(MemberManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `ISOUtil.zeropad`, `res.close`
    - Declares throws: `Exception`
    - Failure points: throws `e`
- Uses (7): `ChildrenBean`, `DBConnection`, `InitConfigValue`, `MemberBean`, `MemberManagementInputBean`, `Status`, `Util`
- Used by (2): `EditAndViewMemberManagement`, `MemberManagement`

### Package `com.shop.inv.report.action`

#### MemberReport — class · Controller / Web
- File: `src/java/com/shop/inv/report/action/MemberReport.java` (L36)
- Extends `ActionSupport` · implements `ModelDriven<MemberReportInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `MemberReportInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `String List()`
    - Calls: `service.loadData`, `Math.ceil`, `ex.printStackTrace`
  - `String Download()`
    - Calls: `service.loadReportData`, `e.printStackTrace`
    - Declares throws: `Exception`
  - `boolean checkAccess(String method, int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 10, 34 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (12): `AccessControlService`, `Common`, `LogFileCreator`, `MemberReportBean`, `MemberReportInputBean`, `MemberReportService`, `PageVarList`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`, `Util`

#### MemberSummary — class · Controller / Web
- File: `src/java/com/shop/inv/report/action/MemberSummary.java` (L30)
- Extends `ActionSupport` · implements `ModelDriven<MemberSummaryInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `MemberSummaryInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `String List()`
    - Calls: `service.loadData`, `Math.ceil`, `ex.printStackTrace`
  - `boolean checkAccess(String method, int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 10, 34 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (11): `AccessControlService`, `Common`, `LogFileCreator`, `MemberSummaryBean`, `MemberSummaryInputBean`, `MemberSummaryService`, `PageVarList`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`

### Package `com.shop.inv.report.bean`

#### MemberReportBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/report/bean/MemberReportBean.java` (L12)
- Fields: `memIdDes: String`, `memId: String`, `memName: String`, `perAddr: String`, `temAddr: String`, `offAddr: String`, `tpNum: String`, `mobileNum: String`, `offPhnNum: String`, `memCast: String`, `regDate: String`, `fullCount: long`
- Plus 24 trivial accessor/boilerplate methods
- Used by (3): `MemberReport`, `MemberReportInputBean`, `MemberReportService`

#### MemberReportInputBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/report/bean/MemberReportInputBean.java` (L18)
- Fields: `memId: String`, `memCastID: String`, `memCastList: Map<String,String>`, `search: boolean`, `vadd: boolean`, `vupdate: boolean`, `vdelete: boolean`, `vdownload: boolean`, `vresetpass: boolean`, `gridModel: List<MemberReportBean>`, `rows: Integer`, `page: Integer`, `total: Integer`, `records: Long`, `sord: String`, `sidx: String`, `searchField: String`, `searchString: String`, `searchOper: String`, `parameterMap: Map`, `reportdatalist: List<MemberReportBean>`, `fileName: String`
- Plus 44 trivial accessor/boilerplate methods
- Uses (2): `MemberReportBean`, `Util`
- Used by (2): `MemberReport`, `MemberReportService`

#### MemberSummaryBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/report/bean/MemberSummaryBean.java` (L12)
- Fields: `castName: String`, `castCount: String`, `fullCount: long`
- Plus 6 trivial accessor/boilerplate methods
- Used by (3): `MemberSummary`, `MemberSummaryInputBean`, `MemberSummaryService`

#### MemberSummaryInputBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/report/bean/MemberSummaryInputBean.java` (L15)
- Fields: `vadd: boolean`, `vupdate: boolean`, `vdelete: boolean`, `vdownload: boolean`, `vresetpass: boolean`, `gridModel: List<MemberSummaryBean>`, `rows: Integer`, `page: Integer`, `total: Integer`, `records: Long`, `sord: String`, `sidx: String`, `searchField: String`, `searchString: String`, `searchOper: String`
- Plus 30 trivial accessor/boilerplate methods
- Uses (1): `MemberSummaryBean`
- Used by (2): `MemberSummary`, `MemberSummaryService`

### Package `com.shop.inv.report.service`

#### MemberReportService — class · Service
- File: `src/java/com/shop/inv/report/service/MemberReportService.java` (L25)
- Methods:
  - `List<MemberReportBean> loadData(MemberReportInputBean bean, String orderBy, int from, int rows)`
    - Calls: `con.prepareStatement`, `<chain>.toUpperCase`, `prepSt.executeQuery`, `res.next`, `res.close` …
    - Declares throws: `Exception`
    - SQL: R dma_member; R dma_member
    - Failure points: throws `e`
  - `void loadReportData(MemberReportInputBean inputBean)`
    - Calls: `con.prepareStatement`, `<chain>.toUpperCase`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R dma_member
    - Failure points: throws `e`
- Uses (5): `DBConnection`, `MemberReportBean`, `MemberReportInputBean`, `Status`, `Util`
- Used by (1): `MemberReport`

#### MemberSummaryService — class · Service
- File: `src/java/com/shop/inv/report/service/MemberSummaryService.java` (L23)
- Methods:
  - `List<MemberSummaryBean> loadData(MemberSummaryInputBean bean, String orderBy, int from, int rows)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R dma_cast; R dma_member
    - Failure points: throws `e`
- Uses (4): `DBConnection`, `MemberSummaryBean`, `MemberSummaryInputBean`, `Util`
- Used by (1): `MemberSummary`

### Package `com.shop.inv.user.action`

#### UserManagement — class · Controller / Web
- File: `src/java/com/shop/inv/user/action/UserManagement.java` (L34)
- Extends `ActionSupport` · implements `ModelDriven<UserManagementInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `UserManagementInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `String List()`
    - Calls: `service.loadData`, `Math.ceil`, `ex.printStackTrace`
  - `String Find()`
    - Calls: `service.findData`
    - Failure points: ⚠ swallows exceptions (L101)
  - `String Update()`
    - Calls: `doValidationUpdate`, `service.updateData`, `ex.printStackTrace`
  - `String Delete()`
    - Calls: `service.deleteData`, `ex.printStackTrace`
  - `String Add()`
    - Calls: `doValidation`, `ex.printStackTrace`
  - `boolean checkAccess(String method, int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 10, 31 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (15): `AccessControlService`, `Common`, `InitConfigValue`, `LogFileCreator`, `Module`, `PageVarList`, `PasswordValidator`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`, `UserBean`, `UserManagementInputBean`, `UserManagementService`, `Util`

#### UsrProfileManagement — class · Controller / Web
- File: `src/java/com/shop/inv/user/action/UsrProfileManagement.java` (L33)
- Extends `ActionSupport` · implements `ModelDriven<UsrProfileManagementInputBean>`, `AccessControlService`
- Methods:
  - `SessionUserBean getSub()`
  - `String execute()`
  - `String List()`
    - Calls: `service.loadData`, `Math.ceil`, `ex.printStackTrace`
  - `String Add()`
    - Calls: `doValidationAdd`, `ex.printStackTrace`
  - `String Find()`
    - Calls: `service.findData`, `e.printStackTrace`
  - `String Update()`
    - Calls: `service.updateData`, `ex.printStackTrace`
  - `String Delete()`
    - Calls: `Integer.parseInt`, `service.deleteData`, `ex.printStackTrace`
  - `String loadModuleSection()`
    - Calls: `e.printStackTrace`
  - `String loadSectionTask()`
    - Calls: `e.printStackTrace`
  - `String UpdateTask()`
    - Calls: `doValidationUpdate`, `service.updateTaskData`, `ex.printStackTrace`
  - `UsrProfileManagementInputBean getModel()`
    - Calls: `ex.printStackTrace`
  - `boolean checkAccess(String method,int userRole)`
    - Calls: `applyUserPrivileges`, `<chain>.checkMethodAccess`
    - Complexity 13, 37 lines — many branches, check conditions carefully
- Plus 1 trivial accessor/boilerplate methods
- Uses (13): `AccessControlService`, `Common`, `LogFileCreator`, `Module`, `PageVarList`, `SessionUserBean`, `SystemMessage`, `TaskBean`, `TaskVarList`, `UsrProfileBean`, `UsrProfileManagementInputBean`, `UsrProfileManagementService`, `Util`

### Package `com.shop.inv.user.bean`

#### UserBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/user/bean/UserBean.java` (L12)
- Fields: `profileId: String`, `name: String`, `username: String`, `email: String`, `mobile: String`, `profile: String`, `profilename: String`, `status: String`, `regDate: String`, `fullCount: long`
- Plus 20 trivial accessor/boilerplate methods
- Used by (3): `UserManagement`, `UserManagementInputBean`, `UserManagementService`

#### UserManagementInputBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/user/bean/UserManagementInputBean.java` (L9)
- Fields: `searchname: String`, `search: boolean`, `username: String`, `name: String`, `password: String`, `repassword: String`, `userPro: String`, `userProList: HashMap<String,String>`, `email: String`, `mobile: String`, `message: String`, `success: boolean`, `upusername: String`, `upusernamecopy: String`, `upname: String`, `upuserPro: String`, `upstatus: String`, `upemail: String`, `upmobile: String`, `upstatusList: Map<Integer,String>`, `vadd: boolean`, `vupdate: boolean`, `vdelete: boolean`, `vdownload: boolean`, `vresetpass: boolean` …
- Plus 70 trivial accessor/boilerplate methods
- Uses (2): `UserBean`, `Util`
- Used by (2): `UserManagement`, `UserManagementService`

#### UsrProfileBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/user/bean/UsrProfileBean.java` (L13)
- Fields: `profileId: String`, `profileName: String`, `status: String`, `regDate: String`, `fullCount: long`
- Plus 10 trivial accessor/boilerplate methods
- Used by (3): `UsrProfileManagement`, `UsrProfileManagementInputBean`, `UsrProfileManagementService`

#### UsrProfileManagementInputBean — class · Entity / Model / DTO
- File: `src/java/com/shop/inv/user/bean/UsrProfileManagementInputBean.java` (L19)
- Fields: `profilename: String`, `search: boolean`, `upprofilename: String`, `upprofileId: String`, `upmoduleId: String`, `moduleIdList: HashMap<String,String>`, `uppageId: String`, `pageIdList: HashMap<String,String>`, `currentBox: List<String>`, `taskList: Map<String, String>`, `newBox: List<String>`, `selectedtaskList: Map<String, String>`, `message: String`, `success: boolean`, `upestatus: String`, `upstatusList: Map<Integer,String>`, `upeprofilename: String`, `upeprofileId: String`, `vadd: boolean`, `vupdate: boolean`, `vdelete: boolean`, `vdownload: boolean`, `vresetpass: boolean`, `gridModel: List<UsrProfileBean>`, `rows: Integer` …
- Plus 66 trivial accessor/boilerplate methods
- Uses (2): `UsrProfileBean`, `Util`
- Used by (2): `UsrProfileManagement`, `UsrProfileManagementService`

### Package `com.shop.inv.user.service`

#### UserManagementService — class · Service
- File: `src/java/com/shop/inv/user/service/UserManagementService.java` (L22)
- Methods:
  - `List<UserBean> loadData(UserManagementInputBean bean, String orderBy, int from, int rows)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`, `<chain>.toUpperCase`
    - Declares throws: `Exception`
    - SQL: R web_user; R WEB_USER
    - Failure points: throws `e`
  - `void findData(UserManagementInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER
    - Failure points: throws `e`
  - `boolean updateData(UserManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `<chain>.toLowerCase`, `Integer.parseInt`, `prepSt.executeUpdate`, `res.close`
    - Declares throws: `Exception`
    - SQL: W WEB_USER
    - Failure points: throws `e`
  - `boolean deleteData(UserManagementInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeUpdate`, `con.commit`, `con.rollback`, `prepSt.close`
    - Declares throws: `Exception`
    - SQL: W WEB_USER
    - Failure points: throws `e`
  - `boolean checkUserName(String username)`
    - Calls: `connection.prepareStatement`, `ps.executeQuery`, `result.next`, `result.close`
    - Declares throws: `Exception`
    - SQL: R web_user
    - Failure points: throws `ex`
  - `boolean addData(UserManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `<chain>.toLowerCase`, `Util.generateHash`, `preStat.executeUpdate`, `con.commit` …
    - Declares throws: `Exception`
    - SQL: W web_user
    - Failure points: throws `e`
  - `void getProfileList(UserManagementInputBean inputBean)`
    - Calls: `connection.prepareStatement`, `ps.executeQuery`, `result.next`, `result.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER_PROFILE
    - Failure points: throws `ex`
- Uses (5): `DBConnection`, `Status`, `UserBean`, `UserManagementInputBean`, `Util`
- Used by (1): `UserManagement`

#### UsrProfileManagementService — class · Service
- File: `src/java/com/shop/inv/user/service/UsrProfileManagementService.java` (L27)
- Methods:
  - `List<UsrProfileBean> loadData(UsrProfileManagementInputBean bean, String orderBy, int from, int rows)`
    - Calls: `con.prepareStatement`, `<chain>.toUpperCase`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER_PROFILE; R WEB_USER_PROFILE
    - Failure points: throws `e`
  - `void findData(UsrProfileManagementInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER_PROFILE
    - Failure points: throws `e`
  - `boolean updateTaskData(UsrProfileManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `Integer.parseInt`, `prepSt.executeUpdate`, `prepSt.close`, `<chain>.substring`
    - Declares throws: `Exception`
    - SQL: W WEB_USER_PROFILE_PRIVILAGE; W WEB_USER_PROFILE_PRIVILAGE
    - Failure points: throws `e`
  - `boolean deleteData(UsrProfileManagementInputBean bean)`
    - Calls: `con.prepareStatement`, `prepSt.executeUpdate`, `prepSt.close`
    - Declares throws: `Exception`
    - SQL: W WEB_USER_PROFILE_PRIVILAGE; W WEB_USER_PROFILE
    - Failure points: throws `e`
  - `Map<String,String> getModuleList()`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R MT_MODULES
    - Failure points: throws `e`
  - `Map<String,String> getPageList(String modulId)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R MT_SECTION
    - Failure points: throws `e`
  - `Map<String,String> getTaskList(String pageId)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R MT_SECTION_TASK
    - Failure points: throws `e`
  - `boolean addData(UsrProfileManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `preStat.executeUpdate`, `preStat.close`
    - Declares throws: `Exception`
    - SQL: W WEB_USER_PROFILE
    - Failure points: throws `e`
  - `void getTaskListsLoad(UsrProfileManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `prepSt.executeQuery`, `res.next`, `res.close`, `Integer.parseInt` …
    - Declares throws: `Exception`
    - SQL: R MT_SECTION_TASK; R WEB_USER_PROFILE_PRIVILAGE
    - Failure points: throws `e`
  - `boolean profilenameAlready(String profilename)`
    - Calls: `connection.prepareStatement`, `profilename.toUpperCase`, `ps.executeQuery`, `result.next`, `result.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER_PROFILE
    - Failure points: throws `ex`
  - `boolean updateData(UsrProfileManagementInputBean inputBean)`
    - Calls: `con.prepareStatement`, `Integer.parseInt`, `prepSt.executeUpdate`, `res.close`
    - Declares throws: `Exception`
    - SQL: W WEB_USER_PROFILE
    - Failure points: throws `e`
- Uses (5): `DBConnection`, `Status`, `UsrProfileBean`, `UsrProfileManagementInputBean`, `Util`
- Used by (1): `UsrProfileManagement`

### Package `com.shop.login.action`

#### UserLogin — class · Controller / Web
- File: `src/java/com/shop/login/action/UserLogin.java` (L43)
- Extends `ActionSupport` · implements `Action`, `ModelDriven<UserLoginBean>`
- Methods:
  - `String execute()`
  - `String loginCheck()`
    - Calls: `Util.generateHash`, `sessionPrevious.invalidate`, `ex.printStackTrace`
  - `String homeFunction()`
    - Declares throws: `Exception`
  - `UserLoginBean getModel()`
  - `String Logout()`
    - Calls: `session.removeAttribute`, `session.invalidate`, `e.printStackTrace`
    - Complexity 11, 44 lines — many branches, check conditions carefully
- Uses (13): `HomeValues`, `InitConfigValue`, `LogFileCreator`, `LoginService`, `ModuleBean`, `PageBean`, `SessionUserBean`, `SessionVarlist`, `Status`, `SystemMessage`, `TaskBean`, `UserLoginBean`, `Util`
- Used by (1): `AccessControlInterceptor`

### Package `com.shop.login.bean`

#### ConfigurationBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/ConfigurationBean.java` (L12)
- Fields: `logBackUpPath: String`, `servicePort: int`
- Plus 4 trivial accessor/boilerplate methods

#### HomeValues — class
- File: `src/java/com/shop/login/bean/HomeValues.java` (L11)
- Plus 12 trivial accessor/boilerplate methods
- Used by (1): `UserLogin`

#### ModuleBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/ModuleBean.java` (L11)
- Fields: `MODULE_ID: String`, `MODULE_NAME: String`
- Plus 4 trivial accessor/boilerplate methods
- Used by (3): `LoginService`, `ModuleComparator`, `UserLogin`

#### PageBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/PageBean.java` (L11)
- Fields: `PAGE_ID: String`, `MODULE: String`, `PAGE_NAME: String`, `PAGE_URL: String`
- Plus 8 trivial accessor/boilerplate methods
- Used by (2): `LoginService`, `UserLogin`

#### SessionUserBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/SessionUserBean.java` (L11)
- Fields: `username: String`, `UserProfileId: int`, `name: String`, `adStatus: int`, `status: int`, `userType: String`, `logFilePath: String`, `currentSessionId: String`, `qrEncMsg: String`
- Plus 18 trivial accessor/boilerplate methods
- Used by (11): `AccessControlInterceptor`, `ChildrenManagement`, `ContextListener`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserLogin`, `UserManagement`, `UsrProfileManagement`, `Util`

#### TaskBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/TaskBean.java` (L13)
- Fields: `TASK_ID: String`, `TASK_NAME: String`
- Plus 4 trivial accessor/boilerplate methods
- Used by (10): `ChildrenManagement`, `Common`, `EditAndViewMemberManagement`, `LoginService`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserLogin`, `UserManagement`, `UsrProfileManagement`

#### UserLoginBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/UserLoginBean.java` (L16)
- Fields: `userName: String`, `password: String`, `name: String`, `profileId: int`, `status: int`, `dbPassword: String`, `imei: String`, `message: String`, `success: boolean`
- Plus 18 trivial accessor/boilerplate methods
- Used by (2): `LoginService`, `UserLogin`

#### UserProfileModuleBean — class · Entity / Model / DTO
- File: `src/java/com/shop/login/bean/UserProfileModuleBean.java` (L11)
- Fields: `PROFILE_ID: int`, `MODULE_ID: String`, `PAGE_ID: String`
- Plus 6 trivial accessor/boilerplate methods

### Package `com.shop.login.service`

#### LoginService — class · Service
- File: `src/java/com/shop/login/service/LoginService.java` (L25)
- Methods:
  - `boolean getDbUserDetails(UserLoginBean ulb)`
    - Calls: `con.prepareStatement`, `<chain>.toLowerCase`, `perSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER
    - Failure points: throws `ex`
  - `Map<ModuleBean, List<PageBean>> getModulePageByUser(int profileId)`
    - Calls: `con.prepareStatement`, `perSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R MT_MODULES
    - Failure points: throws `ex`
    - Complexity 11, 96 lines — many branches, check conditions carefully
  - `List<String> getUserprofilePageidList(int dBuserProfile)`
    - Calls: `con.prepareStatement`, `perSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `SQLException`, `Exception`
    - SQL: R WEB_USER_PROFILE_PRIVILAGE
    - Failure points: throws `ex`
  - `HashMap<String, List<TaskBean>> getAllPageTask(int profileID)`
    - Calls: `con.prepareStatement`, `perSt.executeQuery`, `res.next`, `res.close`
    - Declares throws: `Exception`
    - SQL: R WEB_USER_PROFILE_PRIVILAGE
    - Failure points: throws `ex`
    - Complexity 10, 101 lines — many branches, check conditions carefully
- Uses (5): `DBConnection`, `ModuleBean`, `PageBean`, `TaskBean`, `UserLoginBean`
- Used by (1): `UserLogin`

### Package `com.shop.util`

#### AccessControlService — interface · Service
- File: `src/java/com/shop/util/AccessControlService.java` (L11)
- Methods:
  - `boolean checkAccess(String method,int userRole)`
- Used by (8): `AccessControlInterceptor`, `ChildrenManagement`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserManagement`, `UsrProfileManagement`

#### Common — class
- File: `src/java/com/shop/util/Common.java` (L18)
- Methods:
  - `boolean checkMethodAccess(String task, String page, HttpSession sessionk)`
    - Calls: `profilePageidList.contains`, `checkTaskAvaliable`, `e.printStackTrace`
  - `List<TaskBean> getUserTaskListByPage(String page, HttpServletRequest request)`
    - Calls: `pageMap.keySet`, `<chain>.iterator`, `itr.next`
- Uses (2): `LogFileCreator`, `TaskBean`
- Used by (7): `ChildrenManagement`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserManagement`, `UsrProfileManagement`

#### EswitchEchoTest — class · Test
- File: `src/java/com/shop/util/EswitchEchoTest.java` (L15)
- Methods:
  - `static void checkEcho()`
- Uses (1): `Status`

#### ExcelCommon — class
- File: `src/java/com/shop/util/ExcelCommon.java` (L22)
- Methods:
  - `static XSSFCellStyle getFontBoldedCell(XSSFWorkbook workbook)`
    - Calls: `workbook.createFont`, `workbook.createCellStyle`
  - `static XSSFCellStyle getFontBoldedUnderlinedCell(XSSFWorkbook workbook)`
    - Calls: `workbook.createFont`, `workbook.createCellStyle`
  - `static XSSFCellStyle getColumnHeadeCell(XSSFWorkbook workbook)`
    - Calls: `workbook.createFont`, `workbook.createCellStyle`
  - `static XSSFCellStyle getRowColumnCell(XSSFWorkbook workbook)`
    - Calls: `workbook.createCellStyle`
  - `static XSSFCellStyle getAligneCell(XSSFWorkbook workbook, XSSFCellStyle cellStyle, short alignment)` — return XSSFCellSytyle witch contains the alignment according to the parameter value ' short alignment ' contain and if XSSFCellStyle parameter is null then it create new style with the alignment that came with the align…
    - Calls: `workbook.createCellStyle`, `style.cloneStyleFrom`
  - `static ByteArrayOutputStream zipFiles(File[] listFiles)`
    - Calls: `fileInputStream.read`, `zipOutputStream.write`, `zipOutputStream.closeEntry`, `fileInputStream.close`, `zipOutputStream.finish` …
    - Declares throws: `Exception`
    - Failure points: throws `e`

#### LogFileCreator — class
- File: `src/java/com/shop/util/LogFileCreator.java` (L17)
- Methods:
  - `static void writeInfoToLog(String msg)`
    - Calls: `bw.write`, `bw.newLine`, `bw.flush`, `ioe.printStackTrace`, `bw.close`
    - Declares throws: `Exception`
    - Failure points: throws `ioe`; ⚠ swallows exceptions (L45)
  - `static void writeErrorToLog(Throwable aThrowable)`
    - Calls: `bw.write`, `bw.newLine`, `bw.flush`, `ioe.printStackTrace`, `bw.close`
    - Failure points: ⚠ swallows exceptions (L76)
- Uses (2): `InitConfigValue`, `Util`
- Used by (11): `AccessControlInterceptor`, `ChildrenManagement`, `Common`, `ContextListener`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserLogin`, `UserManagement`, `UsrProfileManagement`

#### ModuleComparator — class
- File: `src/java/com/shop/util/ModuleComparator.java` (L16)
- Implements `Comparator<ModuleBean>`
- Methods:
  - `int compare(ModuleBean _first, ModuleBean _second)`
    - Calls: `<chain>.compareTo`
- Uses (1): `ModuleBean`

#### PasswordValidator — class
- File: `src/java/com/shop/util/PasswordValidator.java` (L15)
- Used by (4): `ChildrenManagement`, `EditAndViewMemberManagement`, `MemberManagement`, `UserManagement`

#### SessionVarlist — class
- File: `src/java/com/shop/util/SessionVarlist.java` (L13)
- Constants: `USERMAP="USERMAP"`
- Used by (2): `AccessControlInterceptor`, `UserLogin`

#### SystemMessage — class
- File: `src/java/com/shop/util/SystemMessage.java` (L11)
- Constants: `COMMON_ERROR_PROCESS="Error occurred while processing"`, `LOGIN_MSG="User login successful "`, `LOGOUT_MSG="User logout successful "`, `LOGIN_INVALID="Invalid user login"`, `LOGIN_INVALID_PW="Invalid user password"`, `LOGIN_INVALID_BANKUSER="Invalid bank user login"`, `USR_NAME_EMPTY="Empty name"`, `USR_NAME_INVALID="Invalid name"`
- Used by (8): `ChildrenManagement`, `EditAndViewMemberManagement`, `MemberManagement`, `MemberReport`, `MemberSummary`, `UserLogin`, `UserManagement`, `UsrProfileManagement`

#### Test — class · Test
- File: `src/java/com/shop/util/Test.java` (L31)
- Methods:
  - `static void main(String[] args)`
    - Calls: `Util.encryptionPass`, `Util.decryptionPass`, `e.printStackTrace`
- Uses (2): `InitConfigValue`, `Util`

#### Util — class · Utility
- File: `src/java/com/shop/util/Util.java` (L42)
- Constants: `ENCRYPTION_KEY="kreshanKey111111"`, `PATTERN=Pattern.compile( "^(([01]?\\d\\d?\|2[0-…`
- Methods:
  - `static String encryptionPass(String accNumber)`
    - Calls: `cipher.init`, `cipher.doFinal`, `ISOUtil.hexString`
    - Declares throws: `Exception`
  - `static String decryptionPass(String encrypted)`
    - Calls: `cipher.init`, `ISOUtil.hexString`, `cipher.doFinal`
    - Declares throws: `Exception`
  - `static boolean validateNAME(String text)`
    - Calls: `text.matches`
    - Declares throws: `Exception`
  - `static boolean validateNUMBER(String numericString)`
    - Calls: `numericString.matches`
    - Declares throws: `Exception`
  - `static boolean validateEMAIL(String email)`
    - Calls: `email.matches`
    - Declares throws: `Exception`
  - `static boolean validatePHONENO(String numericString)`
    - Calls: `numericString.matches`
    - Declares throws: `Exception`
  - `static boolean validatePORT(String numericString)`
    - Calls: `numericString.matches`
    - Declares throws: `Exception`
  - `static boolean validateMOBILE(String numericString)`
    - Calls: `numericString.matches`
    - Declares throws: `Exception`
  - `static boolean validateAMOUNT(String numericString)`
    - Calls: `numericString.matches`
    - Declares throws: `Exception`
  - `static boolean validateNIC(String nic)`
    - Calls: `nic.matches`
  - `static boolean validationNICPP(String nicpp)`
    - Calls: `nicpp.matches`
  - `static boolean validateSPECIALCHAR(String specialChars)`
    - Calls: `specialChars.matches`
    - Declares throws: `Exception`
  - `static boolean validateDESCRIPTION(String text)`
    - Calls: `text.matches`
  - `static boolean validateIP(final String ip)`
    - Calls: `PATTERN.matcher`, `<chain>.matches`
  - `static boolean validateURL(String text)`
    - Calls: `text.matches`
  - `static boolean validateSTRING(String text)`
    - Calls: `text.matches`
    - Declares throws: `Exception`
  - `static boolean validateImageFileName(String filenamei)`
    - Calls: `filename.substring`, `filename.lastIndexOf`, `extension.toUpperCase`, `e.printStackTrace`
    - Declares throws: `Exception`
  - `static Date convertStringToDate(String dateString)`
    - Calls: `format.parse`
    - Declares throws: `Exception`
  - `static java.sql.Date convertStringToDBDate(String date)`
    - Calls: `formtter.parse`, `sql.Date`
    - Declares throws: `Exception`
  - `static Map<String, String> getMemIslifeList()`
  - `static Map<String, String> getMerriedList()`
  - `static Map<String, String> getNumberList()`
  - `static Map<String, String> getChildGenderdList()`
  - `static Map<String, String> getChildMerriedStatusList()`
  - `static Map<K, V> sortByValues(Map<K, V> map)`
    - Calls: `map.entrySet`, `Collections.sort`, `compare`, `<chain>.compareTo`
  - … +10 more methods
- Plus 2 trivial accessor/boilerplate methods
- Uses (4): `DBConnection`, `MemberManagementInputBean`, `SessionUserBean`, `Status`
- Used by (20): `ChildrenInputBean`, `ChildrenManagement`, `ChildrenService`, `EditAndViewMemberManagement`, `LogFileCreator`, `MemberManagement`, `MemberManagementInputBean`, `MemberManagementService`, `MemberReport`, `MemberReportInputBean`, `MemberReportService`, `MemberSummaryService`, `Test`, `UserLogin`, `UserManagement` …

## 13. Dependency insights

### Most depended-on classes (change with care)

| Class | Layer | Used by (files) |
|---|---|---|
| `Util` | Utility | 20 |
| `LogFileCreator` | Other | 11 |
| `SessionUserBean` | Entity / Model / DTO | 11 |
| `TaskBean` | Entity / Model / DTO | 10 |
| `DBConnection` | Other | 10 |
| `InitConfigValue` | Other | 9 |
| `SystemMessage` | Other | 8 |
| `AccessControlService` | Service | 8 |
| `Status` | Other | 8 |
| `Common` | Other | 7 |
| `TaskVarList` | Other | 7 |
| `PageVarList` | Other | 7 |
| `ChildrenBean` | Entity / Model / DTO | 5 |
| `PasswordValidator` | Other | 4 |
| `MemberManagementInputBean` | Entity / Model / DTO | 4 |

### Not referenced by other scanned Java files
_May be framework-wired (Spring/XML/reflection), entry points, or dead code — verify before deleting._

`AccessControlInterceptor`, `Cast`, `ConfigurationBean`, `ContextListener`, `ExcelCommon`, `ModuleComparator`, `Operation`, `UserProfileModuleBean`

## 14. File index

| File | Type | Lines | Summary |
|---|---|---|---|
| `build.xml` | xml | 71 | Ant build `Startup_WEB` default target `default` |
| `nbproject/ant-deploy.xml` | xml | 111 | Ant build `` default target `-deploy-ant` |
| `nbproject/build-impl.xml` | xml | 1520 | Ant build `Startup_WEB-impl` default target `default` |
| `nbproject/genfiles.properties` | properties | 8 | 6 keys |
| `nbproject/project.properties` | properties | 173 | 122 keys |
| `nbproject/project.xml` | xml | 175 | <project> document (129 elements; library×39, file×39, path-in-war×39, root×2, project×1, type×1) |
| `src/java/com/shop/db/DBConnection.java` | java | 78 | class DBConnection |
| `src/java/com/shop/global/ContextListener.java` | java | 60 | class ContextListener [Filter / Listener / Interceptor] |
| `src/java/com/shop/init/Cast.java` | java | 16 | class Cast |
| `src/java/com/shop/init/InitConfigValue.java` | java | 32 | class InitConfigValue |
| `src/java/com/shop/init/InitConfigValueReader.java` | java | 29 | class InitConfigValueReader |
| `src/java/com/shop/init/Module.java` | java | 31 | class Module — Title :Module Description : Company :Epic Lanka (pvt) Ltd |
| `src/java/com/shop/init/Operation.java` | java | 31 | class Operation |
| `src/java/com/shop/init/PageVarList.java` | java | 25 | class PageVarList |
| `src/java/com/shop/init/Status.java` | java | 23 | class Status |
| `src/java/com/shop/init/TaskVarList.java` | java | 22 | class TaskVarList |
| `src/java/com/shop/interceptor/AccessControlInterceptor.java` | java | 99 | class AccessControlInterceptor [Filter / Listener / Interceptor] |
| `src/java/com/shop/inv/member/action/ChildrenManagement.java` | java | 304 | class ChildrenManagement [Controller / Web] |
| `src/java/com/shop/inv/member/action/EditAndViewMemberManagement.java` | java | 435 | class EditAndViewMemberManagement [Controller / Web] |
| `src/java/com/shop/inv/member/action/MemberManagement.java` | java | 358 | class MemberManagement [Controller / Web] |
| `src/java/com/shop/inv/member/bean/ChildrenBean.java` | java | 138 | class ChildrenBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/member/bean/ChildrenInputBean.java` | java | 440 | class ChildrenInputBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/member/bean/MemberBean.java` | java | 136 | class MemberBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/member/bean/MemberManagementInputBean.java` | java | 939 | class MemberManagementInputBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/member/service/ChildrenService.java` | java | 319 | class ChildrenService [Service] |
| `src/java/com/shop/inv/member/service/MemberManagementService.java` | java | 843 | class MemberManagementService [Service] |
| `src/java/com/shop/inv/report/action/MemberReport.java` | java | 191 | class MemberReport [Controller / Web] |
| `src/java/com/shop/inv/report/action/MemberSummary.java` | java | 163 | class MemberSummary [Controller / Web] |
| `src/java/com/shop/inv/report/bean/MemberReportBean.java` | java | 135 | class MemberReportBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/report/bean/MemberReportInputBean.java` | java | 240 | class MemberReportInputBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/report/bean/MemberSummaryBean.java` | java | 44 | class MemberSummaryBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/report/bean/MemberSummaryInputBean.java` | java | 159 | class MemberSummaryInputBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/report/service/MemberReportService.java` | java | 166 | class MemberReportService [Service] |
| `src/java/com/shop/inv/report/service/MemberSummaryService.java` | java | 86 | class MemberSummaryService [Service] |
| `src/java/com/shop/inv/user/action/UserManagement.java` | java | 338 | class UserManagement [Controller / Web] |
| `src/java/com/shop/inv/user/action/UsrProfileManagement.java` | java | 338 | class UsrProfileManagement [Controller / Web] |
| `src/java/com/shop/inv/user/bean/UserBean.java` | java | 116 | class UserBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/user/bean/UserManagementInputBean.java` | java | 391 | class UserManagementInputBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/user/bean/UsrProfileBean.java` | java | 63 | class UsrProfileBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/user/bean/UsrProfileManagementInputBean.java` | java | 352 | class UsrProfileManagementInputBean [Entity / Model / DTO] |
| `src/java/com/shop/inv/user/service/UserManagementService.java` | java | 398 | class UserManagementService [Service] |
| `src/java/com/shop/inv/user/service/UsrProfileManagementService.java` | java | 490 | class UsrProfileManagementService [Service] |
| `src/java/com/shop/login/action/UserLogin.java` | java | 191 | class UserLogin [Controller / Web] |
| `src/java/com/shop/login/bean/ConfigurationBean.java` | java | 33 | class ConfigurationBean [Entity / Model / DTO] |
| `src/java/com/shop/login/bean/HomeValues.java` | java | 69 | class HomeValues |
| `src/java/com/shop/login/bean/ModuleBean.java` | java | 31 | class ModuleBean [Entity / Model / DTO] |
| `src/java/com/shop/login/bean/PageBean.java` | java | 50 | class PageBean [Entity / Model / DTO] |
| `src/java/com/shop/login/bean/SessionUserBean.java` | java | 104 | class SessionUserBean [Entity / Model / DTO] |
| `src/java/com/shop/login/bean/TaskBean.java` | java | 34 | class TaskBean [Entity / Model / DTO] |
| `src/java/com/shop/login/bean/UserLoginBean.java` | java | 114 | class UserLoginBean [Entity / Model / DTO] |
| `src/java/com/shop/login/bean/UserProfileModuleBean.java` | java | 39 | class UserProfileModuleBean [Entity / Model / DTO] |
| `src/java/com/shop/login/service/LoginService.java` | java | 329 | class LoginService [Service] |
| `src/java/com/shop/util/AccessControlService.java` | java | 13 | interface AccessControlService [Service] |
| `src/java/com/shop/util/Common.java` | java | 71 | class Common |
| `src/java/com/shop/util/EswitchEchoTest.java` | java | 57 | class EswitchEchoTest [Test] |
| `src/java/com/shop/util/ExcelCommon.java` | java | 135 | class ExcelCommon |
| `src/java/com/shop/util/LogFileCreator.java` | java | 121 | class LogFileCreator |
| `src/java/com/shop/util/ModuleComparator.java` | java | 22 | class ModuleComparator |
| `src/java/com/shop/util/PasswordValidator.java` | java | 145 | class PasswordValidator |
| `src/java/com/shop/util/SessionVarlist.java` | java | 15 | class SessionVarlist |
| `src/java/com/shop/util/SystemMessage.java` | java | 170 | class SystemMessage |
| `src/java/com/shop/util/Test.java` | java | 55 | class Test [Test] |
| `src/java/com/shop/util/Util.java` | java | 369 | class Util [Utility] |
| `src/java/log4j.properties` | properties | 30 | 7 keys |
| `src/java/struts.xml` | xml | 150 | <struts> document (88 elements; result×44, param×15, action×11, interceptor-ref×6, package×5, struts×1) |
| `web/META-INF/context.xml` | xml | 2 | <Context> document (1 elements; Context×1) |
| `web/WEB-INF/web.xml` | xml | 32 | Servlet deployment descriptor: 0 servlets, 1 filters, 1 listeners |
| `web/resources/js/TreeMenu.js` | js | 452 | TreeMenu v1.4 Copyright (c) 2006 Mackley F. Pexton. All rights reserved. This is free software for individual, educational, and non-profit… |
| `web/resources/js/amcharts.js` | js | 380 | third-party/minified (minified (very long lines)) |
| `web/resources/js/div.js` | js | 36 | 3 functions, 0 AJAX calls |
| `web/resources/js/jquery-2.1.js` | js | 5 | third-party/minified (by path/name) |
| `web/resources/js/jquery.blockUI.js` | js | 620 | third-party/minified (by path/name) |
| `web/resources/js/jquery.cookie.js` | js | 114 | third-party/minified (by path/name) |
| `web/resources/js/jquery.flot.js` | js | 3169 | third-party/minified (by path/name) |
| `web/resources/js/jquery.flot.pie.js` | js | 821 | third-party/minified (by path/name) |
| `web/resources/js/jquery.js` | js | 9473 | third-party/minified (by path/name) |
| `web/resources/js/login.js` | js | 18 | 2 functions, 0 AJAX calls |
| `web/resources/js/pie.js` | js | 10 | third-party/minified (minified (very long lines)) |
| `web/resources/template/themes/mytheme/external/jquery/jquery.js` | js | 9790 | third-party/minified (by path/name) |
| `web/resources/template/themes/mytheme/jquery-ui.js` | js | 16582 | third-party/minified (by path/name) |
