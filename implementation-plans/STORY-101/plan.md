# Implementation Blueprint: Multi-Language and Time-Aware Personalized Greeting Service

**Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 5-6 PRs

## Subtask 1: Define Language & Salutation Data Structures and Configuration : **Subtask ID:** `SUBTASK-STORY-101-1`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask focuses on establishing the foundational data structures for multi-language and personalized greetings. It involves creating a `GreetingConfig` class to centralize supported languages, time-of-day greeting phrases, and salutations, and a `GreetingContext` record to encapsulate all input parameters for greeting generation. This directly supports AC2, AC3, and AC4 by providing the necessary data models for localization and personalization.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java` | **Create** | Configuration | New class to hold language-specific greetings, salutations, and supported languages. |
| `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java` | **Create** | Domain Model / DTO | New immutable record/class to encapsulate all greeting input parameters. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Greeting Configuration Class

- **Target File:** `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java`
- **Detailed Instructions:**
  1. Create a new class `GreetingConfig` annotated with `@ConfigurationProperties(prefix = "greeting.config")` and `@Configuration`.
  2. Define properties to hold maps for `languageGreetings` (e.g., `Map<String, Map<String, String>>` for language -> timeOfDay -> greeting), `salutations` (e.g., `Map<String, String>` for language -> salutation list), and `supportedLanguages` (e.g., `List<String>`).
  3. Provide public getters for these properties.

#### Step 3.2: Greeting Context Data Structure

- **Target File:** `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java`
- **Detailed Instructions:**
  1. Create a new Java record `GreetingContext` (or immutable class).
  2. Define fields: `String name`, `String salutation`, `String language`, `String timeZone`.
  3. Ensure immutability and provide a constructor.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** None
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** N/A

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Standard enterprise security practices
- **Performance Constraints:** Standard SLA targets
- **Error Handling Standards:** Standard GlobalExceptionHandler mapping

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/config/GreetingConfigTest.java`
- **Test Scenarios:**
  - [ ] Test `GreetingConfig` ensures correct loading of properties from `application.properties`.
  - [ ] Test `GreetingConfig` retrieves language and salutation data correctly.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/model/GreetingContextTest.java`
- **Test Scenarios:**
  - [ ] Test `GreetingContext` immutability and data integrity are verified.
  - [ ] Test `GreetingContext` field accessors return correct values.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 2: Implement Time Zone Resolution and Time-Aware Greeting Logic : **Subtask ID:** `SUBTASK-STORY-101-2`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask introduces time zone awareness and time-of-day categorization into the greeting service. It involves creating a `TimeZoneService` to parse and validate `Time-Zone` headers, a `TimeOfDayResolver` utility to determine 'Morning', 'Afternoon', or 'Evening' based on local time, and integrating these into the existing `GreetingService` to enable dynamic, time-aware greetings. This directly addresses AC2, AC3, and AC5.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/service/TimeZoneService.java` | **Create** | Utility Service | New service to resolve IANA time zone identifiers from HTTP headers. |
| `src/main/java/com/nordea/demo/helloworld/util/TimeOfDayResolver.java` | **Create** | Utility | New utility to categorize local time into 'Morning', 'Afternoon', or 'Evening'. |
| `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` | **Modify** | Business Logic | Integrate time zone and time-of-day resolution logic. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Time Zone Service Implementation

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/TimeZoneService.java`
- **Detailed Instructions:**
  1. Create a new `@Service` class `TimeZoneService`.
  2. Implement a method `ZoneId resolveTimeZone(String timeZoneHeader)` that:
  3. - Accepts a `String` representing the `Time-Zone` HTTP header value.
  4. - Attempts to parse it into a `ZoneId` using `ZoneId.of()`.
  5. - If parsing fails or the header is null/empty, return `ZoneId.of("UTC")` as a fallback (Assumption 2).

#### Step 3.2: Time of Day Resolver Utility

- **Target File:** `src/main/java/com/nordea/demo/helloworld/util/TimeOfDayResolver.java`
- **Detailed Instructions:**
  1. Create a new utility class `TimeOfDayResolver` (can be static methods or a `@Component`).
  2. Implement a method `String getTimeOfDay(LocalTime localTime)` that:
  3. - Takes a `LocalTime` object.
  4. - Returns "Morning" (05:00-11:59), "Afternoon" (12:00-17:59), or "Evening" (18:00-04:59) based on the time (Assumption 1).

