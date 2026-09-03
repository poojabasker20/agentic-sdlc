# Implementation Blueprint: Localized and Personalized Greeting Service

**Story ID:** `STORY-102`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 5 PRs

## Subtask 1: Localization Data Structures & Configuration : **Subtask ID:** `SUBTASK-STORY-102-1`

**Parent Story ID:** `STORY-102`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask introduces new classes and property files to manage localized greeting messages based on language and time of day. It defines an enum for `TimeOfDay` (e.g., MORNING, AFTERNOON, EVENING, NIGHT) to categorize different parts of the day for time-aware greetings. These resources will store the various greeting phrases for supported languages, fulfilling AC2, AC3, and AC4.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/localization/GreetingLocaleConfig.java` | **Create** | Configuration / Utility | New class to configure and manage localized message sources. |
| `src/main/java/com/nordea/demo/helloworld/localization/TimeOfDay.java` | **Create** | Utility / Enum | New enum to represent different parts of the day for time-aware greetings. |
| `src/main/resources/messages_de.properties` | **Create** | Resource / Localization | Property file for German localized greeting messages. |
| `src/main/resources/messages_fi.properties` | **Create** | Resource / Localization | Property file for Finnish localized greeting messages. |
| `src/main/resources/messages_fr.properties` | **Create** | Resource / Localization | Property file for French localized greeting messages. |
| `src/main/resources/messages_en.properties` | **Create** | Resource / Localization | Property file for English localized greeting messages (default). |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Define TimeOfDay Enum

- **Target File:** `src/main/java/com/nordea/demo/helloworld/localization/TimeOfDay.java`
- **Detailed Instructions:**
  1. Define a public enum `TimeOfDay` with values like MORNING, AFTERNOON, EVENING, NIGHT.
  2. Implement a static factory method `fromHour(int hour)` that takes an hour (0-23) and returns the corresponding `TimeOfDay` enum value based on predefined ranges (e.g., MORNING: 5-11, AFTERNOON: 12-16, EVENING: 17-21, NIGHT: 22-4).

#### Step 3.2: Create Localization Property Files

- **Target File:** `src/main/resources/messages_xx.properties`
- **Detailed Instructions:**
  1. Create `messages_de.properties`, `messages_fi.properties`, `messages_fr.properties`, and `messages_en.properties` in `src/main/resources`.
  2. Populate each file with key-value pairs for different greeting types (e.g., `greeting.morning=Guten Morgen`, `greeting.afternoon=Guten Tag`, `greeting.evening=Guten Abend`, `greeting.night=Gute Nacht`).
  3. Include a key for unsupported language notification (e.g., `greeting.unsupported.language=Requested language is unsupported. Hello, {0}!`).

#### Step 3.3: Implement GreetingLocaleConfig

- **Target File:** `src/main/java/com/nordea/demo/helloworld/localization/GreetingLocaleConfig.java`
- **Detailed Instructions:**
  1. Create a `@Configuration` class `GreetingLocaleConfig`.
  2. Define a `@Bean` method that returns a `ReloadableResourceBundleMessageSource`.
  3. Configure the `MessageSource` to load `messages` from the classpath, set default encoding to UTF-8, and enable caching.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** None
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** N/A

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Ensure property files do not contain sensitive information.
- **Performance Constraints:** MessageSource caching should be configured to prevent performance degradation from repeated file reads.
- **Error Handling Standards:** Default messages should be provided for missing keys in property files.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/localization/TimeOfDayTest.java`
- **Test Scenarios:**
  - [ ] Test `fromHour` method for correct categorization of hours into MORNING, AFTERNOON, EVENING, NIGHT.
  - [ ] Test edge cases for hour boundaries (e.g., 4, 5, 11, 12, 16, 17, 21, 22).

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/localization/GreetingLocaleConfigTest.java`
- **Test Scenarios:**
  - [ ] Test correct loading and retrieval of localized messages from `MessageSource` for 'en', 'de', 'fi', 'fr' locales.
  - [ ] Test retrieval of default message for an unsupported locale or missing key.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 2: Core Localization & Personalization Service Logic : **Subtask ID:** `SUBTASK-STORY-102-2`

**Parent Story ID:** `STORY-102`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1-2 PRs

### 1. Executive Summary & Objective

This subtask refactors the `GreetingService` to incorporate new methods for resolving `Locale` from `Accept-Language` headers and `ZoneId` from `X-Timezone-Offset` or `ZoneId` headers. It implements logic to determine the `TimeOfDay` based on the resolved timezone, prioritizing `X-Timezone-Offset` and defaulting to UTC if invalid/missing. Localized greetings are constructed using data from Subtask 1, including handling unsupported languages with explicit notifications and applying optional professional titles. This fulfills AC1, AC2, AC3, and AC4.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/GreetingService.java` | **Modify** | Business Logic | Refactor to include localization, timezone, time-of-day resolution, and personalized greeting generation. |
| `src/main/java/com/nordea/demo/helloworld/localization/LocaleResolver.java` | **Create** | Utility | New class to resolve `Locale` from `Accept-Language` headers. |
| `src/main/java/com/nordea/demo/helloworld/localization/TimezoneResolver.java` | **Create** | Utility | New class to resolve `ZoneId` from `X-Timezone-Offset` or `ZoneId` headers. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Create LocaleResolver

