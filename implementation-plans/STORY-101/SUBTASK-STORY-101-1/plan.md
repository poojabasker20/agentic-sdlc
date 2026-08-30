# Implementation Blueprint: Define Language & Salutation Data Structures and Configuration

**Subtask ID:** `SUBTASK-STORY-101-1`  
**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

## 1. Executive Summary & Objective

This subtask focuses on establishing foundational data structures for the multi-language and time-aware greeting service. It involves creating a new `GreetingConfig` class to centralize configurable greeting phrases and salutations, and a `GreetingContext` record to encapsulate all necessary input parameters (name, salutation, language, timeZone) for greeting generation, ensuring a clean and type-safe data flow for subsequent service enhancements.

## 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java` | **Create** | Configuration | New class to hold configurable language-specific greetings and supported salutations. |
| `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java` | **Create** | Domain Models | New immutable record to encapsulate all input parameters for greeting generation. |
| `src/test/java/com/nordea/demo/helloworld/config/GreetingConfigTest.java` | **Create** | Unit Test | Unit tests for GreetingConfig to verify property binding and data retrieval. |
| `src/test/java/com/nordea/demo/helloworld/model/GreetingContextTest.java` | **Create** | Unit Test | Unit tests for GreetingContext to verify immutability and data integrity. |

## 3. Step-by-Step Technical Implementation Guide

### Step 3.1: Data Models & DTO Schemas (GreetingContext)

- **Target File:** `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java`
- **Detailed Instructions:**
  1. Create a new Java record named `GreetingContext` in the `com.nordea.demo.helloworld.model` package.
  2. Define the record components: `String name`, `String salutation`, `String language`, and `java.time.ZoneId timeZone`.
  3. Ensure the record is immutable (inherent with Java records).
  4. Add appropriate Javadoc comments to describe the purpose of the record and its components.

### Step 3.2: Configuration for Language & Salutation Data (GreetingConfig)

- **Target File:** `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java`
- **Detailed Instructions:**
  1. Create a new class named `GreetingConfig` in the `com.nordea.demo.helloworld.config` package.
  2. Annotate the class with `@Configuration` to register it as a Spring configuration bean.
  3. Annotate the class with `@ConfigurationProperties(prefix = "greeting.config")` to enable binding properties from `application.properties` or `application.yml`.
  4. Define a private field `Map<String, Map<String, String>> languageGreetings` to store language-specific and time-of-day specific greeting phrases (e.g., `{"en": {"morning": "Good morning", "afternoon": "Good afternoon", "evening": "Good evening"}}`).
  5. Define a private field `List<String> supportedSalutations` to store a list of available salutations.
  6. Provide public getter and setter methods for both `languageGreetings` and `supportedSalutations` for Spring Boot's property binding mechanism.
  7. Add appropriate Javadoc comments for the class and its fields.

## 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `GreetingService (will consume GreetingContext and GreetingConfig in future subtasks)`, `GreetingController (will construct GreetingContext in future subtasks)`
- **Breaking Changes:** None, as these are new components being introduced.
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** These are new, isolated data structures and configuration. No specific mitigation strategy is required at this stage beyond standard code review.

## 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** The 'name' field within `GreetingContext` could potentially contain PII. Ensure that any logging of `GreetingContext` instances in subsequent subtasks adheres to FIN-GOV-GUARD-001 for PII masking and redaction.; Configuration data in `GreetingConfig` should not contain sensitive information.
- **Performance Constraints:** Configuration loading for `GreetingConfig` is a one-time startup cost and should not impact runtime performance.; `GreetingContext` is a lightweight, immutable data carrier, ensuring minimal performance overhead.
- **Error Handling Standards:** N/A for these data structures themselves. Error handling will be implemented in services consuming these structures.

## 6. Comprehensive Testing Strategy

### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/config/GreetingConfigTest.java`
- **Test Scenarios:**
  - [ ] Verify that `GreetingConfig` correctly binds properties from `application.properties` (or `application.yml`) for `languageGreetings`.
  - [ ] Verify that `GreetingConfig` correctly binds properties for `supportedSalutations`.
  - [ ] Test retrieval of a specific greeting phrase for a given language and time of day from `languageGreetings`.
  - [ ] Test retrieval of the list of supported salutations from `supportedSalutations`.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/model/GreetingContextTest.java`
- **Test Scenarios:**
  - [ ] Verify that `GreetingContext` can be successfully instantiated with all its components.
  - [ ] Verify the immutability of `GreetingContext` by checking that getter methods return the same values as provided during construction.
  - [ ] Verify the correct implementation of `equals()` and `hashCode()` for the `GreetingContext` record.

### Integration & API Contract Tests

- None specified.

## 7. Open Questions & Clarifications Needed

- [ ] **Q1:** Should `GreetingConfig` include default hardcoded values for greetings if not specified in external properties, or should it strictly rely on external configuration (with potentially empty defaults if not present)?
- [ ] **Q2:** Are there any specific validation rules (e.g., regex for name, allowed values for salutation/language) for the fields within `GreetingContext` that should be enforced at the model level, or will validation be handled by a service layer?

## 8. Agent Assumptions Made

- **Assumption 1:** `GreetingConfig` will be populated via Spring Boot's `@ConfigurationProperties` mechanism, requiring entries in `application.properties` or `application.yml` for actual values.
- **Assumption 2:** `GreetingContext` is intended as an immutable data carrier; field validation (beyond basic type checking) will be handled by downstream services rather than within the record itself.
- **Assumption 3:** The `java.time.ZoneId` in `GreetingContext` will be populated by the `TimeZoneService` in a later subtask, and its presence is assumed for the context's completeness.

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