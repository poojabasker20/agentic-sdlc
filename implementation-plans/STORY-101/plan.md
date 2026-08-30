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

This subtask establishes the foundational data structures and configuration for the multi-language and salutation features. It involves creating a GreetingConfig class to manage supported languages, greeting phrases, and salutations, and a GreetingContext record/class to encapsulate all greeting-related input parameters.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java` | **Create** | Configuration | Define configuration properties for supported languages, time-of-day greetings, and salutations. |
| `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java` | **Create** | DTO Schema | Define an immutable record/class to encapsulate all greeting input parameters. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Define Greeting Configuration

- **Target File:** `src/main/java/com/nordea/demo/helloworld/config/GreetingConfig.java`
- **Detailed Instructions:**
  1. 1. Create a new Java class `GreetingConfig` in the `com.nordea.demo.helloworld.config` package.
  2. 2. Annotate the class with `@ConfigurationProperties(prefix = "greeting")` to bind properties from `application.properties`.
  3. 3. Define a `Map<String, Map<String, String>> languages` field to store greetings per language and time of day (e.g., `greeting.languages.en.morning=Good morning`).
  4. 4. Define a `List<String> salutations` field to store supported salutations (e.g., `greeting.salutations=Mr,Ms,Dr`).
  5. 5. Provide public getters for these fields.

#### Step 3.2: Define Greeting Context Data Structure

- **Target File:** `src/main/java/com/nordea/demo/helloworld/model/GreetingContext.java`
- **Detailed Instructions:**
  1. 1. Create a new Java record (or immutable class) `GreetingContext` in the `com.nordea.demo.helloworld.model` package.
  2. 2. Define record components: `String name`, `String salutation`, `String language`, `java.time.ZoneId timeZone`.
  3. 3. Ensure the record is immutable and provides standard accessors.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** None
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** New components, no direct impact on existing functionality.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Configuration properties should not contain sensitive information directly.; Ensure `GreetingContext` is immutable to prevent unintended state changes.
- **Performance Constraints:** Configuration loading should be efficient at application startup.
- **Error Handling Standards:** N/A for data structures and configuration.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/config/GreetingConfigTest.java`
- **Test Scenarios:**
  - [ ] Test that `GreetingConfig` correctly loads supported languages and their greetings from properties.
  - [ ] Test that `GreetingConfig` correctly loads supported salutations from properties.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/model/GreetingContextTest.java`
- **Test Scenarios:**
  - [ ] Test `GreetingContext` immutability and correct encapsulation of name, salutation, language, and timeZone.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 2: Implement Time Zone Resolution and Time-Aware Greeting Logic : **Subtask ID:** `SUBTASK-STORY-101-2`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask introduces time zone handling and time-of-day categorization. It involves creating a TimeZoneService to parse and validate time zone headers, a TimeOfDayResolver utility to determine the time segment (Morning, Afternoon, Evening), and integrating these into the GreetingService to enable time-aware greetings.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/service/TimeZoneService.java` | **Create** | Business Logic | Service to parse and validate IANA time zone identifiers from HTTP headers. |
