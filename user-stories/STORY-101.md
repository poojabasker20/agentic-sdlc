# Multi-Language and Time-Aware Personalized Greeting Service

**Issue Type:** User Story  
**Status:** Ready for Development  
**Priority:** High

## 1. Description

**As an** International Client Application or Portal Developer,  
**It is requested that** culturally aware, time-sensitive, and localized greeting responses be retrievable via REST endpoints with optional salutation, client time zone detection, and language selection,  
**So that** international customers across Nordic and European markets experience a personalized, polite, and natural first touchpoint without breaking legacy API integrations.

## 2. Business Context & Background

As part of regional expansion across Nordic territories (Sweden, Norway, Denmark, Finland, Iceland) and mainland Europe (Spain, France, Germany), client portals and partner applications require localized and time-aware greeting services. The baseline service returns static English greetings regardless of locale or client time zone. This user story enhances the core greeting service to support multi-language greetings across Nordic and continental European languages, time-of-day dynamic messaging (Morning, Afternoon, Evening) resolved against the client time zone header, formal salutations (e.g., Herr, Fru, Madame, Señor, Dr.), and automatic language negotiation (Accept-Language), while preserving full backward compatibility with legacy API contracts.

## 3. Acceptance Criteria

- **AC1: Backward Compatibility on Legacy Root and Default Hello Endpoints**
  - **Given** The Greeting API service is running
  - **When** A GET request is sent to `/` or `/hello` without language or salutation parameters
  - **Then** The response status code is 200 OK
  - **Then** The response payload matches the legacy contract: `{"message": "Hello, World!", "recipient": "World"}`

- **AC2: Localized Greeting with Explicit Language Parameter, Salutation, and Client Time Zone**
  - **Given** Supported language `es` (Spanish) and salutation `Señor` are specified
  - **Given** The client header `Time-Zone: Europe/Madrid` is supplied where local time is 09:30
  - **When** A GET request is sent to `/hello?name=Gomez&salutation=Señor&lang=es`
  - **Then** The response status code is 200 OK
  - **Then** The recipient field is formatted as `Señor Gomez`
  - **Then** The message contains the appropriate Spanish morning greeting (e.g., `¡Buenos días, Señor Gomez!`)

- **AC3: Nordic Locale Support and Automatic Language Negotiation via Accept-Language Header**
  - **Given** No `lang` query parameter is supplied in the request
  - **Given** The HTTP request contains the header `Accept-Language: sv-SE,sv;q=0.9,en;q=0.8`
  - **Given** The client header `Time-Zone: Europe/Stockholm` is provided where local time is 08:15
  - **When** A GET request is sent to `/hello?name=Lindqvist&salutation=Fru`
  - **Then** Swedish (`sv`) is negotiated from the Accept-Language header
  - **Then** The response status code is 200 OK
  - **Then** The recipient field is formatted as `Fru Lindqvist`
  - **Then** The message contains the Swedish time-aware greeting evaluated in the Europe/Stockholm time zone (e.g., `God morgon, Fru Lindqvist!`)

- **AC4: Fallback Behavior for Unsupported Language Request**
  - **Given** An unsupported language code `it` is requested via query parameter or header
  - **When** A GET request is sent to `/hello?name=Mario&lang=it`
  - **Then** The response status code is 200 OK
  - **Then** The service falls back gracefully to English (`en`)
  - **Then** The message is rendered in English (e.g., `Good morning, Mario!`)
  - **Then** An informational response header `X-Supported-Languages: en, sv, da, no, fi, is, es, fr, de` is returned

- **AC5: Path Variable Endpoint with Client Time-Aware Greeting**
  - **Given** A valid path variable name `Bob` is provided
  - **Given** The client header `Time-Zone: Europe/Berlin` is provided where local time is 14:00
  - **When** A GET request is sent to `/hello/Bob` with `Accept-Language: de`
  - **Then** The response status code is 200 OK
  - **Then** The recipient is `Bob`
  - **Then** The message contains the German afternoon greeting based on Berlin local time (e.g., `Guten Tag, Bob!`)

## 4. Technical Constraints & Out of Scope

- **Constraints:**
  - Maintain immutable payload structure: `Greeting(String message, String recipient)`.
  - Codebase package lock: All classes must reside under `com.nordea.demo.helloworld`.
  - Technology stack: Java 17/21 LTS, Spring Boot 3.x, Apache Maven.
  - Time Zone Resolution: Client time-of-day evaluation must derive from the `Time-Zone` HTTP header (IANA time zone identifier, e.g., `Europe/Stockholm`), falling back to UTC if omitted or invalid.
  - Observability & Telemetry: Localization demand and request metrics must be emitted using structured application logs in JSON format in compliance with FIN-GOV-GUARD-001 audit standards.
  - Performance SLA: Response latency p99 < 50ms under 500 RPS nominal load (< 10ms local unit test latency).
  - Security & Logging: Compliance with FIN-GOV-GUARD-001 (PII masking in log lines, TLS 1.3 in transit).
  - Supported languages: `en`, `sv`, `da`, `no`, `fi`, `is`, `es`, `fr`, `de`.
- **Out of Scope:**
  - Database persistence or caching layer (Redis).
  - OAuth2 / FAPI token authentication filters inside application container (managed upstream at API gateway).
  - UI / frontend components.
  - UK-specific localization profiles (focused strictly on Nordic and continental European coverage).

## 5. Design & UI/UX (If applicable)

- N/A - Backend only

## 6. Definition of Done (DoD)

- [ ] Code is peer-reviewed and approved.
- [ ] Unit and integration tests are written using JUnit 5 & RestTestClient and passing (>80% branch coverage).
- [ ] All Acceptance Criteria (AC1 - AC5) are successfully verified.
- [ ] Time-of-day resolution correctly computes greeting partition from the client `Time-Zone` header with UTC fallback.
- [ ] Structured application logs are implemented for localization and telemetry tracking.
- [ ] Backward compatibility verified for legacy routes (`GET /`, `GET /hello`, `GET /hello/{name}`).
- [ ] Relevant documentation (OpenAPI / Swagger specs) updated.
- [ ] SAST / DAST scans pass with zero Critical/High CVEs.

## 7. Open Questions & Clarifications Needed

_All prior open questions have been clarified by reviewer feedback on PR #3._

## 8. Agent Assumptions Made

- **Assumption 1:** Time partition logic evaluates local client time: Morning (05:00-11:59), Afternoon (12:00-17:59), Evening (18:00-04:59).
- **Assumption 2:** Invalid or missing `Time-Zone` header values fall back safely to UTC without throwing client 4xx errors.
- **Assumption 3:** Legacy responses without query parameters remain byte-compatible with the existing `Greeting` record structure.

## 9. Revision Changelog

- v1.0: Initial PR creation for review.
- v1.1: Addressed PR #3 review feedback: removed first-person pronouns in favor of passive/objective voice; incorporated all Nordic countries (Sweden, Norway, Denmark, Finland, Iceland) and removed UK scope; resolved Q1 by sourcing client time from the Time-Zone header; resolved Q2 by adopting structured JSON application logging for localization metrics.