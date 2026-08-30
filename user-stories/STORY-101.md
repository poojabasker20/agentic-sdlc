# Multi-Language and Time-Aware Personalized Greeting Service

**Issue Type:** User Story  
**Status:** Ready for Development  
**Priority:** High

## 1. Description

**As an** International Client Application or Portal Developer,  
**I want to** retrieve culturally aware, time-sensitive, and localized greeting responses via REST endpoints with optional salutation and language selection,  
**So that** international customers across Europe experience a personalized, polite, and natural first touchpoint without breaking legacy API integrations.

## 2. Business Context & Background

As part of our expansion across Europe (Spain, France, Germany, Sweden, and UK), our client portals and partner applications require a localized, respectful, and intelligent greeting service. The current service returns static English greetings regardless of locale, client identity, or time of day. This user story extends the core greeting service to support multi-language greetings (`en`, `es`, `fr`, `de`, `sv`), time-of-day dynamic messaging (Morning / Afternoon / Evening), formal salutations (e.g., Herr, Madame, Señor, Dr.), and automatic language negotiation (`Accept-Language`), while preserving complete backward compatibility with existing API contracts.

## 3. Acceptance Criteria

- **AC1: Backward Compatibility on Legacy Root and Default Hello Endpoints**
  - **Given** The Greeting API service is running
  - **When** A client sends a GET request to `/` or `/hello` without language or salutation parameters
  - **Then** The response status code is 200 OK
  - **Then** The response payload matches the existing contract: `{"message": "Hello, World!", "recipient": "World"}`

- **AC2: Localized Greeting with Explicit Language Parameter and Salutation**
  - **Given** Supported language `es` (Spanish) and salutation `Señor`
  - **When** A client sends a GET request to `/hello?name=Gomez&salutation=Señor&lang=es`
  - **Then** The response status code is 200 OK
  - **Then** The recipient field is formatted as `Señor Gomez`
  - **Then** The message contains the appropriate Spanish greeting for the current time of day (e.g., `¡Buenos días, Señor Gomez!`)

- **AC3: Automatic Language Detection via Accept-Language Header**
  - **Given** A client request does not supply a `lang` query parameter
  - **Given** The HTTP request contains header `Accept-Language: fr-FR,fr;q=0.9,en;q=0.8`
  - **When** The client sends a GET request to `/hello?name=Dupont&salutation=Madame`
  - **Then** The service detects French (`fr`) from the Accept-Language header
  - **Then** The response status code is 200 OK
  - **Then** The message contains the appropriate French time-aware greeting (e.g., `Bonjour, Madame Dupont!`)

- **AC4: Fallback Behavior for Unsupported Language Request**
  - **Given** An unsupported language code `it` is requested via query parameter or header
  - **When** A client sends a GET request to `/hello?name=Mario&lang=it`
  - **Then** The response status code is 200 OK
  - **Then** The service gracefully falls back to English (`en`)
  - **Then** The message is rendered in English (e.g., `Good morning, Mario!`)
  - **Then** An informational response header `X-Supported-Languages: en, es, fr, de, sv` is returned

- **AC5: Path Variable Endpoint with Time-Aware Greeting**
  - **Given** A valid path variable name `Bob`
  - **When** A client sends a GET request to `/hello/Bob` with `Accept-Language: de`
  - **Then** The response status code is 200 OK
  - **Then** The recipient is `Bob`
  - **Then** The message contains the German time-aware greeting (e.g., `Guten Morgen, Bob!` / `Guten Tag, Bob!` / `Guten Abend, Bob!`)

## 4. Technical Constraints & Out of Scope

- **Constraints:**
  - Maintain immutable payload structure: `Greeting(String message, String recipient)`.
  - Codebase package lock: All classes must reside under `com.nordea.demo.helloworld`.
  - Technology stack: Java 17/21 LTS, Spring Boot 3.x, Apache Maven.
  - Performance SLA: Response latency p99 < 50ms under 500 RPS nominal load (< 10ms local unit test latency).
  - Security & Logging: Compliance with FIN-GOV-GUARD-001 (PII masking in log lines, TLS 1.3 in transit).
  - Supported languages: `en`, `es`, `fr`, `de`, `sv`.
- **Out of Scope:**
  - Database persistence or caching layer (Redis).
  - OAuth2 / FAPI token authentication filters inside application container (managed upstream at API gateway).
  - UI / frontend components.

## 5. Design & UI/UX (If applicable)

- N/A - Backend only

## 6. Definition of Done (DoD)

- [ ] Code is peer-reviewed and approved.
- [ ] Unit and integration tests are written using JUnit 5 & RestTestClient and passing (>80% branch coverage).
- [ ] All Acceptance Criteria (AC1 - AC5) are successfully verified.
- [ ] Backward compatibility verified for legacy routes (`GET /`, `GET /hello`, `GET /hello/{name}`).
- [ ] Relevant documentation (OpenAPI / Swagger specs) updated.
- [ ] SAST / DAST scans pass with zero Critical/High CVEs.

## 7. Open Questions & Clarifications Needed

- [ ] **Q1:** What exact time zone should drive time-of-day greeting partitions (UTC server default vs client-provided `Time-Zone` header)?
- [ ] **Q2:** How should usage metrics for localization demand (e.g. French vs Spanish usage counters) be published (Micrometer Actuator metrics vs structured application logs)?

## 8. Agent Assumptions Made

- **Assumption 1:** Time partition defaults to UTC/Server time (Morning: 05:00-11:59, Afternoon: 12:00-17:59, Evening: 18:00-04:59) unless a timezone header is agreed upon.
- **Assumption 2:** Micrometer `MeterRegistry` counters tagged with `lang` will be used for localization tracking metrics.
- **Assumption 3:** Legacy responses without query parameters remain byte-compatible with the existing `Greeting` record structure.

## 9. Revision Changelog

- v1.0: Initial PR creation for review.