| `src/main/java/com/nordea/demo/helloworld/util/TimeOfDayResolver.java` | **Create** | Utility | Utility to categorize local time into 'Morning', 'Afternoon', or 'Evening'. |
| `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` | **Modify** | Business Logic | Integrate TimeZoneService and TimeOfDayResolver for time-aware greeting generation. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Implement Time Zone Resolution Service

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/TimeZoneService.java`
- **Detailed Instructions:**
  1. 1. Create a new Java class `TimeZoneService` in the `com.nordea.demo.helloworld.service` package.
  2. 2. Annotate the class with `@Service`.
  3. 3. Implement a public method `ZoneId resolveTimeZone(String timeZoneHeader)`:
  4. 4.   - If `timeZoneHeader` is null or empty, return `ZoneId.of("UTC")`.
  5. 5.   - Use a `try-catch` block to parse `timeZoneHeader` using `ZoneId.of(timeZoneHeader)`.
  6. 6.   - Catch `java.time.zone.ZoneRulesException` for invalid IDs and return `ZoneId.of("UTC")` as a fallback.

#### Step 3.2: Implement Time-of-Day Resolver Utility

- **Target File:** `src/main/java/com/nordea/demo/helloworld/util/TimeOfDayResolver.java`
- **Detailed Instructions:**
  1. 1. Create a new Java class `TimeOfDayResolver` in the `com.nordea.demo.helloworld.util` package.
  2. 2. Implement a public static method `String getTimeOfDay(LocalTime localTime)`:
  3. 3.   - Define time ranges: Morning (05:00-11:59), Afternoon (12:00-17:59), Evening (18:00-04:59).
  4. 4.   - Use `localTime.isBefore()` and `localTime.isAfter()` to determine the correct time segment.
  5. 5.   - Return "morning", "afternoon", or "evening" as a String.

#### Step 3.3: Integrate Time-Aware Logic into GreetingService

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java`
- **Detailed Instructions:**
  1. 1. Inject `TimeZoneService` and `TimeOfDayResolver` into `GreetingService`.
  2. 2. Modify the existing `getGreeting(String name)` method or add a new method (e.g., `getGreeting(GreetingContext context)`) to accept a `GreetingContext` (from SUBTASK-STORY-101-1).
  3. 3. Inside the method:
  4. 4.   - Use `context.timeZone()` to get the `ZoneId`.
  5. 5.   - Get the current `LocalTime` for that `ZoneId` (e.g., `LocalTime.now(context.timeZone())`).
  6. 6.   - Use `TimeOfDayResolver.getTimeOfDay()` to determine the time segment.
  7. 7.   - (Initial integration) For now, use a placeholder to indicate time-awareness in the greeting message (e.g., "Good " + timeOfDay + ", " + name + "!"). Full localization will be in SUBTASK-STORY-101-3.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `com.nordea.demo.helloworld.service.GreetingService`
