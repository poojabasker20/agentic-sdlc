# Technical Subtask Decomposition: Multi-Language and Time-Aware Personalized Greeting Service

**Story ID:** STORY-101  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Implementation  
**Estimated Total PRs:** 5-6 PRs

## 1. Overview & Architectural Approach

The implementation will extend the existing `GreetingService` to incorporate multi-language, time-aware, and salutation-based greeting logic. A new `TimeZoneService` will handle client time zone detection and time-of-day resolution. A `LanguageNegotiationService` will manage language selection based on query parameters and `Accept-Language` headers. The `GreetingController` will be updated to extract all relevant request parameters and headers, delegating to the enhanced service layer while maintaining backward compatibility for existing endpoints. Structured JSON logging will be introduced for localization metrics. Comprehensive unit and integration tests will be developed to cover all new functionalities and ensure backward compatibility.

## 2. Technical Subtasks Breakdown

### Subtask 1: Define Language & Salutation Data Structures and Configuration

- **Subtask ID:** `SUBTASK-STORY-101-1`
- **Target Component / Layer:** Configuration / Domain Models
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC2, AC3, AC4
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java` (New)
- **Overview of Changes:** Create a new `GreetingConfig` class to centralize the configuration of supported languages, their associated time-of-day greeting phrases (Morning, Afternoon, Evening), and available salutations. Define a `GreetingContext` record or class to encapsulate all input parameters (name, salutation, language, timeZone) that will be passed to the service layer for greeting generation.
- **Verification & Testing Goals:**
  - [ ] Unit tests for `GreetingConfig` ensure correct loading and retrieval of language and salutation data.
  - [ ] `GreetingContext` immutability and data integrity are verified.

---

### Subtask 2: Implement Time Zone Resolution and Time-Aware Greeting Logic

- **Subtask ID:** `SUBTASK-STORY-101-2`
- **Target Component / Layer:** Utility / Business Service
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC2, AC3, AC5
- **Dependencies:** `SUBTASK-STORY-101-1`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/service/TimeZoneService.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/util/TimeOfDayResolver.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` (Modify)
- **Overview of Changes:** Develop a `TimeZoneService` to parse the `Time-Zone` HTTP header, validate IANA time zone identifiers, and provide a `ZoneId` or fallback to UTC. Create a `TimeOfDayResolver` utility to categorize local time into 'Morning', 'Afternoon', or 'Evening' based on the agent's assumptions. Integrate these new components into the `GreetingService` to enable time-aware greeting generation.
- **Verification & Testing Goals:**
  - [ ] Unit tests for `TimeZoneService` cover valid/invalid headers and UTC fallback scenarios.
  - [ ] Unit tests for `TimeOfDayResolver` verify correct time-of-day categorization for various local times.
  - [ ] `GreetingService` unit tests verify time-aware greeting generation using mocked time zone and time-of-day inputs.

---

### Subtask 3: Enhance Greeting Service with Localization, Salutations, and Fallback

- **Subtask ID:** `SUBTASK-STORY-101-3`
- **Target Component / Layer:** Business Service
- **Estimated Scope:** 1-2 PRs
- **Fulfills User Story Criteria:** AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-101-1`, `SUBTASK-STORY-101-2`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` (Modify)
  - `src/main/java/com/nordea/demo/helloworld/service/LanguageNegotiationService.java` (New)
  - `src/main/java/com/nordea/demo/helloworld/util/MessageFormatter.java` (New)
- **Overview of Changes:** Refactor `GreetingService` to accept a `GreetingContext` object. Implement logic for language negotiation (prioritizing query parameter, then `Accept-Language` header, then default English), salutation formatting, and dynamic message selection based on the negotiated language and determined time of day. Implement graceful fallback to English for unsupported languages and provide a mechanism to return the list of supported languages.
- **Verification & Testing Goals:**
  - [ ] Unit tests for `LanguageNegotiationService` verify correct language selection based on `Accept-Language` header and supported languages.
  - [ ] `GreetingService` unit tests verify localized, time-aware greetings with salutations for all supported languages.
  - [ ] `GreetingService` unit tests verify fallback to English for unsupported languages and the correct list of supported languages.

---

### Subtask 4: Integrate Enhanced Greeting Service into Controller, Handle Headers, and Implement Logging

