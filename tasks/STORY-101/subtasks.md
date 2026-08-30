# Technical Subtask Decomposition: Multi-Language and Time-Aware Personalized Greeting Service

**Story ID:** STORY-101  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Implementation  
**Estimated Total PRs:** 4-5 PRs

## 1. Overview & Architectural Approach

The implementation will introduce a new `LocalizationHelper` component to encapsulate the complex logic for language negotiation, time zone parsing, and time-of-day-aware message selection. The existing `GreetingService` will be enhanced to utilize this new helper for generating personalized and localized greetings. The `GreetingController` will be modified to extract new query parameters and HTTP headers (`Time-Zone`, `Accept-Language`) and pass them to the service layer. Structured JSON logging will be integrated for observability, and comprehensive integration tests will ensure all acceptance criteria, including backward compatibility, are met.

## 2. Technical Subtasks Breakdown

### Subtask 1: Implement Core Localization and Time-Aware Greeting Logic

- **Subtask ID:** `SUBTASK-STORY-101-1`
- **Target Component / Layer:** Utility / Business Logic
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC2, AC3, AC4, AC5
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/util/LocalizationHelper.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/model/TimeOfDay.java` (New)
  - `src/main/resources/messages_en.properties` (New)
  - `src/main/resources/messages_sv.properties` (New)
  - `src/main/resources/messages_da.properties` (New)
  - `src/main/resources/messages_no.properties` (New)
  - `src/main/resources/messages_fi.properties` (New)
  - `src/main/resources/messages_is.properties` (New)
  - `src/main/resources/messages_es.properties` (New)
  - `src/main/resources/messages_fr.properties` (New)
  - `src/main/resources/messages_de.properties` (New)
- **Technical Description & Steps:**
  1. Create `LocalizationHelper` class to encapsulate language resolution, time zone parsing, and time-of-day logic.
  2. Implement language negotiation logic based on `Accept-Language` header and `lang` query parameter, with fallback to English.
  3. Implement time zone parsing from `Time-Zone` header (IANA identifier) and define fallback to UTC if invalid or missing.
  4. Define `TimeOfDay` enum (Morning, Afternoon, Evening) and logic to determine it based on local time.
  5. Store localized greeting messages in properties files (e.g., `messages_en.properties`, `messages_es.properties`) for each supported language and time of day.
- **Verification & Testing Criteria:**
  - [ ] Unit tests for `LocalizationHelper` cover language negotiation, time zone parsing, time-of-day determination, and message retrieval for all supported languages and edge cases (e.g., unsupported language, invalid time zone).

---

### Subtask 2: Enhance GreetingService to Utilize Localization Logic

- **Subtask ID:** `SUBTASK-STORY-101-2`
- **Target Component / Layer:** Business Service Layer
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-101-1`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` (Modify)
- **Technical Description & Steps:**
  1. Inject `LocalizationHelper` into `GreetingService`.
  2. Add new methods to `GreetingService` that accept `name`, `salutation`, `lang` (query param), `timeZoneHeader`, and `acceptLanguageHeaders`.
  3. These new methods will orchestrate calls to `LocalizationHelper` to construct the appropriate `message` and `recipient` strings.
  4. Update existing `getGreeting(String name)` and `getDefaultGreeting()` methods to internally call the new localized logic with default parameters (e.g., 'World' as name, no salutation, default language/timezone).
- **Verification & Testing Criteria:**
  - [ ] Unit tests for `GreetingService` verify correct delegation to `LocalizationHelper` and proper construction of `Greeting` objects for various inputs.
  - [ ] Existing unit tests for `GreetingService` (if any) continue to pass, ensuring backward compatibility at the service layer.

---

### Subtask 3: Update GreetingController for New Endpoints, Parameters, and Headers

- **Subtask ID:** `SUBTASK-STORY-101-3`
- **Target Component / Layer:** REST Controller Layer
- **Estimated Scope:** 1-2 PRs
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-101-2`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java` (Modify)
- **Technical Description & Steps:**
  1. Modify `@GetMapping("/hello")` and `@GetMapping("/hello/{name}")` endpoints to accept optional `salutation` and `lang` query parameters.
  2. Extract `Time-Zone` and `Accept-Language` HTTP headers from the incoming request.
  3. Pass all extracted parameters and headers to the enhanced `GreetingService` methods.
  4. Add the `X-Supported-Languages` response header to all relevant endpoints, listing supported languages as per AC4.
  5. Ensure the root endpoint (`@GetMapping("/")`) and default `/hello` endpoint (without parameters) maintain their exact legacy behavior as per AC1.
- **Verification & Testing Criteria:**
  - [ ] Integration tests verify correct extraction of query parameters and HTTP headers.
  - [ ] Integration tests confirm localized and time-aware greetings are returned for AC2, AC3, AC5.
  - [ ] Integration tests verify the `X-Supported-Languages` header is present and correctly formatted for AC4.
  - [ ] Integration tests confirm AC1 (backward compatibility) for `/` and `/hello` endpoints.

---

### Subtask 4: Implement Structured JSON Logging and Comprehensive Integration Testing

- **Subtask ID:** `SUBTASK-STORY-101-4`
- **Target Component / Layer:** Observability / Testing
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-101-3`
- **Affected / Target Files:**
  - `src/main/resources/logback-spring.xml` (Modify)
  - `src/main/java/com/nordea/demo/helloworld/logging/RequestLoggingAspect.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java` (Modify)
  - `src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java` (Modify)