- **Breaking Changes:** None (new services, `GreetingService` modification will be internal for now)
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** New services are isolated. `GreetingService` changes are internal until integrated by the controller.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Ensure `TimeZoneService` handles invalid time zone inputs gracefully to prevent exceptions or unexpected behavior.
- **Performance Constraints:** Time zone resolution and time-of-day calculation should be performant and not introduce significant latency.
- **Error Handling Standards:** Invalid `Time-Zone` header values must fall back safely to UTC without throwing client 4xx errors (as per AC).

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `resolveTimeZone` with valid IANA time zone identifiers (e.g., 'Europe/Madrid', 'America/New_York').
  - [ ] Test `resolveTimeZone` with invalid time zone identifiers (e.g., 'Invalid/Zone') to ensure fallback to UTC.
  - [ ] Test `resolveTimeZone` with null or empty input to ensure fallback to UTC.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java`
- **Test Scenarios:**
  - [ ] Test `getTimeOfDay` for various `LocalTime` values within the 'Morning' range (e.g., 05:00, 09:30, 11:59).
  - [ ] Test `getTimeOfDay` for various `LocalTime` values within the 'Afternoon' range (e.g., 12:00, 14:00, 17:59).
  - [ ] Test `getTimeOfDay` for various `LocalTime` values within the 'Evening' range (e.g., 18:00, 23:00, 04:59).

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] Verify `GreetingService` (with mocked `TimeZoneService` and `TimeOfDayResolver`) generates time-aware greetings based on mocked time-of-day inputs.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 3: Enhance Greeting Service with Localization, Salutations, and Fallback : **Subtask ID:** `SUBTASK-STORY-101-3`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1-2 PRs

### 1. Executive Summary & Objective

This subtask refactors the GreetingService to fully support localization, salutations, and language negotiation. It introduces a LanguageNegotiationService to determine the preferred language and a MessageFormatter to construct the final greeting string. The GreetingService will use these components along with GreetingConfig and GreetingContext to generate personalized, localized, and time-aware greetings with appropriate fallbacks.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java` | **Modify** | Business Logic | Refactor to accept GreetingContext, implement language negotiation, salutation formatting, and dynamic message selection. |
| `src/main/java/com/nordea/demo/helloworld/service/LanguageNegotiationService.java` | **Create** | Business Logic | Service to determine the preferred language based on query parameters and Accept-Language header. |
| `src/main/java/com/nordea/demo/helloworld/util/MessageFormatter.java` | **Create** | Utility | Utility to construct the final greeting string with salutations. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Implement Language Negotiation Service

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/LanguageNegotiationService.java`
- **Detailed Instructions:**
  1. 1. Create a new Java class `LanguageNegotiationService` in the `com.nordea.demo.helloworld.service` package.
  2. 2. Annotate the class with `@Service`.
  3. 3. Inject `GreetingConfig` (from SUBTASK-STORY-101-1).
  4. 4. Implement a public method `String negotiateLanguage(String langQueryParam, String acceptLanguageHeader)`:
  5. 5.   - Prioritize `langQueryParam` if it's a supported language.
  6. 6.   - If not, parse `acceptLanguageHeader` (e.g., `sv-SE,sv;q=0.9,en;q=0.8`) to find the best match among supported languages.
  7. 7.   - Use `Locale.LanguageRange` and `Locale.lookup` for robust `Accept-Language` parsing.
  8. 8.   - Fallback to "en" (English) if no supported language is found.
  9. 9. Implement a public method `List<String> getSupportedLanguages()` that returns the keys from `GreetingConfig.languages`.

#### Step 3.2: Implement Message Formatter Utility

- **Target File:** `src/main/java/com/nordea/demo/helloworld/util/MessageFormatter.java`
- **Detailed Instructions:**
  1. 1. Create a new Java class `MessageFormatter` in the `com.nordea.demo.helloworld.util` package.
  2. 2. Implement a public static method `String formatGreeting(String timeOfDayGreeting, String salutation, String name)`:
  3. 3.   - If `salutation` is provided and not empty, format as `timeOfDayGreeting, salutation name!` (e.g., '¡Buenos días, Señor Gomez!').
  4. 4.   - If `salutation` is not provided, format as `timeOfDayGreeting, name!` (e.g., 'Good morning, Bob!').

#### Step 3.3: Refactor GreetingService for Localization and Salutations

- **Target File:** `src/main/java/com/nordea/demo/helloworld/service/GreetingService.java`
- **Detailed Instructions:**
  1. 1. Inject `GreetingConfig`, `LanguageNegotiationService`, `TimeZoneService`, `TimeOfDayResolver`, and `MessageFormatter` into `GreetingService`.
  2. 2. Create a new public method `Greeting getLocalizedGreeting(GreetingContext context)`:
  3. 3.   - Call `languageNegotiationService.negotiateLanguage(context.language(), acceptLanguageHeader)` (the header will be passed from the controller in SUBTASK-STORY-101-4) to determine the `negotiatedLanguage`.
  4. 4.   - Resolve `ZoneId` from `context.timeZone()` using `TimeZoneService`.
  5. 5.   - Determine `timeOfDay` using `TimeOfDayResolver` and the local time for the resolved `ZoneId`.
  6. 6.   - Retrieve the base greeting phrase from `greetingConfig.languages` using `negotiatedLanguage` and `timeOfDay`.
  7. 7.   - If the specific greeting phrase is not found for the `negotiatedLanguage` and `timeOfDay`, fallback to the English equivalent or a generic English greeting.
  8. 8.   - Construct the `recipient` string: If `context.salutation()` is present, prepend it to `context.name()`.
  9. 9.   - Use `MessageFormatter.formatGreeting()` to create the final `message`.
  10. 10.   - Return a new `Greeting(message, recipient)` record.
  11. 11. Update existing `getGreeting(String name)` and `getDefaultGreeting()` methods to delegate to `getLocalizedGreeting` with default `GreetingContext` values (e.g., English, UTC, no salutation) to maintain backward compatibility.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `com.nordea.demo.helloworld.controller.GreetingController`
- **Breaking Changes:** None (internal `GreetingService` methods are modified, but public API will be adapted in SUBTASK-STORY-101-4)
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Changes are contained within the service layer. Controller adaptation will handle external API contract.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Ensure language negotiation logic is robust against malformed `Accept-Language` headers.; Salutation formatting should not introduce injection vulnerabilities (though unlikely with simple string concatenation).
- **Performance Constraints:** Language negotiation and message formatting should be efficient to meet response latency SLAs.
- **Error Handling Standards:** Graceful fallback to English for unsupported languages (AC4).

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `negotiateLanguage` with `lang` query parameter taking precedence.
  - [ ] Test `negotiateLanguage` with various `Accept-Language` headers (e.g., `sv-SE,sv;q=0.9,en;q=0.8`, `fr`, `de-CH,de;q=0.9`).
  - [ ] Test `negotiateLanguage` with unsupported languages in headers/query to ensure fallback to English.
  - [ ] Test `getSupportedLanguages` returns the correct list from `GreetingConfig`.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/util/MessageFormatterTest.java`
