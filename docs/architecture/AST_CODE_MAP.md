# AST Code Map (`poojabasker20/springboot-hello-world` @ `main`)


---

> *Auto-generated artifact used by Agentic SDLC pipeline for context grounding.*


---

### Class: `Application` (`src/main/java/com/nordea/demo/helloworld/Application.java`)
- **Annotations**: `@SpringBootApplication`
- **Methods / Endpoints**:
  - **Method**: `void main(String[] args)` (Annotations: ``)

---

### Record: `Greeting` (`src/main/java/com/nordea/demo/helloworld/Greeting.java`)
- **Methods / Endpoints**:
  - **Method**: `Greeting of(String recipient)` (Annotations: ``)
- **Fields / Components**:
  - **Record Components**: `(
    String message,
    String recipient
)`

---

### Class: `GreetingController` (`src/main/java/com/nordea/demo/helloworld/GreetingController.java`)
- **Annotations**: `@RestController`
- **Methods / Endpoints**:
  - **Constructor**: `GreetingController(GreetingService greetingService)`
  - **Endpoint**: `@GetMapping("/")` -> `Greeting home()`
  - **Endpoint**: `@GetMapping("/hello")` -> `Greeting hello(@RequestParam(value = "name", defaultValue = "World") String name)`
  - **Endpoint**: `@GetMapping("/hello/{name}")` -> `Greeting helloWithName(@PathVariable String name)`
- **Fields / Components**:
  - **Field**: `private final GreetingService greetingService;` (Validation: ``)

---

### Class: `GreetingService` (`src/main/java/com/nordea/demo/helloworld/GreetingService.java`)
- **Annotations**: `@Service`
- **Methods / Endpoints**:
  - **Method**: `Greeting getGreeting(String name)` (Annotations: ``)
  - **Method**: `Greeting getDefaultGreeting()` (Annotations: ``)

---

### Class: `GreetingControllerTest` (`src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java`)
- **Methods / Endpoints**:
  - **Method**: `void setup()` (Annotations: `@BeforeEach`)
  - **Method**: `void testRootEndpoint()` (Annotations: `@Test, @DisplayName("GET / should return default Hello, World!")`)
  - **Method**: `void testHelloDefault()` (Annotations: `@Test, @DisplayName("GET /hello with default param should return Hello, World!")`)
  - **Method**: `void testHelloWithQueryParam()` (Annotations: `@Test, @DisplayName("GET /hello?name=Alice should return personalized greeting")`)
  - **Method**: `void testHelloWithPathVariable()` (Annotations: `@Test, @DisplayName("GET /hello/Bob should return personalized greeting via path variable")`)
  - **Method**: `void testDirectControllerCall()` (Annotations: `@Test, @DisplayName("Direct unit test invocation with AssertJ")`)
- **Fields / Components**:
  - **Field**: `private MockMvc mockMvc;` (Validation: ``)
  - **Field**: `private GreetingController greetingController;` (Validation: ``)