#### Step 3.3: Integrate into GreetingService

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java`
- **Detailed Instructions:**
  1. Inject `TimeZoneService` and `TimeOfDayResolver` into `GreetingService`.
  2. Modify the `getGreeting` method (or create a new one, e.g., `getLocalizedGreeting`) to accept `GreetingContext`.
  3. Inside this method, use `TimeZoneService` to resolve the `ZoneId` from `GreetingContext.timeZone()`.
  4. Get the current `LocalTime` for that `ZoneId`.
  5. Use `TimeOfDayResolver` to get the time-of-day string.
  6. Prepare to use this time-of-day string to fetch the appropriate greeting from `GreetingConfig` (from SUBTASK-STORY-101-1).

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `GreetingService`
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** N/A

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Standard enterprise security practices
- **Performance Constraints:** Standard SLA targets
- **Error Handling Standards:** Standard GlobalExceptionHandler mapping

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `TimeZoneService` covers valid IANA IDs (e.g., "Europe/Madrid", "UTC").
  - [ ] Test `TimeZoneService` handles invalid IDs, null, and empty inputs, verifying UTC fallback.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java`
- **Test Scenarios:**
  - [ ] Test `TimeOfDayResolver` covers various `LocalTime` values across morning, afternoon, and evening boundaries (e.g., 04:59, 05:00, 11:59, 12:00, 17:59, 18:00).
  - [ ] Test `TimeOfDayResolver` verifies correct time-of-day categorization.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `GreetingService` (new method) uses mocked `TimeZoneService` and `TimeOfDayResolver` to verify time-aware greeting logic.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 3: Enhance Greeting Service with Localization, Salutations, and Fallback : **Subtask ID:** `SUBTASK-STORY-101-3`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1-2 PRs

### 1. Executive Summary & Objective

This subtask refines the `GreetingService` to handle language negotiation, salutation integration, and robust fallback mechanisms. It introduces a `LanguageNegotiationService` to determine the preferred language from request headers and a `MessageFormatter` to construct the final greeting. The `GreetingService` will be updated to orchestrate these components, ensuring localized, time-aware greetings with salutations, and gracefully falling back to English for unsupported languages. This fulfills AC2, AC3, AC4, and AC5.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` | **Modify** | Business Logic | Refactor to accept `GreetingContext`, integrate language negotiation, salutations, and fallback. |
| `src/main/java/com/nordea/demo/helloworld/service/LanguageNegotiationService.java` | **Create** | Business Logic / Utility Service | New service to handle `Accept-Language` header parsing and language selection. |
| `src/main/java/com/nordea/demo/helloworld/util/MessageFormatter.java` | **Create** | Utility | New utility to format localized and personalized greeting messages. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Language Negotiation Service

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/LanguageNegotiationService.java`
- **Detailed Instructions:**
  1. Create a new `@Service` class `LanguageNegotiationService`.
  2. Inject `GreetingConfig` (from SUBTASK-STORY-101-1).
  3. Implement a method `String negotiateLanguage(String langParam, String acceptLanguageHeader)` that:
  4. - Prioritizes `langParam` if present and supported by `GreetingConfig.supportedLanguages`.
  5. - If not, parses `acceptLanguageHeader` (e.g., `sv-SE,sv;q=0.9,en;q=0.8`) and selects the best match from `GreetingConfig.supportedLanguages` (Assumption 4).
  6. - If no match, defaults to "en" (English).
  7. Provide a method `List<String> getSupportedLanguages()` that delegates to `GreetingConfig`.

#### Step 3.2: Message Formatter Utility

- **Target File:** `src/main/java/com/nordea/demo/helloworld/util/MessageFormatter.java`
- **Detailed Instructions:**
  1. Create a new utility class `MessageFormatter` (can be static methods or a `@Component`).
  2. Implement a method `String formatGreeting(String language, String timeOfDay, String salutation, String name, GreetingConfig config)` that:
  3. - Retrieves the appropriate greeting phrase from `GreetingConfig` based on `language` and `timeOfDay`.
  4. - Constructs the final message, incorporating `salutation` and `name` (e.g., "Good morning, {Salutation} {Name}!").
  5. - Handles cases where salutation might be null/empty.