- **Test Scenarios:**
  - [ ] Test `formatGreeting` with a salutation (e.g., 'Good morning', 'Mr', 'John').
  - [ ] Test `formatGreeting` without a salutation (e.g., 'Good afternoon', null, 'Jane').

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] Verify `getLocalizedGreeting` generates localized, time-aware greetings with salutations for all supported languages (mocking dependencies).
  - [ ] Verify `getLocalizedGreeting` falls back to English for unsupported languages.
  - [ ] Verify `getLocalizedGreeting` handles missing salutations gracefully.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 4: Integrate Enhanced Greeting Service into Controller, Handle Headers, and Implement Logging : **Subtask ID:** `SUBTASK-STORY-101-4`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask integrates the enhanced GreetingService into the GreetingController, enabling it to extract all necessary parameters (query, headers) to build a GreetingContext. It ensures backward compatibility for existing endpoints, adds the X-Supported-Languages header on fallback, and introduces structured JSON logging for localization metrics.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java` | **Modify** | API / Controller | Extract query parameters and HTTP headers, construct GreetingContext, delegate to enhanced GreetingService, ensure backward compatibility, add X-Supported-Languages header. |
| `src/main/java/com/nordea/demo/helloworld/logging/StructuredLogger.java` | **Create** | Cross-Cutting Concern | Implement structured JSON logging for localization demand and request metrics. |
| `src/main/resources/application.properties` | **Modify** | Configuration | Add configuration for GreetingConfig and Logback JSON layout. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Implement Structured JSON Logger

- **Target File:** `src/main/java/com/nordea/demo/helloworld/logging/StructuredLogger.java`
- **Detailed Instructions:**
  1. 1. Create a new Java class `StructuredLogger` in the `com.nordea.demo.helloworld.logging` package.
  2. 2. Annotate the class with `@Component`.
  3. 3. Use `org.slf4j.Logger` for logging.
  4. 4. Implement a public method `void logLocalizationRequest(String requestedLang, String negotiatedLang, String timeZone, String timeOfDay, String name)`:
  5. 5.   - Log key-value pairs using `logger.info("Localization Request: {}", Map.of(...))` or similar structured logging approach.
  6. 6.   - Ensure PII (like `name`) is handled according to FIN-GOV-GUARD-001. For this specific service, the `name` field is explicitly *not* considered PII, and therefore no masking or hashing is required for logging purposes.
  7. 7.   - Include fields like `event_id`, `timestamp`, `action` (e.g., `GREETING_REQUEST`), `source_ip` (if available from request context), `correlation_id` (if available).

#### Step 3.2: Modify GreetingController for Enhanced Functionality

- **Target File:** `src/main/java/com/nordea/demo/helloworld/controller/GreetingController.java`
- **Detailed Instructions:**
  1. 1. Inject `GreetingService`, `LanguageNegotiationService`, and `StructuredLogger` into `GreetingController`.
  2. 2. Modify the `@GetMapping("/")` endpoint (`home()` method):
  3. 3.   - Extract optional `@RequestHeader("Time-Zone") String timeZoneHeader` and `@RequestHeader("Accept-Language") String acceptLanguageHeader`.
  4. 4.   - Create a `GreetingContext` with default values (name="World", salutation=null, language=null, timeZone=null).
  5. 5.   - Call `greetingService.getLocalizedGreeting(context)`.
  6. 6.   - Add `X-Supported-Languages` header to the response if language fallback occurred (e.g., `negotiatedLanguage` != `requestedLanguage`).
  7. 7.   - Call `structuredLogger.logLocalizationRequest(...)`.
  8. 8. Modify the `@GetMapping("/hello")` endpoint (`hello(@RequestParam String name)`) to accept additional parameters:
  9. 9.   - Add `@RequestParam(value = "lang", required = false) String langParam`.
  10. 10.   - Add `@RequestParam(value = "salutation", required = false) String salutationParam`.
  11. 11.   - Extract `@RequestHeader("Time-Zone") String timeZoneHeader` and `@RequestHeader("Accept-Language") String acceptLanguageHeader`.
  12. 12.   - Construct `GreetingContext` using all extracted parameters and headers, providing defaults where necessary (e.g., `name` defaults to "World").
  13. 13.   - Call `greetingService.getLocalizedGreeting(context)`.
  14. 14.   - Add `X-Supported-Languages` header to the response if language fallback occurred.
  15. 15.   - Call `structuredLogger.logLocalizationRequest(...)`.
  16. 16. Modify the `@GetMapping("/hello/{name}")` endpoint (`helloWithName(@PathVariable String name)`) to accept additional parameters:
  17. 17.   - Add `@RequestParam(value = "lang", required = false) String langParam`.
  18. 18.   - Add `@RequestParam(value = "salutation", required = false) String salutationParam`.
  19. 19.   - Extract `@RequestHeader("Time-Zone") String timeZoneHeader` and `@RequestHeader("Accept-Language") String acceptLanguageHeader`.
  20. 20.   - Construct `GreetingContext` using all extracted parameters and headers.
  21. 21.   - Call `greetingService.getLocalizedGreeting(context)`.
  22. 22.   - Add `X-Supported-Languages` header to the response if language fallback occurred.
  23. 23.   - Call `structuredLogger.logLocalizationRequest(...)`.
  24. 24. Ensure that for all endpoints, if no language parameters/headers are provided, the response defaults to English, maintaining backward compatibility (AC1).

#### Step 3.3: Update application.properties for Configuration and Logging

- **Target File:** `src/main/resources/application.properties`
- **Detailed Instructions:**
  1. 1. Add `greeting.languages` and `greeting.salutations` properties as defined in SUBTASK-STORY-101-1 (e.g., `greeting.languages.en.morning=Good morning`, `greeting.salutations=Mr,Ms`).
  2. 2. Configure Logback to output JSON format for structured logging. This will primarily involve creating or modifying `src/main/resources/logback-spring.xml` to define a JSON appender and logger configuration.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `All API consumers of /, /hello, /hello/{name} endpoints.`
- **Breaking Changes:** None (backward compatibility is a strict requirement, new features are additive or gracefully fallback).
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Extensive integration testing (SUBTASK-STORY-101-5) to ensure backward compatibility and correct new feature behavior. Feature flags could be considered for new headers if rollout is phased.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Input sanitization for query parameters and headers (Spring Boot handles much of this, but custom validation might be needed for salutations).; Ensure PII masking in logs as per FIN-GOV-GUARD-001.; Authentication/authorization checks (though out of scope for this story, ensure no new vulnerabilities are introduced).
- **Performance Constraints:** Response latency p99 < 50ms under 500 RPS nominal load must be maintained.; Logging should be asynchronous to minimize impact on request processing time.
- **Error Handling Standards:** Standardized exception responses (e.g., HTTP 400 for invalid query parameters, though most validation is handled by fallback).; Logging of errors and warnings should follow established guidelines.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- None specified.

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Verify GET / and GET /hello (without params) return legacy payload and 200 OK.
  - [ ] Fulfills AC2: Verify GET /hello?name=Gomez&salutation=Señor&lang=es with Time-Zone: Europe/Madrid returns localized, time-aware greeting with salutation.
  - [ ] Fulfills AC3: Verify GET /hello?name=Lindqvist&salutation=Fru with Accept-Language: sv-SE and Time-Zone: Europe/Stockholm returns Swedish time-aware greeting.
  - [ ] Fulfills AC4: Verify GET /hello?name=Mario&lang=it returns English fallback and X-Supported-Languages header.
  - [ ] Fulfills AC5: Verify GET /hello/Bob with Accept-Language: de and Time-Zone: Europe/Berlin returns German afternoon greeting.
  - [ ] Verify `X-Supported-Languages` header is present when language fallback occurs.
  - [ ] Verify structured JSON logs are emitted for relevant requests (can use a test appender or mock `StructuredLogger`).


---

## Subtask 5: Comprehensive Test Suite Update & Refinement : **Subtask ID:** `SUBTASK-STORY-101-5`

**Parent Story ID:** `STORY-101`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask focuses on ensuring comprehensive test coverage for all new features and modified components. It involves updating existing controller tests and creating new dedicated unit test classes for the newly introduced services and utilities.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java` | **Modify** | Integration Test | Update existing integration tests and add new ones to cover all ACs, header parsing, query parameters, language negotiation, time zone handling, and fallback scenarios. |
| `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java` | **Create** | Unit Test | Create dedicated unit tests for the enhanced GreetingService logic. |
| `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java` | **Create** | Unit Test | Create dedicated unit tests for TimeZoneService. |
| `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java` | **Create** | Unit Test | Create dedicated unit tests for LanguageNegotiationService. |
| `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java` | **Create** | Unit Test | Create dedicated unit tests for TimeOfDayResolver. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Update GreetingController Integration Tests