- **Target File:** `src/main/java/com/nordea/demo/helloworld/localization/LocaleResolver.java`
- **Detailed Instructions:**
  1. Create a `@Component` class `LocaleResolver`.
  2. Implement a method `resolveLocale(String acceptLanguageHeader)` that parses the `Accept-Language` header.
  3. Return a `Locale` object, defaulting to `Locale.ENGLISH` if the header is missing or invalid, or if the requested language is not explicitly supported (de, fi, fr, en).

#### Step 3.2: Create TimezoneResolver

- **Target File:** `src/main/java/com/nordea/demo/helloworld/localization/TimezoneResolver.java`
- **Detailed Instructions:**
  1. Create a `@Component` class `TimezoneResolver`.
  2. Implement a method `resolveZoneId(String xTimezoneOffset, String zoneIdHeader)`.
  3. Prioritize `xTimezoneOffset`: if present and valid, parse it (e.g., '+02:00' to `ZoneOffset`).
  4. If `xTimezoneOffset` is invalid or missing, try to parse `zoneIdHeader` (e.g., 'Europe/Helsinki' to `ZoneId`).
  5. If both are invalid or missing, default to `ZoneOffset.UTC`.

#### Step 3.3: Refactor GreetingService

- **Target File:** `src/main/java/com/nordea/demo/helloworld/GreetingService.java`
- **Detailed Instructions:**
  1. Inject `LocaleResolver`, `TimezoneResolver`, and `MessageSource` (from `GreetingLocaleConfig`) into `GreetingService`.
  2. Modify the existing `getGreeting(String name)` method or create a new overloaded method `getGreeting(String name, String title, String acceptLanguage, String xTimezoneOffset, String zoneId)`.
  3. Inside the new method:
  4. 1. Use `LocaleResolver` to get the `Locale` from `acceptLanguage`.
  5. 2. Use `TimezoneResolver` to get the `ZoneId` from `xTimezoneOffset` and `zoneId`.
  6. 3. Determine the current `TimeOfDay` using `LocalTime.now(zoneId)` and `TimeOfDay.fromHour()`.
  7. 4. Construct the greeting message key (e.g., `greeting.morning`).
  8. 5. Use `MessageSource.getMessage()` with the resolved `Locale` and message key to get the localized greeting.
  9. 6. If the resolved `Locale` is not one of the explicitly supported languages (de, fi, fr, en), retrieve the 'unsupported language' message from `MessageSource` and format it.
  10. 7. Construct the `recipient` string, prepending the `title` if provided.
  11. 8. Return a new `Greeting` record.
  12. Ensure the original `getGreeting(String name)` and `getDefaultGreeting()` methods continue to function as before for backward compatibility, potentially by calling the new method with null/default parameters.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `GreetingController (will need to be updated to call new service methods)`