#### Step 3.3: Refactor GreetingService

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java`
- **Detailed Instructions:**
  1. Inject `LanguageNegotiationService`, `MessageFormatter`, and `GreetingConfig`.
  2. Modify the `getLocalizedGreeting(GreetingContext context, String acceptLanguageHeader)` method (from SUBTASK-STORY-101-2):
  3. - Use `LanguageNegotiationService` to determine the `finalLanguage` based on `context.language()` and `acceptLanguageHeader`.
  4. - Use `TimeZoneService` and `TimeOfDayResolver` (from SUBTASK-STORY-101-2) to get `timeOfDay`.
  5. - Use `MessageFormatter` to construct the final `message` string.
  6. - Construct the `recipient` string using `context.salutation()` and `context.name()`.
  7. - Return a new `Greeting` record with the `message` and `recipient`.
  8. Add a method `List<String> getSupportedLanguages()` that delegates to `LanguageNegotiationService`.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `GreetingService`
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** N/A

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Standard enterprise security practices
- **Performance Constraints:** Standard SLA targets
- **Error Handling Standards:** Standard GlobalExceptionHandler mapping

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `LanguageNegotiationService` covers various `Accept-Language` headers, `lang` query parameters, and fallback to English.
  - [ ] Test `LanguageNegotiationService` verifies correct language selection based on `q` values and supported languages.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/util/MessageFormatterTest.java`
- **Test Scenarios:**
  - [ ] Test `MessageFormatter` covers different languages, time-of-day, and salutation combinations.
  - [ ] Test `MessageFormatter` handles null/empty salutations gracefully.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `GreetingService` (new method) verifies localized, time-aware greetings with salutations for all supported languages.
  - [ ] Test `GreetingService` verifies fallback to English for unsupported languages.
  - [ ] Test `GreetingService` verifies the correct list of supported languages is returned.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 4: Integrate Enhanced Greeting Service into Controller, Handle Headers, and Implement Logging : **Subtask ID:** `SUBTASK-STORY-101-4`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask integrates the enhanced `GreetingService` into the `GreetingController`, enabling it to process new query parameters and HTTP headers for personalized, localized, and time-aware greetings. It ensures backward compatibility for existing endpoints and introduces structured JSON logging for localization metrics, adhering to `FIN-GOV-GUARD-001`. This subtask addresses AC1, AC2, AC3, AC4, and AC5.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java` | **Modify** | API / Controller | Update controller to extract new parameters/headers, construct `GreetingContext`, call enhanced `GreetingService`, and handle response headers. |
| `src/main/java/com/nordea/demo/helloworld/logging/StructuredLogger.java` | **Create** | Cross-Cutting Concerns / Logging | New component for emitting structured JSON logs for localization metrics. |
| `src/main/resources/application.properties` | **Modify** | Configuration | Add configuration for `greeting.config` and potentially logging format. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Structured Logger Implementation

- **Target File:** `src/main/java/com/nordea/demo/helloworld/logging/StructuredLogger.java`
- **Detailed Instructions:**
  1. Create a new `@Component` class `StructuredLogger`.
  2. Inject a standard `Logger` (e.g., `org.slf4j.Logger`).
  3. Implement a method `void logLocalizationMetrics(Map<String, String> metrics)` that:
  4. - Converts the `metrics` map into a JSON string.
  5. - Logs the JSON string at INFO level.
  6. - Ensure PII masking if any sensitive data were to be logged (though not expected for localization metrics).

#### Step 3.2: Modify GreetingController

- **Target File:** `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java`
- **Detailed Instructions:**
  1. Update the constructor to inject `GreetingService` and `StructuredLogger`.
  2. **Modify `@GetMapping("/")`:**
  3. - Add `@RequestHeader(value = "Accept-Language", required = false) String acceptLanguageHeader`, `@RequestHeader(value = "Time-Zone", required = false) String timeZoneHeader`, `@RequestParam(value = "lang", required = false) String langParam`, `@RequestParam(value = "salutation", required = false) String salutationParam`, `@RequestParam(value = "name", defaultValue = "World") String nameParam`.
  4. - If `langParam`, `salutationParam`, `timeZoneHeader`, or `acceptLanguageHeader` are present, construct a `GreetingContext` and call `greetingService.getLocalizedGreeting(context, acceptLanguageHeader)`.
  5. - Otherwise, call `greetingService.getDefaultGreeting()` (or the existing logic).
  6. - Log metrics using `StructuredLogger`.
  7. - Add `X-Supported-Languages` header if `greetingService` indicates fallback.
  8. **Modify `@GetMapping("/hello")`:**
  9. - Similar to `/`, but `name` parameter is already present. Add `@RequestHeader` and `@RequestParam` for new parameters.
  10. - If new parameters are present, construct `GreetingContext` with `nameParam` and call `greetingService.getLocalizedGreeting`.
  11. - Otherwise, use existing logic `greetingService.getGreeting(nameParam)`.
  12. - Log metrics and add `X-Supported-Languages` header.
  13. **Modify `@GetMapping("/hello/{name}")`:**
  14. - Similar to `/hello`, but `name` is a path variable. Add `@RequestHeader` and `@RequestParam` for new parameters.
  15. - If new parameters are present, construct `GreetingContext` with `name` from path variable and call `greetingService.getLocalizedGreeting`.
  16. - Otherwise, use existing logic `greetingService.getGreeting(name)`.
  17. - Log metrics and add `X-Supported-Languages` header.

#### Step 3.3: Update `application.properties`

- **Target File:** `src/main/resources/application.properties`
- **Detailed Instructions:**
  1. Add configuration properties for `greeting.config` prefix (e.g., `greeting.config.supported-languages`, `greeting.config.language-greetings.en.morning`, etc.).
  2. Configure logging to output in JSON format if the logging framework supports it directly (e.g., `logging.pattern.console=...` or `logging.pattern.file=...` for Logback/Log4j2). If not, `StructuredLogger` will handle the JSON formatting within the log message.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `GreetingController`
- **Breaking Changes:** None (existing endpoints are enhanced to accept new parameters/headers while maintaining original behavior if not provided)
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Thorough integration testing to ensure backward compatibility and correct handling of new parameters/headers.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Input sanitization for query parameters and headers (handled by Spring's binding).; Structured JSON logging for localization metrics, ensuring no PII is logged (FIN-GOV-GUARD-001).
- **Performance Constraints:** Standard SLA targets
- **Error Handling Standards:** Standard GlobalExceptionHandler mapping

### 6. Comprehensive Testing Strategy

#### Unit Tests

- None specified.

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Verify legacy endpoints (`/`, `/hello`, `/hello/{name}`) return expected status code and payload structure when no new parameters/headers are provided.
  - [ ] Fulfills AC2: Verify HTTP endpoint returns expected status code, recipient, and localized message with explicit language, salutation, and `Time-Zone` header.
  - [ ] Fulfills AC3: Verify HTTP endpoint returns expected status code, recipient, and localized message with `Accept-Language` header and `Time-Zone` header.
  - [ ] Fulfills AC4: Verify unsupported language request falls back to English and returns `X-Supported-Languages` header.
  - [ ] Fulfills AC5: Verify path variable endpoint returns correct German afternoon greeting based on Berlin local time and `Accept-Language` header.
  - [ ] Verify structured JSON logs are emitted for relevant requests.


---

## Subtask 5: Comprehensive Test Suite Update & Refinement : **Subtask ID:** `SUBTASK-STORY-101-5`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask focuses on ensuring robust test coverage for all new functionalities. It involves updating the existing `GreetingControllerTest` for integration scenarios and creating new dedicated unit test classes for `GreetingService`, `TimeZoneService`, `LanguageNegotiationService`, and `TimeOfDayResolver`. The goal is to achieve high code coverage and verify all acceptance criteria (AC1-AC5) through automated tests.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java` | **Modify** | Integration Test | Update existing controller tests to cover new features, headers, and backward compatibility. |
| `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java` | **Create** | Unit Test | New unit test class for the enhanced `GreetingService`. |
| `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java` | **Create** | Unit Test | New unit test class for `TimeZoneService`. |
| `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java` | **Create** | Unit Test | New unit test class for `LanguageNegotiationService`. |
| `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java` | **Create** | Unit Test | New unit test class for `TimeOfDayResolver`. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Update GreetingControllerTest for Integration Scenarios