- **Subtask ID:** `SUBTASK-STORY-101-4`
- **Target Component / Layer:** REST Controller / Cross-Cutting Concerns
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-101-1`, `SUBTASK-STORY-101-2`, `SUBTASK-STORY-101-3`
- **Affected / Target Files:**
  - `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java` (Modify)
  - `src/main/java/com/nordea/demo/helloworld/logging/StructuredLogger.java` (New)
  - `src/main/resources/application.properties` (Modify)
- **Overview of Changes:** Modify `GreetingController` to extract `lang`, `salutation` query parameters, and `Time-Zone`, `Accept-Language` HTTP headers. Construct a `GreetingContext` object and pass it to the enhanced `GreetingService`. Ensure existing `/`, `/hello`, and `/hello/{name}` endpoints maintain full backward compatibility. Add logic to include the `X-Supported-Languages` response header when a language fallback occurs. Implement structured JSON logging for localization demand and request metrics as per FIN-GOV-GUARD-001.
- **Verification & Testing Goals:**
  - [ ] Integration tests verify all ACs (AC1-AC5) are met, including correct localized messages, salutations, time-aware greetings, and header handling.
  - [ ] Backward compatibility for legacy endpoints (`/`, `/hello`, `/hello/{name}`) is verified via integration tests.
  - [ ] Verify `X-Supported-Languages` header is present on fallback scenarios.
  - [ ] Verify structured JSON logs are emitted for relevant requests.

---

### Subtask 5: Comprehensive Test Suite Update & Refinement

- **Subtask ID:** `SUBTASK-STORY-101-5`
- **Target Component / Layer:** Testing
- **Estimated Scope:** 1 PR
- **Fulfills User Story Criteria:** AC1, AC2, AC3, AC4, AC5
- **Dependencies:** `SUBTASK-STORY-101-1`, `SUBTASK-STORY-101-2`, `SUBTASK-STORY-101-3`, `SUBTASK-STORY-101-4`
- **Affected / Target Files:**
  - `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java` (Modify)
  - `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java` (New)
  - `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java` (New)
  - `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java` (New)
  - `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java` (New)
- **Overview of Changes:** Update the existing `GreetingControllerTest` to include comprehensive integration tests for all new features, covering header parsing, query parameters, language negotiation, time zone handling, and fallback scenarios using `RestTestClient`. Create new dedicated unit test classes for `TimeZoneService`, `LanguageNegotiationService`, `TimeOfDayResolver`, and `GreetingService` to ensure high code coverage and isolated testing of business logic components.
- **Verification & Testing Goals:**
  - [ ] All unit and integration tests pass with high code coverage (>80% branch coverage).
  - [ ] All acceptance criteria (AC1-AC5) are covered by automated tests.
  - [ ] Backward compatibility for legacy routes is explicitly tested.

---

## 3. Execution Dependency Graph

```text
SUBTASK-STORY-101-1 (Data Structures) ──► SUBTASK-STORY-101-2 (Time Zone/Time-Aware) ──► SUBTASK-STORY-101-3 (Localized Service) ──► SUBTASK-STORY-101-4 (Controller/Logging) ──► SUBTASK-STORY-101-5 (Testing)
```

## 4. Open Questions & Clarifications Needed

- [ ] **Q1:** None at this time.

## 5. Agent Assumptions Made

- **Assumption 1:** Time partition logic evaluates local client time: Morning (05:00-11:59), Afternoon (12:00-17:59), Evening (18:00-04:59).
- **Assumption 2:** Invalid or missing `Time-Zone` header values fall back safely to UTC without throwing client 4xx errors.
- **Assumption 3:** Legacy responses without query parameters remain byte-compatible with the existing `Greeting` record structure.
- **Assumption 4:** The `Accept-Language` header negotiation will prioritize the first supported language in the list, or the one with the highest 'q' value if multiple supported languages are present.

## 6. Revision Changelog

- v1.0: Initial PR creation for tech lead review.

## 7. Done When Checklist

- [ ] Subtask plan was generated from refined User Story (`user-stories/<story_id>.md`) and grounded in AST context (`docs/architecture/AST_CODE_MAP.md`).
- [ ] Every subtask is bounded to 1–2 PRs in scope with explicit file paths and verification goals.
- [ ] Dependencies between subtasks are mapped sequentially in Section 3.
- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.
- [ ] The subtask plan was saved to `tasks/<story_id>/subtasks.md` on `agentic-sdlc`.
- [ ] A GitHub Pull Request was created (CREATE mode) or updated with a revision commit and comment (REVISE mode) on `agentic-sdlc`.