- **Breaking Changes:** None (backward compatibility for existing methods is maintained)
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Ensure existing `GreetingService` methods are preserved or gracefully delegate to new logic with default parameters to maintain backward compatibility.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Input sanitization for `name` and `title` parameters to prevent injection attacks.; Validate `Accept-Language`, `X-Timezone-Offset`, and `ZoneId` headers to prevent malformed input from causing errors.; Adhere to FIN-GOV-GUARD-001: Ensure no plain-text PII is logged or persisted in diagnostic logs, especially from `name` or `title`.
- **Performance Constraints:** Locale and Timezone resolution logic should be efficient to maintain sub-10ms response latency.
- **Error Handling Standards:** Handle `DateTimeParseException` for invalid timezone inputs gracefully, falling back to UTC.; Provide explicit notification for unsupported languages as per AC4.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/localization/LocaleResolverTest.java`
- **Test Scenarios:**
  - [ ] Test `resolveLocale` with valid `Accept-Language` headers (e.g., 'de-DE', 'fi', 'fr', 'en-US').
  - [ ] Test `resolveLocale` with multiple languages in header (e.g., 'de-DE,en-US;q=0.9').
  - [ ] Test `resolveLocale` with missing or invalid `Accept-Language` header, expecting default to English.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/localization/TimezoneResolverTest.java`
- **Test Scenarios:**
  - [ ] Test `resolveZoneId` with valid `X-Timezone-Offset` (e.g., '+02:00', '-05:30').
  - [ ] Test `resolveZoneId` with valid `ZoneId` (e.g., 'Europe/Helsinki', 'America/New_York').
  - [ ] Test `resolveZoneId` with both `X-Timezone-Offset` and `ZoneId`, verifying `X-Timezone-Offset` precedence.
  - [ ] Test `resolveZoneId` with invalid or missing headers, expecting fallback to UTC.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/GreetingServiceTest.java`
- **Test Scenarios:**
  - [ ] Test `getGreeting` for correct localized messages for German, Finnish, French, English across different times of day (morning, afternoon, evening, night) with valid timezone headers (Fulfills AC2, AC3).
  - [ ] Test `getGreeting` with `title` parameter, verifying correct recipient formatting (e.g., 'Dr. Schmidt').
  - [ ] Test `getGreeting` with an unsupported language, verifying the explicit notification message (Fulfills AC4).
  - [ ] Test `getGreeting` with missing localization headers, verifying backward compatibility and default English greeting (Fulfills AC1).
  - [ ] Test `getGreeting` with invalid timezone headers, verifying fallback to UTC and correct time-of-day calculation.

#### Integration & API Contract Tests

- None specified.


---

## Subtask 3: Enhance GreetingController Endpoints : **Subtask ID:** `SUBTASK-STORY-102-3`

**Parent Story ID:** `ST0RY-102`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask updates the existing `GreetingController` methods (`@GetMapping("/hello")` and `@GetMapping("/hello/{name}")`) to accept `Accept-Language`, `X-Timezone-Offset`, and `ZoneId` headers, and an optional `title` query parameter. These new parameters will be extracted from the HTTP request and passed to the enhanced `GreetingService` for processing, with `X-Timezone-Offset` taking precedence for timezone resolution. The root endpoint (`@GetMapping("/")`) will remain unchanged to ensure strict backward compatibility. This fulfills AC1, AC2, AC3, and AC4.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/GreetingController.java` | **Modify** | API / Controller | Update existing /hello endpoints to accept new headers and query parameters for localization and personalization. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Modify /hello Endpoint for Query Parameters and Headers