- **Target File:** `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java`
- **Detailed Instructions:**
  1. Modify `setup()` to use `RestTestClient.bindToController(new GreetingController(mockGreetingService, mockStructuredLogger)).build()` (inject mocks for dependencies).
  2. Add integration tests for AC1 (legacy endpoints without new params).
  3. Add integration tests for AC2 (explicit language, salutation, time zone).
  4. Add integration tests for AC3 (Accept-Language negotiation, time zone).
  5. Add integration tests for AC4 (unsupported language fallback, `X-Supported-Languages` header).
  6. Add integration tests for AC5 (path variable, time-aware, Accept-Language).
  7. Verify structured logging calls (e.g., using `Mockito.verify`).

#### Step 3.2: Create GreetingService Unit Tests

- **Target File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Detailed Instructions:**
  1. Create a new `@ExtendWith(MockitoExtension.class)` class `GreetingServiceTest`.
  2. Mock `TimeZoneService`, `TimeOfDayResolver`, `LanguageNegotiationService`, `MessageFormatter`, `GreetingConfig`.
  3. Test `getLocalizedGreeting` method with various `GreetingContext` inputs, verifying interactions with mocked dependencies and correct `Greeting` output.
  4. Test `getDefaultGreeting` and `getGreeting(name)` for backward compatibility.

