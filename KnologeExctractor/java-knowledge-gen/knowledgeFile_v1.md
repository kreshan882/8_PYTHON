# Knowledge file — S5_SpringLearn_MongoDb

> Auto-generated on 2026-10-07 14:02 from `S5_SpringLearn_MongoDb` by java-knowledge-gen. Structure is extracted statically (regex based, no compilation) — treat it as a map, and verify details in the source.

## Contents

- [1. Project overview](#1-project-overview)
- [2. Technology stack and build](#2-technology-stack-and-build)
- [3. Architecture layers](#3-architecture-layers)
- [4. Entry points and HTTP endpoints](#4-entry-points-and-http-endpoints)
- [5. Configuration](#5-configuration)
- [6. Class catalog](#6-class-catalog)
- [7. Dependency insights](#7-dependency-insights)
- [8. File index](#8-file-index)

## 1. Project overview

| Extension | Files | Lines |
|---|---|---|
| `.java` | 14 | 470 |
| `.properties` | 1 | 18 |
| `.xml` | 1 | 64 |
| **Total** | **16** | **552** |

- Java types: **14** (10 class, 4 interface) in **6** packages

### Packages

| Package | Types | Classes |
|---|---|---|
| `com.kre.mongo` | 2 | SpringLearnMongoDbApplication, SpringLearnMongoDbApplicationTests |
| `com.kre.mongo.collection` | 3 | Address, Person, Photo |
| `com.kre.mongo.config` | 1 | SpringFoxConfig |
| `com.kre.mongo.controller` | 2 | PersonController, PhotoController |
| `com.kre.mongo.repository` | 2 | PersonRepository, PhotoRepository |
| `com.kre.mongo.service` | 4 | PersonService, PersonServiceImpl, PhotoService, PhotoServiceImpl |

## 2. Technology stack and build

| Technology (from imports) | Files using it |
|---|---|
| Spring Data | 7 |
| Spring Framework | 7 |
| Spring MVC | 4 |
| Lombok | 3 |
| Jackson | 2 |
| Spring Boot | 2 |
| Springfox | 2 |
| JUnit | 1 |

### Build: `pom.xml`
Maven jar: com.kre:S5_SpringLearn_MongoDb:0.0.1

**Coordinates**
- groupId `com.kre`, artifactId `S5_SpringLearn_MongoDb`, version `0.0.1`, packaging `jar`
- name: S5_SpringLearn_MongoDb
- description: S5_SpringLearn_MongoDb
- parent: `org.springframework.boot:spring-boot-starter-parent:2.7.2`

**Properties**
- `java.version` = `11`

**Dependencies**
- `org.springframework.boot:spring-boot-starter-data-mongodb`
- `org.springframework.boot:spring-boot-starter-web`
- `org.springframework.boot:spring-boot-starter-test` (test)
- `org.projectlombok:lombok`
- `io.springfox:springfox-boot-starter` 3.0.0
- `io.springfox:springfox-swagger-ui` 3.0.0

**Build plugins**
- `spring-boot-maven-plugin`

## 3. Architecture layers

| Layer | Types | Examples |
|---|---|---|
| Service | 4 | PersonService, PersonServiceImpl, PhotoService, PhotoServiceImpl |
| Configuration | 2 | SpringFoxConfig, SpringLearnMongoDbApplication |
| Entity / Model / DTO | 2 | Person, Photo |
| Controller / Web | 2 | PersonController, PhotoController |
| Repository / DAO / Mapper | 2 | PersonRepository, PhotoRepository |
| Test | 1 | SpringLearnMongoDbApplicationTests |
| Other | 1 | Address |

## 4. Entry points and HTTP endpoints

### HTTP endpoints

| Method | Path | Handler | File |
|---|---|---|---|
| GET | `/person` | `PersonController.getPersonStartWith()` | `src/main/java/com/kre/mongo/controller/PersonController.java:28` |
| POST | `/person` | `PersonController.save()` | `src/main/java/com/kre/mongo/controller/PersonController.java:23` |
| GET | `/person/age` | `PersonController.getByPersonAge()` | `src/main/java/com/kre/mongo/controller/PersonController.java:39` |
| GET | `/person/oldestPerson` | `PersonController.getOldestPerson()` | `src/main/java/com/kre/mongo/controller/PersonController.java:57` |
| GET | `/person/populationByCity` | `PersonController.getPopulationByCity()` | `src/main/java/com/kre/mongo/controller/PersonController.java:62` |
| GET | `/person/searchPagable` | `PersonController.searchPersonPagaple()` | `src/main/java/com/kre/mongo/controller/PersonController.java:46` |
| DELETE | `/person/{id}` | `PersonController.delete()` | `src/main/java/com/kre/mongo/controller/PersonController.java:33` |
| POST | `/photo` | `PhotoController.addPhoto()` | `src/main/java/com/kre/mongo/controller/PhotoController.java:25` |
| GET | `/photo/{id}` | `PhotoController.downloadPhoto()` | `src/main/java/com/kre/mongo/controller/PhotoController.java:31` |

### Other entry points

| Kind | Where | File |
|---|---|---|
| Spring Boot application | `SpringLearnMongoDbApplication` | `src/main/java/com/kre/mongo/SpringLearnMongoDbApplication.java` |
| main() | `SpringLearnMongoDbApplication` | `src/main/java/com/kre/mongo/SpringLearnMongoDbApplication.java` |

## 5. Configuration

### `src/main/resources/application.properties`
11 keys

| Key | Value | Read by |
|---|---|---|
| `server.port` | 8080 |  |
| `spring.data.mongodb.authentication-database` | admin |  |
| `spring.data.mongodb.username` | kreshan |  |
| `spring.data.mongodb.password` | *** |  |
| `spring.data.mongodb.database` | demoK |  |
| `spring.data.mongodb.port` | 27017 |  |
| `spring.data.mongodb.host` | localhost |  |
| `spring.mvc.pathmatch.matching-strategy` | ANT_PATH_MATCHER |  |
| `spring.servlet.multipart.max-file-size` | 256MB |  |
| `spring.servlet.multipart.max-request-size` | 256MB |  |
| `spring.servlet.multipart.enabled` | true |  |

## 6. Class catalog

### Package `com.kre.mongo`

#### SpringLearnMongoDbApplication — class · Configuration
- File: `src/main/java/com/kre/mongo/SpringLearnMongoDbApplication.java` (L10)
- Annotations: `@SpringBootApplication` `@EnableSwagger2`
- Methods:
  - `static void main(String[] args)`

#### SpringLearnMongoDbApplicationTests — class · Test
- File: `src/test/java/com/kre/mongo/SpringLearnMongoDbApplicationTests.java` (L7)
- Annotations: `@SpringBootTest`
- Methods:
  - `void contextLoads()` — (@Test)

### Package `com.kre.mongo.collection`

#### Address — class
- File: `src/main/java/com/kre/mongo/collection/Address.java` (L12)
- Annotations: `@Data` `@NoArgsConstructor` `@AllArgsConstructor` `@Builder`
- Used by (1): `Person`

#### Person — class · Entity / Model / DTO
- File: `src/main/java/com/kre/mongo/collection/Person.java` (L17)
- Annotations: `@Data` `@Builder` `@Document(collection = "person")` `@JsonInclude(JsonInclude.Include.NON_NULL)`
- Fields: `personId: String`, `firstName: String`, `lastName: String`, `age: Integer`, `hobbies: List<String>`, `addresses: List<Address>`
- Uses (1): `Address`
- Used by (4): `PersonController`, `PersonRepository`, `PersonService`, `PersonServiceImpl`

#### Photo — class · Entity / Model / DTO
- File: `src/main/java/com/kre/mongo/collection/Photo.java` (L14)
- Annotations: `@Data` `@Document(collection = "photo")` `@JsonInclude(JsonInclude.Include.NON_NULL)`
- Fields: `id: String`, `title: String`, `photo: Binary`
- Used by (4): `PhotoController`, `PhotoRepository`, `PhotoService`, `PhotoServiceImpl`

### Package `com.kre.mongo.config`

#### SpringFoxConfig — class · Configuration
- File: `src/main/java/com/kre/mongo/config/SpringFoxConfig.java` (L12)
- Annotations: `@Configuration`
- Methods:
  - `Docket api()` — (@Bean)

### Package `com.kre.mongo.controller`

#### PersonController — class · Controller / Web
- File: `src/main/java/com/kre/mongo/controller/PersonController.java` (L17)
- Annotations: `@RestController` `@RequestMapping("/person")`
- Injected: `PersonService personService`
- Methods:
  - `String save(Person person)` — **POST /person**
  - `List<Person> getPersonStartWith(String name)` — **GET /person**
  - `void delete(String id)` — **DELETE /person/{id}**
  - `List<Person> getByPersonAge(Integer minAge, Integer maxAge)` — **GET /person/age**
  - `Page<Person> searchPersonPagaple(String name,Integer minAge, Integer maxAge,String city, Integer page,Integer size)` — **GET /person/searchPagable**
  - `List<Document> getOldestPerson()` — **GET /person/oldestPerson**
  - `List<Document> getPopulationByCity()` — **GET /person/populationByCity**
- Uses (2): `Person`, `PersonService`

#### PhotoController — class · Controller / Web
- File: `src/main/java/com/kre/mongo/controller/PhotoController.java` (L19)
- Annotations: `@RestController` `@RequestMapping("/photo")`
- Injected: `PhotoService photoService`
- Methods:
  - `String addPhoto(MultipartFile image)` — **POST /photo**
  - `ResponseEntity<Resource> downloadPhoto(String id)` — **GET /photo/{id}**
- Uses (2): `Photo`, `PhotoService`

### Package `com.kre.mongo.repository`

#### PersonRepository — interface · Repository / DAO / Mapper
- File: `src/main/java/com/kre/mongo/repository/PersonRepository.java` (L12)
- Annotations: `@Repository`
- Extends `MongoRepository<Person,String>`
- Methods:
  - `List<Person> findByFirstNameStartsWith(String name)`
  - `List<Person> findPersonByAgeBetween(Integer min, Integer max)` — (@Query)
- Uses (1): `Person`
- Used by (1): `PersonServiceImpl`

#### PhotoRepository — interface · Repository / DAO / Mapper
- File: `src/main/java/com/kre/mongo/repository/PhotoRepository.java` (L9)
- Annotations: `@Repository`
- Extends `MongoRepository<Photo, String>`
- Uses (1): `Photo`
- Used by (1): `PhotoServiceImpl`

### Package `com.kre.mongo.service`

#### PersonService — interface · Service
- File: `src/main/java/com/kre/mongo/service/PersonService.java` (L11)
- Methods:
  - `String save(Person person)`
  - `void delete(String id)`
  - `List<Person> getByPersonAge(Integer minAge, Integer maxAge)`
  - `Page<Person> search(String name, Integer minAge, Integer maxAge, String city, Pageable pageable)`
- Plus 3 trivial accessor/boilerplate methods
- Uses (1): `Person`
- Used by (2): `PersonController`, `PersonServiceImpl`

#### PersonServiceImpl — class · Service
- File: `src/main/java/com/kre/mongo/service/PersonServiceImpl.java` (L23)
- Annotations: `@Service`
- Implements `PersonService`
- Injected: `PersonRepository personRepository`, `MongoTemplate mongoTemplate`
- Methods:
  - `String save(Person person)`
  - `List<Person> getPersonStartWith(String name)`
  - `void delete(String id)`
  - `List<Person> getByPersonAge(Integer minAge, Integer maxAge)`
  - `Page<Person> search(String name, Integer minAge, Integer maxAge, String city, Pageable pageable)`
  - `List<Document> getOldestPersonByCity()`
  - `List<Document> getPopulationByCity()`
- Uses (3): `Person`, `PersonRepository`, `PersonService`

#### PhotoService — interface · Service
- File: `src/main/java/com/kre/mongo/service/PhotoService.java` (L9)
- Methods:
  - `String addPhoto(String originalFilename, MultipartFile image)`
- Plus 1 trivial accessor/boilerplate methods
- Uses (1): `Photo`
- Used by (2): `PhotoController`, `PhotoServiceImpl`

#### PhotoServiceImpl — class · Service
- File: `src/main/java/com/kre/mongo/service/PhotoServiceImpl.java` (L15)
- Annotations: `@Service`
- Implements `PhotoService`
- Injected: `PhotoRepository photoRepository`
- Methods:
  - `String addPhoto(String originalFilename, MultipartFile image)`
  - `Photo getPhoto(String id)`
- Uses (3): `Photo`, `PhotoRepository`, `PhotoService`

## 7. Dependency insights

### Most depended-on classes (change with care)

| Class | Layer | Used by (files) |
|---|---|---|
| `Photo` | Entity / Model / DTO | 4 |
| `Person` | Entity / Model / DTO | 4 |
| `PhotoService` | Service | 2 |
| `PersonService` | Service | 2 |
| `PhotoRepository` | Repository / DAO / Mapper | 1 |
| `PersonRepository` | Repository / DAO / Mapper | 1 |
| `Address` | Other | 1 |

## 8. File index

| File | Type | Lines | Summary |
|---|---|---|---|
| `pom.xml` | xml | 64 | Maven jar: com.kre:S5_SpringLearn_MongoDb:0.0.1 |
| `src/main/java/com/kre/mongo/SpringLearnMongoDbApplication.java` | java | 16 | class SpringLearnMongoDbApplication [Configuration] |
| `src/main/java/com/kre/mongo/collection/Address.java` | java | 17 | class Address |
| `src/main/java/com/kre/mongo/collection/Person.java` | java | 26 | class Person [Entity / Model / DTO] |
| `src/main/java/com/kre/mongo/collection/Photo.java` | java | 20 | class Photo [Entity / Model / DTO] |
| `src/main/java/com/kre/mongo/config/SpringFoxConfig.java` | java | 26 | class SpringFoxConfig [Configuration] |
| `src/main/java/com/kre/mongo/controller/PersonController.java` | java | 65 | class PersonController [Controller / Web] |
| `src/main/java/com/kre/mongo/controller/PhotoController.java` | java | 40 | class PhotoController [Controller / Web] |
| `src/main/java/com/kre/mongo/repository/PersonRepository.java` | java | 26 | interface PersonRepository [Repository / DAO / Mapper] |
| `src/main/java/com/kre/mongo/repository/PhotoRepository.java` | java | 10 | interface PhotoRepository [Repository / DAO / Mapper] |
| `src/main/java/com/kre/mongo/service/PersonService.java` | java | 25 | interface PersonService [Service] |
| `src/main/java/com/kre/mongo/service/PersonServiceImpl.java` | java | 138 | class PersonServiceImpl [Service] |
| `src/main/java/com/kre/mongo/service/PhotoService.java` | java | 13 | interface PhotoService [Service] |
| `src/main/java/com/kre/mongo/service/PhotoServiceImpl.java` | java | 35 | class PhotoServiceImpl [Service] |
| `src/main/resources/application.properties` | properties | 18 | 11 keys |
| `src/test/java/com/kre/mongo/SpringLearnMongoDbApplicationTests.java` | java | 13 | class SpringLearnMongoDbApplicationTests [Test] |
