# Technical Subtask Decomposition: Localized and Personalized Greeting Service

**Story ID:** STORY-102  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Implementation  
**Estimated Total PRs:** 5 PRs

## 1. Overview & Architectural Approach

The existing `GreetingController` will be enhanced to accept new headers and query parameters for localization and personalization. The `GreetingService` will be significantly refactored to encapsulate the complex logic for resolving locale, time of day, and constructing dynamic greeting messages. New data structures will be introduced to manage localized greeting templates. Backward compatibility for existing routes will be strictly maintained. Telemetry will be integrated using Spring Boot's metrics capabilities to track regional usage.

## 2. Technical Subtasks Breakdown

### Subtask 1: Localization Data Structures & Configuration

- **Subtask ID:** `SUBTASK-STORY-102-1`
- **Target Component / Layer:** Configuration / Utility
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC2, AC3, AC4
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/localization/GreetingLocaleConfig.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/localization/TimeOfDay.java` (New)
  - `src/main/resources/messages_de.properties` (New)
  - `src/main/resources/messages_fi.properties` (New)
  - `src/main/resources/messages_fr.properties` (New)
  - `src/main/resources/messages_en.properties` (New)
- **Overview of Changes:** Introduce new classes and property files to manage localized greeting messages based on language and time of day. Define an enum for `TimeOfDay` (e.g., MORNING, AFTERNOON, EVENING, NIGHT) to categorize different parts of the day for time-aware greetings. These resources will store the various greeting phrases for supported languages.
- **Verification & Testing Goals:**
  - [ ] Unit tests ensure correct loading and retrieval of localized messages from property files.
  - [ ] Unit tests verify `TimeOfDay` enum logic (e.g., `fromHour(int hour)`) correctly categorizes hours into time segments.

---

### Subtask 2: Core Localization & Personalization Service Logic

- **Subtask ID:** `SUBTASK-STORY-102-2`
- **Target Component / Layer:** Business Service
- **Estimated Scope:** 1-2 PRs
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4
- **Dependencies:** `SUBTASK-STORY-102-1`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/GreetingService.java` (Modify)
  - `src/main/java/com/nordea/demo/helloworld/localization/LocaleResolver.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/localization/TimezoneResolver.java` (New)
- **Overview of Changes:** Refactor `GreetingService` to incorporate new methods for resolving `Locale` from `Accept-Language` headers and `ZoneId` from `X-Timezone-Offset` or `ZoneId` headers. Implement logic to determine the `TimeOfDay` based on the resolved timezone. Prioritize `X-Timezone-Offset` if both are present, and default to UTC if the provided timezone values are invalid or missing. Construct localized greetings using the data structures from Subtask 1. This includes logic for handling unsupported languages by returning a default greeting with an explicit notification message, and applying optional professional titles to the recipient.
- **Verification & Testing Goals:**
  - [ ] Unit tests for `LocaleResolver` and `TimezoneResolver` cover various header inputs and default fallbacks.
  - [ ] Unit tests for `TimezoneResolver` verify correct precedence (`X-Timezone-Offset` over `ZoneId`) and fallback to UTC for invalid or missing timezone headers.
  - [ ] Unit tests for `GreetingService` verify correct localized message generation for all supported languages, time of day, and title combinations.
  - [ ] Unit tests confirm the explicit notification message is returned for unsupported languages.
  - [ ] Unit tests ensure backward compatibility logic (default greetings) is preserved when no localization headers are provided.

---

### Subtask 3: Enhance GreetingController Endpoints

- **Subtask ID:** `SUBTASK-STORY-102-3`
- **Target Component / Layer:** REST Controller
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4
- **Dependencies:** `SUBTASK-STORY-102-2`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/GreetingController.java` (Modify)
- **Overview of Changes:** Update the existing `GreetingController` methods (`@GetMapping("/hello")` and `@GetMapping("/hello/{name}")`) to accept `Accept-Language`, `X-Timezone-Offset`, and `ZoneId` headers, and an optional `title` query parameter. These new parameters will be extracted from the HTTP request and passed to the enhanced `GreetingService` for processing, with `X-Timezone-Offset` taking precedence for timezone resolution. The root endpoint (`@GetMapping("/")`) will remain unchanged to ensure strict backward compatibility.
- **Verification & Testing Goals:**
  - [ ] Integration tests using `RestTestClient` verify that new headers and query parameters are correctly parsed and passed to the service.
  - [ ] Integration tests confirm backward compatibility for requests without localization headers/params, ensuring default responses are returned.
  - [ ] Integration tests verify the `/` endpoint still returns the default 'Hello, World!' message as per AC1.

---

### Subtask 4: Telemetry Integration for Regional Requests

- **Subtask ID:** `SUBTASK-STORY-102-4`
- **Target Component / Layer:** Cross-Cutting Concern / Monitoring
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC5
- **Dependencies:** `SUBTASK-STORY-102-2`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/GreetingService.java` (Modify)
  - `src/main/java/com/nordea/demo/helloworld/metrics/GreetingMetrics.java` (New)