- **Target File:** `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java`
- **Detailed Instructions:**
  1. 1. Update the `setUp()` method to ensure the `RestTestClient` is configured to use the fully integrated `GreetingController` (potentially using `@SpringBootTest` with mocked dependencies or a full application context).
  2. 2. Add new `@Test` methods to cover all scenarios described in AC1-AC5 of the User Story.
  3. 3. Specifically, add tests for:
  4. 4.   - Backward compatibility of `/`, `/hello`, `/hello/{name}` without new parameters (AC1).
  5. 5.   - Localized greetings with explicit `lang`, `salutation`, and `Time-Zone` headers (AC2).
  6. 6.   - Automatic language negotiation via `Accept-Language` header and `Time-Zone` (AC3).
  7. 7.   - Fallback to English for unsupported languages, including verification of the `X-Supported-Languages` response header (AC4).
  8. 8.   - Path variable endpoint with `Accept-Language` and `Time-Zone` (AC5).
  9. 9.   - Verify HTTP status codes (200 OK) and JSON payload structures for all scenarios.
  10. 10.   - Verify the presence and content of the `X-Supported-Languages` header when applicable.

#### Step 3.2: Create Unit Tests for GreetingService

- **Target File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Detailed Instructions:**
  1. 1. Create a new JUnit 5 test class `GreetingServiceTest` in `src/test/java/com/nordea/demo/helloworld/service`.
  2. 2. Use `@ExtendWith(MockitoExtension.class)` and `@Mock` annotations to mock `GreetingConfig`, `LanguageNegotiationService`, `TimeZoneService`, `TimeOfDayResolver`, and `MessageFormatter`.
  3. 3. Write unit tests for the `getLocalizedGreeting(GreetingContext context)` method, covering:
  4. 4.   - Successful generation of localized, time-aware greetings with salutations for various valid inputs.
  5. 5.   - Correct behavior when language negotiation results in a specific language.
  6. 6.   - Correct fallback to English when an unsupported language is requested.
  7. 7.   - Handling of null or empty salutations and names.

