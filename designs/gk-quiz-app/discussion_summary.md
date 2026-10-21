# Discussion Summary: GK Quiz Mobile Application MVP

## 1. Executive Summary & Objective
A lightweight, solo General Knowledge (GK) mobile quiz application offering 2–3 curated quiz packs for its initial MVP. The goal is to provide a frictionless trivia experience with instant onboarding (no sign-up wall) while preventing client-side score manipulation through server-evaluated sessions.

---

## 2. Goals & Non-Goals

### Goals
- **Frictionless Play**: Enable immediate quiz access without mandatory user registration or authentication.
- **Dynamic Content**: Deliver 2–3 quiz packs dynamically via backend API so questions can be updated or expanded without new mobile app releases.
- **Customizable Timer**: Allow users to manually configure their quiz session timer pace (e.g., 60s, 120s, or 180s) prior to starting a pack.
- **Tamper-Resistant Scoring**: Server-side answer evaluation using stateless HMAC session tokens to ensure questions cannot be inspected in advance and completion times are strictly verified.
- **Lean MVP Architecture**: Rapid delivery within a 2–3 week timeline on low/zero-cost infrastructure using Cloud Run Functions / Cloud Run and Firestore.

### Non-Goals
- Multiplayer, live matchmaking, or head-to-head battles (deferred to post-MVP).
- User profile persistence, social logins, or cloud-synced user histories.
- In-app purchases, paywalls, or monetization ad-networks for MVP.
- Offline-only full quiz caching (network connectivity is assumed during quiz start and submission).

---

## 3. Critical User Journeys (CUJs)
1. **Browse Quiz Packs**: User launches the app, sees available GK quiz packs (e.g., "World Geography", "Science & Nature", "History & Culture") with metadata.
2. **Configure Timer & Start Quiz**: User selects a pack and chooses their desired timer duration (e.g., 60s fast challenge, 120s standard, or custom bounds). The mobile app requests a session from the backend passing the chosen duration. The backend returns questions (without answers) and an HMAC session token encoding `pack_id`, `started_at`, and the agreed `duration_seconds`.
3. **Play & Complete**: The user answers questions against their selected countdown timer. Upon completion, the app posts the submitted answers and the session token to the backend.
4. **View Results & Review**: The backend verifies token authenticity and elapsed time against the agreed duration, calculates the score, and returns the final score breakdown with correct answer explanations.

---

## 4. High-Level Architecture & Technical Plan

### Plain-Language Concept: What is an HMAC Token? (Business / Non-Technical Explanation)
Think of an HMAC token like a **tamper-evident digital wristband or sealed entry ticket**:
- When a user starts a quiz, the server stamps the start time and the agreed countdown duration onto a digital ticket with an invisible, unforgeable wax seal (`HMAC`).
- The player holds this ticket on their phone while answering questions.
- When they finish and submit their answers, the server inspects the ticket. If the seal has been tampered with or if the player took longer than the agreed time, the submission is rejected.
- This gives us complete anti-cheat protection without needing expensive databases or forcing users to create an account.

### Components
- **Mobile Frontend (Flutter)**:
  - Clean cross-platform UI for iOS and Android.
  - Timer duration selection picker on the pack start screen.
  - State management for active quiz countdown, question progression, and submission payloads.
- **Backend API (Python / FastAPI or Cloud Run Functions)**:
  - RESTful endpoints (`GET /packs`, `POST /packs/{id}/start`, `POST /packs/{id}/submit`).
  - Deployable as a Cloud Run Function (Cloud Run 2nd Gen) or Cloud Run container service, providing scale-to-zero serverless execution with minimal operational complexity.
  - Cryptographic session manager: Issues and verifies HMAC-SHA256 signed session tokens encoding `session_id`, `pack_id`, `started_at`, and `duration_seconds`.
  - Scoring engine: Validates answers against stored master answer keys.
- **Storage / Hosting**:
  - Backend deployed on **Cloud Run / Cloud Run Functions** (Python).
  - Quiz pack data stored in **Firestore** to facilitate low-friction editing.

### Zoom Out Standard Self-Evaluation
- **Simplicity & YAGNI**: Stateless HMAC tokens eliminate session database management and user account tables.
- **Standard & Tech Fit**: Serverless Python (FastAPI / Cloud Run Functions) satisfies rapid iteration and free-tier cost targets while providing scale-to-zero operational efficiency.
- **Anti-Weeds**: Implementation details remain high level, focusing on contract flows and data boundaries.

---

## 5. Risks & Mitigations
- **Token Tampering / Replay Attacks**: Mitigated by HMAC-SHA256 signing of start timestamps and configured duration. Backend validates `submission_time - start_time <= duration_seconds + grace_period`.
- **Manual Timer Abuse**: Enforce server-side clamping on user-selected durations (e.g., minimum 30s, maximum 300s) to prevent invalid timer values.
- **Network Glitch at Submission**: 15-second grace period allows client retry without failing the time check.
- **Cold Starts**: Scale-to-zero Cloud Run Functions may have a ~1s warm-up latency; kept minimal with lightweight Python dependencies.

---

## 6. Cost & Timeline
- **Cost**: $0 / month during MVP evaluation under Google Cloud Run / Functions and Firestore free-tier quotas.
- **Timeline**: 2–3 weeks total (Week 1: FastAPI / Functions endpoints & Firestore packs; Week 2: Flutter UI with manual timer picker & API integration; Week 3: Testing, polish, & validation).

---

## 7. Verification & Success Exams
- **Automated Tests**:
  - Flutter unit/widget tests for timer picker, countdown, option selection, and score displays.
  - Pytest suite covering token signing, user-configured duration clamping, tampering rejection, and scoring calculations.
- **Success Criteria**:
  - >70% quiz completion rate across the 2–3 initial packs.
  - Zero critical crashes in production MVP smoke tests.