#### Step 3.3: Create TimeZoneService Unit Tests

- **Target File:** `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java`
- **Detailed Instructions:**
  1. Create a new class `TimeZoneServiceTest`.
  2. Test `resolveTimeZone` with valid IANA IDs (e.g., "Europe/Madrid", "UTC").
  3. Test `resolveTimeZone` with invalid IDs (e.g., "Invalid/Zone"), null, and empty strings, verifying fallback to UTC.

#### Step 3.4: Create LanguageNegotiationService Unit Tests

- **Target File:** `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java`
- **Detailed Instructions:**
  1. Create a new class `LanguageNegotiationServiceTest`.
  2. Mock `GreetingConfig` to return predefined supported languages.
  3. Test `negotiateLanguage` with various combinations of `langParam` and `acceptLanguageHeader` (e.g., `lang=es`, `Accept-Language: sv-SE`, `Accept-Language: fr;q=0.9,en;q=0.8`, unsupported language, no headers).
  4. Verify correct language selection and fallback.

#### Step 3.5: Create TimeOfDayResolver Unit Tests

- **Target File:** `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java`
- **Detailed Instructions:**
  1. Create a new class `TimeOfDayResolverTest`.
  2. Test `getTimeOfDay` with `LocalTime` values representing morning, afternoon, and evening boundaries (e.g., 04:59, 05:00, 11:59, 12:00, 17:59, 18:00).
  3. Verify correct time-of-day string is returned.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** None
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** N/A

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Standard enterprise security practices
- **Performance Constraints:** Standard SLA targets
- **Error Handling Standards:** Standard GlobalExceptionHandler mapping

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] All unit tests pass with high code coverage (>80% branch coverage).

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java`
- **Test Scenarios:**
  - [ ] All unit tests pass with high code coverage (>80% branch coverage).

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java`
- **Test Scenarios:**
  - [ ] All unit tests pass with high code coverage (>80% branch coverage).

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java`
- **Test Scenarios:**
  - [ ] All unit tests pass with high code coverage (>80% branch coverage).

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Backward compatibility for legacy routes is explicitly tested.
  - [ ] Fulfills AC2: All acceptance criteria (AC1-AC5) are covered by automated integration tests.
  - [ ] Fulfills AC3: All acceptance criteria (AC1-AC5) are covered by automated integration tests.
  - [ ] Fulfills AC4: All acceptance criteria (AC1-AC5) are covered by automated integration tests.
  - [ ] Fulfills AC5: All acceptance criteria (AC1-AC5) are covered by automated integration tests.


---

## Open Questions & Clarifications Needed

- None at this time.

## Agent Assumptions Made

- **Assumption 1:** Time partition logic evaluates local client time: Morning (05:00-11:59), Afternoon (12:00-17:59), Evening (18:00-04:59).
- **Assumption 2:** Invalid or missing `Time-Zone` header values fall back safely to UTC without throwing client 4xx errors.
- **Assumption 3:** Legacy responses without query parameters remain byte-compatible with the existing `Greeting` record structure.
- **Assumption 4:** The `Accept-Language` header negotiation will prioritize the first supported language in the list, or the one with the highest 'q' value if multiple supported languages are present.
- **Assumption 5:** The existing `/`, `/hello`, and `/hello/{name}` endpoints in `GreetingController` will be enhanced to accept new parameters/headers. If none of the new parameters/headers are present, they will behave exactly as before. If new parameters/headers are present, they will use the new localized/time-aware logic.

## Revision Changelog

- v1.0: Initial PR creation for tech lead review.

## Done When Checklist

- [ ] Implementation plan was generated from all target subtasks in (`tasks/<story_id>/subtasks.md`) and parent story (`user-stories/<story_id>.md`).
- [ ] All file additions, modifications, and deletions are explicitly listed with exact relative paths.
- [ ] Blast radius and security guardrails are fully evaluated in Sections 4 and 5.
- [ ] Unit and integration test specifications map directly to parent User Story BDD acceptance criteria.
- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.
- [ ] The plan was saved to `implementation-plans/STORY-101/plan.md` on `SDLC_GOVERNANCE_REPO`.
- [ ] A GitHub Pull Request was created targeting `main` for human review.