#### Step 3.3: Create Unit Tests for TimeZoneService

- **Target File:** `src/test/java/com/nordea/demo/helloworld/service/TimeZoneService.java`
- **Detailed Instructions:**
  1. 1. Create a new JUnit 5 test class `TimeZoneServiceTest` in `src/test/java/com/nordea/demo/helloworld/service`.
  2. 2. Write unit tests for the `resolveTimeZone(String timeZoneHeader)` method, covering:
  3. 3.   - Valid IANA time zone identifiers (e.g., 'Europe/Paris', 'America/New_York').
  4. 4.   - Invalid time zone identifiers (e.g., 'Invalid/Zone') to ensure fallback to UTC.
  5. 5.   - Null or empty `timeZoneHeader` inputs to ensure fallback to UTC.

#### Step 3.4: Create Unit Tests for LanguageNegotiationService

- **Target File:** `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java`
- **Detailed Instructions:**
  1. 1. Create a new JUnit 5 test class `LanguageNegotiationServiceTest` in `src/test/java/com/nordea/demo/helloworld/service`.
  2. 2. Use `@Mock` for `GreetingConfig` and set up mock behavior for `getSupportedLanguages()`.
  3. 3. Write unit tests for the `negotiateLanguage(String langQueryParam, String acceptLanguageHeader)` method, covering:
  4. 4.   - `langQueryParam` taking precedence over `Accept-Language`.
  5. 5.   - Various `Accept-Language` header values (e.g., `sv-SE,sv;q=0.9,en;q=0.8`, `fr`, `de-CH,de;q=0.9`).
  6. 6.   - Scenarios where no supported language is found in headers/query, ensuring fallback to English.
  7. 7.   - Edge cases like empty or malformed headers.

#### Step 3.5: Create Unit Tests for TimeOfDayResolver