- **Technical Description & Steps:**
  1. Configure `logback-spring.xml` to output structured JSON logs.
  2. Implement a `RequestLoggingAspect` (or similar mechanism) to capture and log details of each greeting request in JSON format, including language negotiated, time zone used, salutation, and recipient.
  3. Ensure PII masking is applied to sensitive fields in logs if `recipient` or `name` were considered PII (though assumed not for this story).
  4. Add comprehensive integration tests to `GreetingControllerTest` using `RestTestClient` to cover all acceptance criteria (AC1-AC5).
  5. Include tests for edge cases such as unsupported language fallback, missing `Time-Zone` header, and invalid `Time-Zone` header.
- **Verification & Testing Criteria:**
  - [ ] Manual inspection of application logs confirms structured JSON format and presence of required localization metrics.
  - [ ] All new and existing integration tests in `GreetingControllerTest` pass, verifying full compliance with AC1-AC5 and specified fallback behaviors.

---

## 3. Execution Dependency Graph

```text
SUBTASK-STORY-101-1 (Localization Logic) ──► SUBTASK-STORY-101-2 (Service Enhancement) ──► SUBTASK-STORY-101-3 (Controller Update) ──► SUBTASK-STORY-101-4 (Logging & Testing)
```

## 4. Open Questions & Clarifications Needed

- [ ] **Q1:** Q1: What is the preferred mechanism for storing localized greeting messages (e.g., Spring's `ResourceBundleMessageSource`, a simple `Map` in `LocalizationHelper`, or an external configuration service)?
- [ ] **Q2:** Q2: Are there specific requirements for the format or content of the `X-Supported-Languages` header beyond a comma-separated list of language codes?

## 5. Agent Assumptions Made

- **Assumption 1:** Assumption 1: Time partition logic for greetings is: Morning (05:00-11:59), Afternoon (12:00-17:59), Evening (18:00-04:59), based on the client's local time.
- **Assumption 2:** Assumption 2: Invalid or missing `Time-Zone` header values will safely fall back to UTC for time-of-day determination without causing client 4xx errors.
- **Assumption 3:** Assumption 3: Legacy responses for `/` and `/hello` (without parameters) must remain byte-compatible with the existing `Greeting` record structure `{"message": "Hello, World!", "recipient": "World"}`.
- **Assumption 4:** Assumption 4: The list of supported languages (`en`, `sv`, `da`, `no`, `fi`, `is`, `es`, `fr`, `de`) is exhaustive and static for this story's scope.
- **Assumption 5:** Assumption 5: PII masking for `recipient` in structured logs is not required, as `recipient` is part of the public greeting message and not considered sensitive data in this context.

## 6. Revision Changelog

- v1.0: Initial PR creation for tech lead review.

## 7. Done When Checklist

- [ ] Subtask plan was generated from refined User Story and grounded in AST context.
- [ ] Every subtask is bounded to 1–2 PRs in scope with explicit file paths and verification criteria.
- [ ] Dependencies between subtasks are mapped sequentially in Section 3.
- [ ] Pull Request opened targeting `main` for tech lead review.