- **Target File:** `src/main/java/com/nordea/demo/helloworld/GreetingController.java`
- **Detailed Instructions:**
  1. Modify the `hello(@RequestParam(value = "name", defaultValue = "World") String name)` method.
  2. Add `@RequestHeader(value = "Accept-Language", required = false) String acceptLanguageHeader`.
  3. Add `@RequestHeader(value = "X-Timezone-Offset", required = false) String xTimezoneOffsetHeader`.
  4. Add `@RequestHeader(value = "ZoneId", required = false) String zoneIdHeader`.
  5. Add `@RequestParam(value = "title", required = false) String title`.
  6. Update the method body to call the enhanced `GreetingService` method, passing all resolved parameters (name, title, acceptLanguageHeader, xTimezoneOffsetHeader, zoneIdHeader).

#### Step 3.2: Modify /hello/{name} Endpoint for Path Variable and Headers

- **Target File:** `src/main/java/com/nordea/demo/helloworld/GreetingController.java`
- **Detailed Instructions:**
  1. Modify the `helloWithName(@PathVariable String name)` method.
  2. Add `@RequestHeader(value = "Accept-Language", required = false) String acceptLanguageHeader`.
  3. Add `@RequestHeader(value = "X-Timezone-Offset", required = false) String xTimezoneOffsetHeader`.
  4. Add `@RequestHeader(value = "ZoneId", required = false) String zoneIdHeader`.
  5. Add `@RequestParam(value = "title", required = false) String title`.
  6. Update the method body to call the enhanced `GreetingService` method, passing all resolved parameters (name, title, acceptLanguageHeader, xTimezoneOffsetHeader, zoneIdHeader).

#### Step 3.3: Ensure Root Endpoint Backward Compatibility

- **Target File:** `src/main/java/com/nordea/demo/helloworld/GreetingController.java`
- **Detailed Instructions:**
  1. Verify that the `home()` method mapped to `@GetMapping("/")` remains unchanged and continues to return the default 'Hello, World!' message, fulfilling AC1.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `Clients calling /hello or /hello/{name} endpoints (new headers/params are optional, so no breaking changes for existing clients).`, `Integration tests for GreetingController.`
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Ensure all new parameters are `required = false` to maintain backward compatibility for existing clients. Thorough integration testing is crucial.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Input validation on `title` query parameter to prevent malicious input.; Ensure headers are not directly logged without sanitization if they contain sensitive information (though these headers are not expected to).
- **Performance Constraints:** Header and query parameter parsing should be efficient to maintain sub-10ms response latency.
- **Error Handling Standards:** Return appropriate HTTP status codes (e.g., 400 Bad Request) for invalid input if validation fails, though current design handles invalid values gracefully with fallbacks.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- None specified.

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Verify GET / returns 'Hello, World!'.
  - [ ] Fulfills AC1: Verify GET /hello without headers/params returns 'Hello, World!'.
  - [ ] Fulfills AC1: Verify GET /hello/Alice without headers/params returns 'Hello, Alice!'.
  - [ ] Fulfills AC2, AC3: Verify GET /hello?name=Schmidt with Accept-Language='de', X-Timezone-Offset='+01:00', title='Dr.' returns 'Guten Morgen, Dr. Schmidt!' (assuming morning hours).
  - [ ] Fulfills AC2, AC3: Verify GET /hello/Virtanen with Accept-Language='fi', ZoneId='Europe/Helsinki' returns a Finnish greeting.
  - [ ] Fulfills AC4: Verify GET /hello?name=User with Accept-Language='xx-YY' returns the unsupported language notification.
  - [ ] Test precedence: Verify `X-Timezone-Offset` takes precedence over `ZoneId` when both are provided.
  - [ ] Test fallback: Verify UTC is used when both timezone headers are invalid or missing.


---

