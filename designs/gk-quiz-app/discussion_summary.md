# Discussion Summary: GK Quiz Mobile Application MVP

## 1. Executive Summary & Objective
A lightweight, solo General Knowledge (GK) mobile quiz application offering 2–3 curated quiz packs for its initial MVP. The goal is to provide a frictionless trivia experience with instant onboarding (no sign-up wall) while preventing client-side score manipulation through server-evaluated sessions.

---

## 2. Goals & Non-Goals

### Goals
- **Frictionless Play**: Enable immediate quiz access without mandatory user registration or authentication.
- **Dynamic Content**: Deliver 2–3 quiz packs dynamically via backend API so questions can be updated or expanded without new mobile app releases.
- **Tamper-Resistant Scoring**: Server-side answer evaluation using stateless HMAC session tokens to ensure questions cannot be inspected in advance and completion times are verified.
- **Lean MVP Architecture**: Rapid delivery within a 2–3 week timeline on low/zero-cost infrastructure.

### Non-Goals
- Multiplayer, live matchmaking, or head-to-head battles (deferred to post-MVP).
- User profile persistence, social logins, or cloud-synced user histories.
- In-app purchases, paywalls, or monetization ad-networks for MVP.
- Offline-only full quiz caching (network connectivity is assumed during quiz start and submission).

---

## 3. Critical User Journeys (CUJs)
1. **Browse Quiz Packs**: User launches the app, sees available GK quiz packs (e.g., "World Geography", "Science & Nature", "History & Culture") with metadata (number of questions, time limit).
2. **Start Quiz Session**: User selects a pack. The Flutter app requests a session from the backend. The backend returns the list of questions (without answers) and a signed HMAC session token containing `pack_id`, question IDs, and `start_time`.
3. **Play & Complete**: The user answers questions against a local countdown timer. Upon completion, the app posts the submitted answers and the session token to the backend.
4. **View Results & Review**: The backend verifies token authenticity and elapsed time, calculates the score, and returns the final score breakdown with correct answer explanations.

---

## 4. High-Level Architecture & Technical Plan

### Components
- **Mobile Frontend (Flutter)**:
  - Clean cross-platform UI for iOS and Android.
  - State management for active quiz countdown, question progression, and submission payloads.
- **Backend API (Python / FastAPI)**:
  - RESTful endpoints (`GET /packs`, `POST /packs/{id}/start`, `POST /packs/{id}/submit`).
  - Cryptographic session manager: Issues and verifies HMAC-SHA256 signed session tokens encoding `session_id`, `pack_id`, and `started_at` timestamp.
  - Scoring engine: Validates answers against stored master answer keys.
- **Storage / Hosting**:
  - Backend deployed on **Cloud Run** (containerized Python/FastAPI).
  - Quiz pack data stored in **Firestore** (or structured JSON storage) to facilitate low-friction editing.

### Zoom Out Standard Self-Evaluation
- **Simplicity & YAGNI**: Avoided database-backed user identity tables and complex session databases; using stateless HMAC tokens eliminates session state synchronization overhead.
- **Corporate Standard Deviations**: Corporate preference typically defaults to Go (Echo); Python (FastAPI) was chosen per explicit user requirement. FastAPI provides strong typing with Pydantic and async performance, which fits Cloud Run execution well.
- **Anti-Weeds**: Implementation details (e.g., local state management libraries, styling widgets) are kept out of this high-level summary and deferred to the drafting phase.

---

## 5. Risks & Mitigations
- **Token Tampering / Replay Attacks**: Mitigated by HMAC-SHA256 signing of start timestamps and pack metadata. Backend checks that `submission_time - start_time <= allowed_pack_duration + grace_period` and rejects expired sessions.
- **Network Glitch at Submission**: If submission fails due to transient connection drop, the Flutter client can retry within the grace period window.
- **Cold Starts**: Python on Cloud Run can encounter slight cold starts (~1-2s); minimized using lightweight dependencies and minimum memory footprint.

---

## 6. Cost & Timeline
- **Cost**: $0 / month during MVP evaluation under Google Cloud Run and Firestore free-tier quotas.
- **Timeline**: 2–3 weeks total (Week 1: FastAPI endpoints & Firestore packs; Week 2: Flutter UI, quiz flow, & API integration; Week 3: Testing, polish, & validation).

---

## 7. Verification & Success Exams
- **Automated Tests**:
  - Flutter unit/widget tests for quiz timers, option selection, and score display screens.
  - Pytest suite covering token signing, tampering rejection, expired submission rejection, and edge-case scoring calculations.
- **Success Criteria**:
  - >70% quiz completion rate across the 2–3 initial packs.
  - Zero critical crashes in production MVP smoke tests.
