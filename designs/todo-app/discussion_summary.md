# Discussion Summary: Todo Application

## 1. Overview & Objective
Build a cloud-backed, multi-user Todo application from scratch that ensures users never miss deadlines by combining clear priority ranking with proactive dual-channel notifications (in-app feed and email).

## 2. Goals & Non-Goals
### Goals
- Full task lifecycle management (create, read, update, delete, complete) with description, priority (`Low`, `Medium`, `High`), and UTC deadlines.
- Timely scheduled alerts: 24 hours before deadline, 1 hour before deadline, and immediate overdue notification.
- In-app notification center for pending/delivered alerts and transactional email dispatch.
- Resilient notification worker utilizing database-level concurrency locking and deduplication.
- Responsive multi-platform client interface across mobile and web.

### Non-Goals (YAGNI / Phase 1)
- Collaborative multi-user shared task lists or team workspaces.
- Recurring tasks or complex calendar sync integrations (e.g., Google Calendar / Outlook).
- Webhook integrations or custom user-defined notification channels (SMS, Slack).

## 3. Critical User Journeys (CUJs)
1. **CUJ-1: Task Creation with Priority and Deadline**: User creates a task with a description, sets priority to `High`, and selects a deadline. The system stores the task in UTC and schedules the alert windows.
2. **CUJ-2: Proactive Notification Delivery**: As the deadline approaches (T-24h, T-1h), the periodic background worker identifies the task, creates an in-app notification record, and sends an email reminder to the user.
3. **CUJ-3: Task Completion & Invalidation**: User completes the task ahead of the deadline. The system transitions the task status to `Completed` and immediately suppresses any pending notifications.
4. **CUJ-4: Overdue Alert Handling**: A task passes its deadline while still `Pending`. The system marks the task as overdue and triggers an immediate overdue alert to the user.

## 4. Architecture Outline
- **Client**: Flutter cross-platform client (Web, iOS, Android) handling local timezone presentation and task interaction.
- **Backend Service**: Go (Echo framework) REST API hosted on Google Cloud Run.
- **Data Persistence**: Cloud SQL (PostgreSQL) storing `users`, `tasks`, and `notifications`.
- **Notification Engine**: Cloud Scheduler triggering a Cloud Run cron endpoint every 5 minutes:
  - Queries upcoming and overdue alerts with `SELECT ... FOR UPDATE SKIP LOCKED`.
  - Dedupes via unique index `(task_id, alert_type)` in the `notifications` table to guarantee idempotency.
  - Sends email via transactional provider (SendGrid/Mailgun) with exponential backoff retries.

## 5. Grilling Analysis (The 8 Pillars)
* **Objective**: A dependable, distraction-free task tracker that ensures high-priority deadlines are met via automated alerting.
* **Limits Today**: Ad-hoc to-do apps either lack proactive lead-time alerts or create alert fatigue by spamming notifications without priority differentiation.
* **New Approach**: Standardized priority tiers paired with predictable lead-time triggers (24h/1h/overdue) and idempotent dual-channel dispatch.
* **Impact**: Eliminates missed deadlines and gives users peace of mind without requiring active app monitoring.
* **Risks & Mitigations**:
  * *Concurrency / Double-Sends*: Mitigated by DB-level row locking (`SKIP LOCKED`) and unique compound keys on notifications.
  * *Email Outages*: Third-party email failures are isolated and do not block task CRUD or in-app notification creation.
  * *Timezone Discrepancies*: Enforce strict UTC storage in the database with client-side localization.
* **Cost**: Minimal / GCP free tier eligible (Cloud Run scale-to-zero, low-tier Cloud SQL instance, standard email free tier).
* **Timeline**: ~2–3 weeks for full MVP (Go backend API, migrations, scheduler job, and Flutter client).
* **Verification**: Time-mocked integration tests verifying notification triggering, idempotency, and cancellation, alongside CI unit tests.