## Subtask 4: Telemetry Integration for Regional Requests : **Subtask ID:** `SUBTASK-STORY-102-4`

**Parent Story ID:** `STORY-102`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask introduces a new component (`GreetingMetrics`) to manage and increment a `greeting.requests.locale` counter using Micrometer. This metrics component will be integrated into the `GreetingService` to record the resolved locale (or 'unsupported'/'default') for each greeting request. Strict adherence to FIN-GOV-GUARD-001 will ensure that no plain-text PII is persisted or logged in diagnostic logs. This fulfills AC5.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/main/java/com/nordea/demo/helloworld/GreetingService.java` | **Modify** | Business Logic | Inject `GreetingMetrics` and call its methods to record locale usage. |
| `src/main/java/com/nordea/demo/helloworld/metrics/GreetingMetrics.java` | **Create** | Monitoring / Metrics | New class to define and manage Micrometer counters for regional greeting requests. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Create GreetingMetrics Component

- **Target File:** `src/main/java/com/nordea/demo/helloworld/metrics/GreetingMetrics.java`
- **Detailed Instructions:**
  1. Create a `@Component` class `GreetingMetrics`.
  2. Inject `MeterRegistry` (Micrometer's central registry) into `GreetingMetrics`.
  3. Define a `Counter` named `greeting.requests.locale` using `MeterRegistry.counter()`.
  4. Implement a public method `incrementLocaleCounter(String localeTag)` that increments this counter, adding a tag for the resolved locale (e.g., 'en', 'de', 'unsupported', 'default').

#### Step 3.2: Integrate Metrics into GreetingService

- **Target File:** `src/main/java/com/nordea/demo/helloworld/GreetingService.java`
- **Detailed Instructions:**
  1. Inject `GreetingMetrics` into `GreetingService`.
  2. In the enhanced `getGreeting` method (from SUBTASK-STORY-102-2), after resolving the `Locale` (and determining if it's supported or default), call `greetingMetrics.incrementLocaleCounter()` with the appropriate locale tag (e.g., `locale.getLanguage()`, 'unsupported', 'default').

#### Step 3.3: Verify PII Compliance

- **Target File:** `src/main/java/com/nordea/demo/helloworld/GreetingService.java`
- **Detailed Instructions:**
  1. Review all logging statements in `GreetingService` and `GreetingController` to ensure no plain-text PII (e.g., `name`, `title`) is logged, in compliance with FIN-GOV-GUARD-001.

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** `Monitoring systems that scrape Micrometer metrics.`
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** Ensure metric names and tags are consistent and well-documented for downstream monitoring systems. Verify PII compliance through automated checks and manual review.

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** FIN-GOV-GUARD-001: Zero plain-text PII must be persisted or logged in diagnostic logs. This applies to metric tags as well; only aggregated, non-identifiable data should be used.; Ensure metric tags do not inadvertently expose sensitive information.
- **Performance Constraints:** Metric incrementation should have minimal overhead to avoid impacting response latency.
- **Error Handling Standards:** N/A (metrics are typically fire-and-forget, failures should not impact core business logic).

### 6. Comprehensive Testing Strategy

#### Unit Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/metrics/GreetingMetricsTest.java`
- **Test Scenarios:**
  - [ ] Test `incrementLocaleCounter` method, verifying that the `greeting.requests.locale` counter is incremented for various locale tags (e.g., 'en', 'de', 'unsupported', 'default').
  - [ ] Verify that tags are correctly applied to the counter.

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/GreetingIntegrationTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC5: Verify that the `greeting.requests.locale` metric is incremented correctly for requests with supported locales (e.g., 'de', 'fi', 'fr').
  - [ ] Fulfills AC5: Verify that the `greeting.requests.locale` metric is incremented for unsupported locales ('unsupported' tag).
  - [ ] Fulfills AC5: Verify that the `greeting.requests.locale` metric is incremented for default requests ('default' tag).
  - [ ] Fulfills AC5: Confirm through log inspection that no PII is present in diagnostic logs after processing requests.


