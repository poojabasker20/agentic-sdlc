# Implementation Blueprint: Define Language & Salutation Data Structures and Configuration

**Subtask ID:** `SUBTASK-STORY-101-1`  
**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

## 1. Executive Summary & Objective

This subtask establishes foundational data structures and configuration for the multi-language and time-aware greeting service. It involves creating a new `GreetingConfig` class to centralize supported languages, their associated time-of-day greeting phrases, and available salutations. Additionally, a `GreetingContext` record/class will be defined to encapsulate all input parameters (name, salutation, language, timeZone) required for greeting generation. This directly supports Acceptance Criteria AC2, AC3, and AC4 of the parent user story by providing the necessary data models for localized and personalized greetings.

## 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java` | **Create** | Configuration | Centralize configuration for supported languages, time-of-day phrases, and salutations. |
| `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java` | **Create** | Domain Models | Encapsulate all input parameters (name, salutation, language, timeZone) for greeting generation. |

## 3. Step-by-Step Technical Implementation Guide

### Step 3.1: Data Models & DTO Schemas (GreetingConfig)

- **Target File:** `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java`
- **Detailed Instructions:**
  1. Create a new class `GreetingConfig` within the `com.nordea.demo.helloworld.config` package.
  2. Annotate the class with `@Configuration` and `@ConfigurationProperties(prefix = "greeting.localization")` to enable Spring Boot configuration binding.
  3. Define properties to hold supported languages, their time-of-day greeting phrases (Morning, Afternoon, Evening), and available salutations. Use `Map<String, Map<String, String>> languagePhrases` for greetings and `Map<String, List<String>> supportedSalutations` for salutations.
  4. Ensure properties are immutable (e.g., using `final` fields and a constructor, or Lombok's `@Value` annotation if used).
  5. Provide public getter methods for all configured properties.

### Step 3.2: Data Models & DTO Schemas (GreetingContext)

- **Target File:** `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java`
- **Detailed Instructions:**
  1. Create a new `record` (Java 17+) or immutable class `GreetingContext` within the `com.nordea.demo.helloworld.model` package.
  2. Define the following fields: `String name`, `String salutation`, `String language`, `String timeZone`.
  3. If using a class instead of a record, ensure all fields are `final` and the class is immutable (e.g., no setters).
  4. Provide a canonical constructor to initialize all fields.

## 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `GreetingService (will consume GreetingContext and GreetingConfig)`, `GreetingController (will construct GreetingContext)`
- **Breaking Changes:** None, as these are new components.
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** These are new, isolated data structures and configuration. The risk is minimal. Ensure proper validation within `GreetingConfig` loading and `GreetingContext` construction to prevent invalid states.

## 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Ensure `GreetingContext` does not inadvertently store sensitive PII beyond the `name` field. If `name` is considered PII, downstream logging components must adhere to FIN-GOV-GUARD-001 for PII masking.; Configuration data in `GreetingConfig` should not contain sensitive information.
- **Performance Constraints:** `GreetingConfig` should be loaded once at application startup, ensuring minimal runtime overhead.; `GreetingContext` objects are lightweight and short-lived, so they will not introduce significant performance impact.
- **Error Handling Standards:** Configuration loading errors for `GreetingConfig` should be handled gracefully during application startup (e.g., fail-fast with clear error messages or provide sensible defaults if applicable).

## 6. Comprehensive Testing Strategy

### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/config/GreetingConfigTest.java`
- **Test Scenarios:**
  - [ ] Verify `GreetingConfig` loads correctly from `application.properties` or `application.yml` with expected language phrases and salutations.
  - [ ] Test retrieval of specific language greetings (Morning, Afternoon, Evening) from `languagePhrases`.
  - [ ] Test retrieval of supported salutations for a given language from `supportedSalutations`.
  - [ ] Verify default values or appropriate error handling if configuration is missing or malformed.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/model/GreetingContextTest.java`
- **Test Scenarios:**
  - [ ] Verify `GreetingContext` can be instantiated with all parameters (name, salutation, language, timeZone).
  - [ ] Verify immutability of the `GreetingContext` object (e.g., no setters, final fields).
  - [ ] Test getter methods return the correct values for each field.

### Integration & API Contract Tests

- None specified.

## 7. Open Questions & Clarifications Needed

- [ ] **Q1:** None at this time.

## 8. Agent Assumptions Made

- **Assumption 1:** The configuration for `GreetingConfig` will be managed via Spring Boot's `@ConfigurationProperties` mechanism, likely from `application.yml` or `application.properties`.
- **Assumption 2:** `GreetingContext` will be an immutable record/class, promoting thread safety and predictable behavior.
- **Assumption 3:** The `name` field in `GreetingContext` is considered non-sensitive for the purpose of this subtask's data structure definition. Downstream logging components will adhere to FIN-GOV-GUARD-001 for PII masking if `name` is deemed PII in a broader context.

## 9. Revision Changelog

- v1.0: Initial PR creation for tech lead review.

## 10. Done When Checklist

- [ ] Implementation plan was generated from target subtask and parent story.
- [ ] All file additions, modifications, and deletions are explicitly listed with exact relative paths.
- [ ] Blast radius and security guardrails are fully evaluated in Sections 4 and 5.
- [ ] Unit and integration test specifications map directly to parent User Story BDD acceptance criteria.
- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.
- [ ] The plan was saved to `implementation-plans/STORY-101/SUBTASK-STORY-101-1/plan.md` on `SDLC_GOVERNANCE_REPO`.
- [ ] A GitHub Pull Request was created targeting `main` for human review.