- **Target File:** `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java`
- **Detailed Instructions:**
  1. 1. Create a new JUnit 5 test class `TimeOfDayResolverTest` in `src/test/java/com/nordea/demo/helloworld/util`.
  2. 2. Write unit tests for the `getTimeOfDay(LocalTime localTime)` method, covering:
  3. 3.   - Various `LocalTime` values that fall into the 'Morning' category (05:00-11:59).
  4. 4.   - Various `LocalTime` values that fall into the 'Afternoon' category (12:00-17:59).
  5. 5.   - Various `LocalTime` values that fall into the 'Evening' category (18:00-04:59).
  6. 6.   - Boundary conditions (e.g., 04:59, 05:00, 11:59, 12:00, 17:59, 18:00).

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** None
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Ensuring high test coverage reduces the risk of regressions and undetected bugs in new features.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Ensure test data does not contain real PII or sensitive information.; Tests should validate proper error handling and fallback mechanisms.
- **Performance Constraints:** Unit tests should run quickly (sub-second) to support rapid development cycles.; Integration tests should be efficient enough to run frequently in CI/CD.
- **Error Handling Standards:** Tests should explicitly verify that error conditions (e.g., invalid time zones, unsupported languages) result in expected fallback behavior or error responses.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] Test successful localized and time-aware greeting generation.
  - [ ] Test language fallback to English.
  - [ ] Test handling of various salutation and name combinations.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/TimeZoneServiceTest.java`
- **Test Scenarios:**
  - [ ] Test valid IANA time zone resolution.
  - [ ] Test invalid time zone fallback to UTC.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/service/LanguageNegotiationServiceTest.java`
- **Test Scenarios:**
  - [ ] Test language negotiation priority (query param > Accept-Language).
  - [ ] Test `Accept-Language` parsing and matching.
  - [ ] Test fallback to English for unsupported languages.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/util/TimeOfDayResolverTest.java`
- **Test Scenarios:**
  - [ ] Test correct categorization for Morning, Afternoon, and Evening time ranges.

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/controller/GreetingControllerTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Verify backward compatibility for legacy endpoints.
  - [ ] Fulfills AC2: Verify localized greeting with explicit parameters and time zone.
  - [ ] Fulfills AC3: Verify Nordic locale support and `Accept-Language` negotiation.
  - [ ] Fulfills AC4: Verify fallback behavior for unsupported languages and `X-Supported-Languages` header.
  - [ ] Fulfills AC5: Verify path variable endpoint with client time-aware greeting.


---

## Open Questions & Clarifications Needed

- None at this time.

## Agent Assumptions Made

- **Assumption 1:** Time partition logic evaluates local client time: Morning (05:00-11:59), Afternoon (12:00-17:59), Evening (18:00-04:59).
- **Assumption 2:** Invalid or missing `Time-Zone` header values fall back safely to UTC without throwing client 4xx errors.
- **Assumption 3:** Legacy responses without query parameters remain byte-compatible with the existing `Greeting` record structure.
- **Assumption 4:** The `Accept-Language` header negotiation will prioritize the first supported language in the list, or the one with the highest 'q' value if multiple supported languages are present.
- **Assumption 5:** New configuration for `GreetingConfig` (languages and salutations) will be added to `application.properties` or `application.yml`.
- **Assumption 6:** Structured JSON logging will be implemented using Logback with a JSON layout, configured in `src/main/resources/logback-spring.xml`.

## Revision Changelog

- v1.0: Initial PR creation for tech lead review.v1.1: Addressed audit findings CHK-001 (clarified PII status of 'name' in logging) and CHK-003 (standardized Logback configuration file to logback-spring.xml).

## Done When Checklist

- [ ] Implementation plan was generated from all target subtasks in (`tasks/<story_id>/subtasks.md`) and parent story (`user-stories/<story_id>.md`).
- [ ] All file additions, modifications, and deletions are explicitly listed with exact relative paths.
- [ ] Blast radius and security guardrails are fully evaluated in Sections 4 and 5.
- [ ] Unit and integration test specifications map directly to parent User Story BDD acceptance criteria.
- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.
- [ ] The plan was saved to `implementation-plans/STORY-101/plan.md` on `SDLC_GOVERNANCE_REPO`.
- [ ] A GitHub Pull Request was created targeting `main` for human review.