---

## Subtask 5: Comprehensive Integration & Performance Testing : **Subtask ID:** `SUBTASK-STORY-102-5`

**Parent Story ID:** `STORY-102`  
**Target Repository:** `poojabasker20/springboot-hello-world`  
**Status:** Ready for Technical Review  
**Estimated Scope:** 1 PR

### 1. Executive Summary & Objective

This subtask expands the existing `GreetingControllerTest` and creates a new `GreetingIntegrationTest` class to cover all new acceptance criteria end-to-end. This includes testing various combinations of `Accept-Language`, `X-Timezone-Offset`, `name`, and `title` parameters. It will verify backward compatibility, correct localized responses, unsupported language notifications, and metric incrementation. Assertions for response latency will be included to ensure the sub-10ms requirement is met. This fulfills AC1, AC2, AC3, AC4, and AC5.

### 2. Affected Files & File Change Delta Matrix

| Relative File Path | Action | Layer / Component | Description of Changes |
| ------------------ | ------ | ----------------- | ---------------------- |
| `src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java` | **Modify** | Integration Test | Expand existing tests to cover new header and query parameter combinations for /hello endpoints. |
| `src/test/java/com/nordea/demo/helloworld/GreetingIntegrationTest.java` | **Create** | Integration Test | New class for comprehensive end-to-end integration tests covering all ACs, including metrics and performance. |

### 3. Step-by-Step Technical Implementation Guide

#### Step 3.1: Expand GreetingControllerTest

- **Target File:** `src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java`
- **Detailed Instructions:**
  1. Add new `@Test` methods to `GreetingControllerTest` (using `RestTestClient.bindToController`) to verify the behavior of `/hello` and `/hello/{name}` with various combinations of `Accept-Language`, `X-Timezone-Offset`, `ZoneId`, and `title` headers/parameters.
  2. Ensure tests cover successful localized greetings (AC2, AC3), unsupported language notifications (AC4), and backward compatibility (AC1).

#### Step 3.2: Create GreetingIntegrationTest

- **Target File:** `src/test/java/com/nordea/demo/helloworld/GreetingIntegrationTest.java`
- **Detailed Instructions:**
  1. Create a new class `GreetingIntegrationTest` annotated with `@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)`.
  2. Inject `WebTestClient` for making HTTP requests to the running application context.
  3. Inject `MeterRegistry` to verify metric values.
  4. Implement `@Test` methods to cover all Acceptance Criteria end-to-end:
  5. 1. **AC1 (Backward Compatibility):** Test `/`, `/hello`, `/hello/{name}` without localization headers/params.
  6. 2. **AC2, AC3 (Localized & Time-Aware):** Test various combinations of `Accept-Language`, `X-Timezone-Offset`/`ZoneId`, `name`, and `title` for German, Finnish, French, and English, verifying correct localized responses.
  7. 3. **AC4 (Unsupported Language):** Test with an unsupported `Accept-Language` header, verifying the explicit notification message.
  8. 4. **AC5 (Telemetry):** After each relevant request, query `MeterRegistry` to assert that the `greeting.requests.locale` counter has incremented correctly for the respective locale tag.
  9. 5. **Performance:** For key integration tests, include assertions on response time to ensure latency is below 10ms (e.g., using `Duration.ofMillis(10)`).

### 4. Blast Radius & Impact Analysis

- **Downstream Components Impacted:** None
- **Breaking Changes:** None
- **Database / Migration Impact:** N/A
- **Risk Mitigation Strategy:** N/A

### 5. Security, Performance & Compliance Guardrails

- **Security Requirements:** Ensure test data used in integration tests does not contain or expose any real PII.; Verify that logging during test execution does not contain PII (FIN-GOV-GUARD-001).
- **Performance Constraints:** Integration tests should include assertions for response latency to ensure the sub-10ms requirement is met (p99 < 50ms).
- **Error Handling Standards:** Integration tests should verify that the application handles invalid inputs gracefully and returns appropriate HTTP status codes or fallback messages.

