# Document Specification: `Architecture_Technical_Spec.pdf`


---

> *Auto-parsed Multimodal PDF artifact for Agentic SDLC context grounding.*


---

## Page 1

Architecture and Technical
Specifications
Target Repository: poojabasker20/springboot-hello-world
Base Package: com.nordea.demo.helloworld
## 1. Document Overview & Metadata
● Document Title: SpringBoot Hello World Service Architecture & Technical Specifications
● Document ID: ARCH-TECH-SPEC-001
● Owner: Nordea Platform Engineering Team
● Status: Active Baseline
● Version: 1.0.0
## 2. Introduction
This document defines the functional, technical, and structural specifications for the SpringBoot
RESTful greeting service. It serves as the baseline for implementation, integration, and testing
across engineering teams.
## 3. Goals & Non-Goals
### 3.1 Goals
● Lightweight REST Endpoint Delivery: Provide synchronous greeting API endpoints via
HTTP GET request methods.
● Strongly-Typed Payloads: Ensure JSON responses strictly follow an immutable,
strongly-typed data record standard.
● High Testability: Enable rapid, sub-second unit and integration testing without requiring
full application context initialization.
### 3.2 Non-Goals
● State Persistence: Database or external storage integration is explicitly out of scope.
● User Authentication/Authorization: Security layer filters or OAuth configurations are
not included in this baseline version.

---

## Page 2

## 4. Requirements
### 4.1 Functional Requirements
● Root Endpoint: MUST return a default greeting payload addressed to "World" at path /.
● Query Parameter Endpoint: MUST support optional query parameters at
/hello?name={name} with a fallback default to "World".
● Path Variable Endpoint: MUST accept standard path variables at /hello/{name} to
construct personalized greetings.
### 4.2 Non-Functional Requirements
● Package Lock: All classes MUST reside strictly within the
com.nordea.demo.helloworld package space.
● Performance: Endpoint response times MUST stay under 10ms under nominal local
testing loads.
## 5. Technical Architecture
### 2.1 Technology Stack Baseline

| Tier / Category | Implementation Selection | Specification Details |
| --- | --- | --- |
| Language & Runtime | Java | OpenJDK 17 / OpenJDK 21 |
| Application Framework | Spring Boot | 3.x<br>(spring-boot-starter-w<br>eb) |
| Build & Dependency Tool | Apache Maven | Maven Wrapper (./mvnw) |
| Testing Harness | JUnit 5 & Spring Web Test<br>Client | Controller binding test<br>execution<br>(RestTestClient) |

### 2.2 Component Layering Model

---

## Page 3

### Page Diagrams & Flowcharts
> **[Architecture Diagram & Component Flow - Page 3]**:
Based on the image provided, here is a detailed description of the architecture diagram:

---

### Architecture & Component Diagram

The diagram illustrates the layered structure and execution environment of the Spring Boot application.

#### 1. Components & Layers (Top to Bottom)

* **Presentation / Web Layer (`@RestController`)**
  * **Implementation:** `GreetingController.java`
  * **Exposed Endpoints:**
    * `GET /`
    * `GET /hello`
    * `GET /hello/{name}`

* **Data Transfer Model (Java Record DTO)**
  * **Implementation:** `Greeting.java`
  * **Structure / JSON Payload:** `{"message": String, "recipient": String}`

* **Embedded Web Container**
  * **Runtime Engine:** `Spring Boot Tomcat Engine`

---

#### 2. Flows and Interactions

1. **Presentation Layer to Data Transfer Model:**
   * **Relation/Action:** `Returns`
   * **Description:** The `GreetingController` in the presentation layer handles incoming GET requests and returns instances of the `Greeting` Java Record DTO.

2. **Data Transfer Model / Web Layer to Container:**
   * **Relation/Action:** `Executes on`
   * **Description:** The web layer and DTO processing run hosted inside the embedded Spring Boot Tomcat Engine web container.

### 2.3 Data Contract Specification
The application defines a single, immutable data transfer record (Greeting) representing
response payloads:

package com.nordea.demo.helloworld;
public record Greeting(
String message,
String recipient
) {}
Serialized JSON Schema

{
"type": "object",
"properties": {

---

## Page 4

"message": {
"type": "string",
"example": "Hello, World!"
},
"recipient": {
"type": "string",
"example": "World"
}
},
"required": ["message", "recipient"]
}
### 2.4 Controller & Endpoint Specification The web layer is implemented in GreetingController, defining three synchronous REST
routes:

package com.nordea.demo.helloworld;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
@RestController
public class GreetingController {
@GetMapping("/")
public ResponseEntity<Greeting> getRootGreeting() {
return ResponseEntity.ok(new Greeting("Hello, World!",
"World"));
}
@GetMapping("/hello")
public ResponseEntity<Greeting> getQueryGreeting(

---

## Page 5

@RequestParam(name = "name", defaultValue = "World")
String name) {
return ResponseEntity.ok(new Greeting("Hello, " + name +
"!", name));
}
@GetMapping("/hello/{name}")
public ResponseEntity<Greeting> getPathGreeting(
@PathVariable("name") String name) {
return ResponseEntity.ok(new Greeting("Hello, " + name +
"!", name));
}
}
Implemented Endpoint Behavior Matrix

| Route | HTTP<br>Metho<br>d | Parameter<br>Source | Parameter<br>Default | Respons<br>e Status | Output JSON<br>Example |
| --- | --- | --- | --- | --- | --- |
| / | GET | None | N/A | 200 OK | {"message":<br>"Hello, World!",<br>"recipient":<br>"World"} |
| /hello | GET | Query<br>(?name=) | "World" | 200 OK | {"message":<br>"Hello, Alice!",<br>"recipient":<br>"Alice"} |
| /hello/{<br>name} | GET | Path<br>(/{name}) | None<br>(Required) | 200 OK | {"message":<br>"Hello, Bob!",<br>"recipient":<br>"Bob"} |


---

## Page 6

## 6. Testing Standards & Verification
Controller verification is performed using isolated instance binding with RestTestClient,
avoiding full application context startup to achieve sub-second execution:

package com.nordea.demo.helloworld;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.reactive.server.RestTestClient;
class GreetingControllerTest {
private RestTestClient client;
@BeforeEach
void setUp() {
this.client = RestTestClient.bindToController(new
GreetingController()).build();
}
@Test
void testRootGreetingReturns200AndDefaultPayload() {
this.client.get().uri("/")
.exchange()
.expectStatus().isOk()
.expectBody()
.jsonPath("$.message").isEqualTo("Hello, World!")
.jsonPath("$.recipient").isEqualTo("World");
}
@Test
void testQueryGreetingWithCustomName() {
this.client.get().uri("/hello?name=Alice")
.exchange()
.expectStatus().isOk()

---

## Page 7

.expectBody()
.jsonPath("$.message").isEqualTo("Hello, Alice!")
.jsonPath("$.recipient").isEqualTo("Alice");
}
@Test
void testPathGreetingWithCustomName() {
this.client.get().uri("/hello/Bob")
.exchange()
.expectStatus().isOk()
.expectBody()
.jsonPath("$.message").isEqualTo("Hello, Bob!")
.jsonPath("$.recipient").isEqualTo("Bob");
}
}