- **Overview of Changes:** Introduce a new component (`GreetingMetrics`) to manage and increment a `greeting.requests.locale` counter using Micrometer. Integrate this metrics component into the `GreetingService` to record the resolved locale (or 'unsupported'/'default') for each greeting request. Ensure that no plain-text PII is persisted or logged in diagnostic logs, adhering to FIN-GOV-GUARD-001.
- **Verification & Testing Goals:**
  - [ ] Unit tests for `GreetingMetrics` verify the counter incrementation logic.
  - [ ] Integration tests verify that the `greeting.requests.locale` metric counter is incremented correctly for various locale requests (supported, unsupported, default).
  - [ ] Confirm through log inspection during testing that no PII is present in diagnostic logs.

---

### Subtask 5: Comprehensive Integration & Performance Testing

- **Subtask ID:** `SUBTASK-STORY-102-5`
- **Target Component / Layer:** Testing
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-102-3`, `SUBTASK-STORY-102-4`
- **Affected / Target Files:**
  - `src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java` (Modify)
  - `src/test/java/com/nordea/demo/helloworld/GreetingIntegrationTest.java` (New)
- **Overview of Changes:** Expand existing `GreetingControllerTest` and create a new `GreetingIntegrationTest` class to cover all new acceptance criteria end-to-end. This includes testing various combinations of `Accept-Language`, `X-Timezone-Offset`, `name`, and `title` parameters. Verify backward compatibility, correct localized responses, unsupported language notifications, and metric incrementation. Include assertions for response latency to ensure the sub-10ms requirement is met.
- **Verification & Testing Goals:**
  - [ ] All existing and new unit/integration tests pass successfully.
  - [ ] All Acceptance Criteria (AC1-AC5) are verified through automated tests, covering all specified scenarios.
  - [ ] Performance tests (or specific assertions within integration tests) confirm sub-10ms response latency (p99 < 50ms) under nominal load.

---

## 3. Execution Dependency Graph

```text
SUBTASK-STORY-102-1 (Localization Data) ──► SUBTASK-STORY-102-2 (Service Logic) ──► SUBTASK-STORY-102-3 (Controller Endpoints) ──► SUBTASK-STORY-102-5 (Integration Tests)
SUBTASK-STORY-102-2 (Service Logic) ──► SUBTASK-STORY-102-4 (Telemetry) ──► SUBTASK-STORY-102-5 (Integration Tests)
```

## 4. Open Questions & Clarifications Needed

- [ ] **Q1:** None at this time.

## 5. Agent Assumptions Made

- **Assumption 1:** The existing `Greeting` record structure (`message`, `recipient`) is sufficient, and only its fields need dynamic population based on localization and personalization logic.
- **Assumption 2:** Time-of-day segments for greetings (e.g., morning, afternoon, evening, night) will be defined based on common conventions (e.g., morning 05:00-11:59, afternoon 12:00-16:59, evening 17:00-21:59, night 22:00-04:59).
- **Assumption 3:** The `title` query parameter is optional and, if provided, will be prepended to the `name` in the `recipient` field.
- **Assumption 4:** Micrometer is the chosen metrics library for implementing the telemetry requirements.
- **Assumption 5:** When both `X-Timezone-Offset` and `ZoneId` headers are provided, `X-Timezone-Offset` will take precedence. If both are invalid or missing, the system will default to UTC for time zone resolution.

## 6. Revision Changelog

- v1.0: Initial PR creation for tech lead review.
v1.1: Incorporated reviewer feedback regarding `X-Timezone-Offset` precedence and UTC fallback for timezone resolution.

## 7. Done When Checklist

- [ ] Subtask plan was generated from refined User Story (`user-stories/<story_id>.md`) and grounded in AST context (`docs/architecture/AST_CODE_MAP.md`).
- [ ] Every subtask is bounded to 1–2 PRs in scope with explicit file paths and verification goals.
- [ ] Dependencies between subtasks are mapped sequentially in Section 3.
- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.
- [ ] The subtask plan was saved to `tasks/<story_id>/subtasks.md` on `agentic-sdlc`.
- [ ] A GitHub Pull Request was created (CREATE mode) or updated with a revision commit and comment (REVISE mode) on `agentic-sdlc`.