### 6. Comprehensive Testing Strategy

#### Unit Tests

- None specified.

#### Integration & API Contract Tests

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/GreetingControllerTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Test root endpoint returns default 'Hello, World!'.
  - [ ] Fulfills AC1: Test /hello with default name and no headers.
  - [ ] Fulfills AC1: Test /hello/{name} with no headers.
  - [ ] Fulfills AC2, AC3: Test /hello with name, title, Accept-Language, X-Timezone-Offset for supported languages and time of day.
  - [ ] Fulfills AC4: Test /hello with unsupported Accept-Language.

- **Target Test File:** `src/test/java/com/nordea/demo/helloworld/GreetingIntegrationTest.java`
- **BDD Scenario Mapping:**
  - [ ] Fulfills AC1: Verify GET / returns default 'Hello, World!' with 200 OK.
  - [ ] Fulfills AC1: Verify GET /hello without headers/params returns default 'Hello, World!' with 200 OK.
  - [ ] Fulfills AC1: Verify GET /hello/Alice without headers/params returns 'Hello, Alice!' with 200 OK.
  - [ ] Fulfills AC2, AC3: Verify GET /hello?name=Schmidt with Accept-Language='de', X-Timezone-Offset='+01:00', title='Dr.' returns 'Guten Morgen, Dr. Schmidt!' (or appropriate time-of-day greeting) with 200 OK and sub-10ms latency.
  - [ ] Fulfills AC2, AC3: Verify GET /hello/Virtanen with Accept-Language='fi', ZoneId='Europe/Helsinki' returns a Finnish greeting with 200 OK and sub-10ms latency.
  - [ ] Fulfills AC4: Verify GET /hello?name=User with Accept-Language='xx-YY' returns the unsupported language notification with 200 OK.
  - [ ] Fulfills AC5: Verify `greeting.requests.locale` counter increments for 'de', 'fi', 'fr', 'en', 'unsupported', and 'default' tags after respective requests.
  - [ ] Verify response latency for all key scenarios is consistently below 10ms.


---

## Open Questions & Clarifications Needed

- None at this time.

## Agent Assumptions Made

- **Assumption 1:** The existing `Greeting` record structure (`message`, `recipient`) is sufficient, and only its fields need dynamic population based on localization and personalization logic.
- **Assumption 2:** Time-of-day segments for greetings (e.g., morning, afternoon, evening, night) will be defined based on common conventions (e.g., morning 05:00-11:59, afternoon 12:00-16:59, evening 17:00-21:59, night 22:00-04:59).
- **Assumption 3:** The `title` query parameter is optional and, if provided, will be prepended to the `name` in the `recipient` field.
- **Assumption 4:** Micrometer is the chosen metrics library for implementing the telemetry requirements.
- **Assumption 5:** When both `X-Timezone-Offset` and `ZoneId` headers are provided, `X-Timezone-Offset` will take precedence. If both are invalid or missing, the system will default to UTC for time zone resolution.

## Revision Changelog

- v1.0: Initial PR creation for tech lead review.

## Done When Checklist

- [ ] Implementation plan was generated from all target subtasks in (`tasks/<story_id>/subtasks.md`) and parent story (`user-stories/<story_id>.md`).
- [ ] All file additions, modifications, and deletions are explicitly listed with exact relative paths.
- [ ] Blast radius and security guardrails are fully evaluated in Sections 4 and 5.
- [ ] Unit and integration test specifications map directly to parent User Story BDD acceptance criteria.
- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.
- [ ] The plan was saved to `implementation-plans/STORY-102/plan.md` on `SDLC_GOVERNANCE_REPO`.
- [ ] A GitHub Pull Request was created targeting `main` for human review.