# Cloud-Synced Mobile Todo Application

* **Author:** design-agent
* **Status:** Draft
* **Date:** 2025-05-18

---

## Overview

The Cloud-Synced Mobile Todo Application provides a friction-free, cross-platform productivity tool for iOS and Android. By prioritizing immediate utility through anonymous guest sessions, users can instantly capture tasks, decompose them into actionable subtasks, set granular priorities, and schedule precision deadline reminders without undergoing an upfront registration process. Data is automatically synchronized to Google Cloud Firestore via a Go backend hosted on Google Cloud Run, with the flexibility to link permanent credentials at any point for multi-device access.

## The Problem

Most modern productivity and task management applications present an immediate barrier to entry: mandatory registration walls requiring email verification or third-party sign-ins before a user can record their first task. This upfront friction leads to significant drop-off rates during initial onboarding.

Conversely, simple local-only todo applications avoid registration barriers but suffer from critical shortcomings: tasks are bound to a single device, leaving users vulnerable to catastrophic data loss upon device damage or deletion, and precluding cross-device synchronization. Furthermore, existing solutions often lack intuitive subtask breakdown or flexible deadline reminder scheduling (e.g., reminding users at custom offsets prior to a deadline), forcing users into rigid all-or-nothing notification patterns.

There is a clear need for an anonymous-first, cloud-synchronized task management system that delivers instantaneous utility, hierarchical subtask organization, and dependable, customizable push notifications without forcing account creation upfront.

## Goals

* **Instantaneous Guest Onboarding**: Enable immediate task and subtask creation upon initial launch without presenting account creation or sign-in prompts.
* **Hierarchical Task Organization**: Support task titles, rich descriptions, priority classifications (Low, Medium, High), and embedded subtask checklists with independent completion toggling.
* **Customizable Deadline Push Reminders**: Allow users to specify deadline dates/times alongside relative reminder offsets (e.g., at deadline, 15m before, 1h before, 1d before, or custom duration), delivering reliable notifications to iOS and Android devices via Google Cloud Tasks, Firebase Cloud Messaging (FCM), and Apple Push Notification service (APNs).
* **Comprehensive Task Lifecycle**: Provide simple state transitions to complete, archive, unarchive, or permanently delete tasks and subtasks.
* **Frictionless Account Linking**: Allow seamless linking of anonymous credentials with permanent identity providers (Google, Apple, Email) to enable cross-device synchronization and permanent data retention without disrupting existing tasks.
* **Standard Infrastructure Alignment**: Utilize Flutter for mobile clients, Go (Echo) for the backend REST service, Google Cloud Run for containerized serverless compute, and Google Cloud Firestore for persistence.

## Non-Goals

* **Bidirectional Offline Sync Engine**: Offline conflict resolution, CRDTs (Conflict-free Replicated Data Types), or distributed local-to-cloud synchronization are out of scope for the MVP. Mutations require active network connectivity (online-only write model), with local caching deferred to Phase 2.
* **Multi-User Collaboration**: Shared lists, task assignments, activity streams, and multi-user workspace access are excluded from this release.
* **Complex Recurring Task Engine**: Advanced recurrence rules (e.g., RRULE recurrence patterns, bi-weekly schedules) are deferred to future milestones.
* **Desktop or Web Client Support**: The client surface is limited strictly to mobile platforms (iOS and Android).

## Critical User Journeys (CUJs)

```yaml
- user: Mobile Guest User
  goals:
  - goal: Capture a complex task with subtasks and a reminder without signing up
    tasks:
    - task: Launch application and establish anonymous session
      scenario:
        given: App is freshly installed on an iOS or Android device with network connectivity.
        when: User opens the application for the first time.
        then: An anonymous Firebase Auth session is provisioned silently and saved in the OS Keychain/Keystore; user is placed directly on the main task list without an onboarding gate.
    - task: Create a prioritized task with subtasks and custom reminder offset
      scenario:
        given: User is on the active task list screen.
        when: User enters task title, description, sets priority to "High", defines a deadline 24 hours out with a "1 hour before" reminder offset, adds two subtask checklist items, and submits.
        then: Task and embedded subtasks are persisted to Firestore, a scheduled Google Cloud Task is enqueued for 23 hours from now, and the task renders immediately in the user's active list.
- user: Scheduled Task Notification Recipient
  goals:
  - goal: Receive timely reminder and review task details
    tasks:
    - task: Receive push notification at scheduled reminder offset
      scenario:
        given: A pending task with a scheduled reminder offset exists and remains active/incomplete.
        when: The scheduled Google Cloud Task executes at the target reminder timestamp.
        then: Backend verifies task validity and dispatches a push notification via FCM/APNs to user's registered device tokens.
    - task: Open task directly from push notification
      scenario:
        given: Push notification is delivered to the user device lock screen or notification tray.
        when: User taps the push notification.
        then: Application opens and navigates directly to the specific task detail view displaying parent task metadata and subtask checklist.
- user: Active Task Manager
  goals:
  - goal: Track subtask progress and archive completed tasks
    tasks:
    - task: Update subtask completion status
      scenario:
        given: User is viewing a task containing unfinished subtasks.
        when: User taps the checkbox next to a subtask item.
        then: Subtask status toggles to completed, updating Firestore atomically and reflecting progress immediately on the UI.
    - task: Archive completed parent task
      scenario:
        given: User has finished all subtasks or marked the parent task complete.
        when: User taps the archive action.
        then: Task status transitions to "archived", task disappears from the active view into the Archive tab, and any unexecuted scheduled reminder Cloud Task is effectively invalidated.
- user: Returning Guest User
  goals:
  - goal: Secure tasks and sync across devices via account linking
    tasks:
    - task: Link anonymous account to a permanent identity provider
      scenario:
        given: User has accumulated tasks under an anonymous session.
        when: User navigates to Settings and authenticates via Apple Sign-In or Google Sign-In.
        then: Anonymous Firebase Auth UID is upgraded and bound to the permanent provider credentials, retaining all existing Firestore data under the same UID.
    - task: Access synchronized tasks on a secondary device
      scenario:
        given: User account has been linked to a permanent provider.
        when: User installs the application on a second mobile device and signs in with the linked provider.
        then: All tasks, subtasks, priorities, and deadlines are retrieved from Firestore and displayed identically across both devices.
```

## Technical Plan (Architecture)

### System Architecture Overview

The system follows a cloud-native, microservices-ready architecture using Google Cloud standard building blocks. The Flutter client interacts with a Go (Echo) REST API hosted on Google Cloud Run over HTTPS. Google Cloud Firestore provides scalable NoSQL document persistence. Push reminder execution is driven asynchronously via Google Cloud Tasks scheduled queues, which invoke internal dispatch webhooks on the Cloud Run service to deliver push messages through Firebase Cloud Messaging (FCM) and the Apple Push Notification service (APNs).

```
+-----------------------------------------------------------------------------------+
|                            Mobile Client (Flutter)                                |
|  - iOS (APNs) & Android (FCM) Targets                                             |
|  - Firebase Auth SDK: Anonymous Session & Federated Account Linking               |
|  - Flutter Secure Storage: Key material & Token persistence                       |
|  - Push Notifications: firebase_messaging background/foreground handlers          |
+-----------------------------------------+-----------------------------------------+
                                          | HTTPS / REST (Firebase JWT Bearer)
                                          v
+-----------------------------------------------------------------------------------+
|                        Go Echo Service (Google Cloud Run)                         |
|  +-----------------------------------------------------------------------------+  |
|  | Auth Middleware: Firebase ID Token Verification & User Context Extraction   |  |
|  +-----------------------------------------------------------------------------+  |
|  | REST Routing Layer:                                                         |  |
|  |   - /api/v1/tasks             (CRUD, subtask toggling, archive/delete)      |  |
|  |   - /api/v1/devices/token     (Register/Refresh FCM device push tokens)     |  |
|  |   - /internal/v1/dispatch     (Secured by Google OIDC service-to-service)   |  |
|  +-----------------------------------------------------------------------------+  |
|  | Business Services: TaskManager, NotificationScheduler, PushSender           |  |
|  +-----------------------------------------------------------------------------+  |
+--------------------+---------------------------------------+----------------------+
                     |                                       |
                     v                                       v
    +---------------------------------+    +----------------------------------+
    |     Google Cloud Firestore      |    |        Google Cloud Tasks        |
    |  - users/{userId}/tasks/{taskId}|    |  - Scheduled reminder queue      |
    |  - users/{userId}/devices/{tok} |    |  - Target: /internal/v1/dispatch |
    +---------------------------------+    +-----------------+----------------+
                                                             | At reminder execution time
                                                             v
                                           +----------------------------------+
                                           | Push Dispatch Webhook Handler    |
                                           | (Cloud Run -> FCM / APNs Client) |
                                           +-----------------+----------------+
                                                             | Push Payload
                                                             v
                                                   [ User Mobile Device ]
```

### Component Details & Interactions

#### 1. Client Layer (Flutter Mobile App)
* **Auth Management**: Initializes anonymous authentication via `FirebaseAuth.instance.signInAnonymously()` on first launch. If account linking is triggered later, it invokes `linkWithCredential()` (Apple or Google auth), preserving the original Firebase UID.
* **Device Token Registration**: Obtains the FCM registration token via `FirebaseMessaging.instance.getToken()` and registers it with the backend at `POST /api/v1/devices/token`.
* **State Management & Networking**: Encapsulates network communication via an HTTP client that automatically attaches the user's current Firebase ID token in the `Authorization: Bearer <token>` header.

#### 2. Backend Compute (Go / Echo on Google Cloud Run)
* **Runtime**: Go binary running in a lightweight container on Cloud Run with scale-to-zero enabled.
* **Authentication Middleware**: Validates incoming Firebase JWTs using the Google Auth / Firebase Admin SDK, populating the Echo request context with the verified `userId`.
* **Internal Webhook Security**: The `/internal/v1/dispatch` endpoint is restricted to calls originating from Google Cloud Tasks by verifying Google-signed OIDC ID tokens matching the configured service account.

#### 3. Push Notification Scheduling & Delivery Flow
* **Schedule Calculation**:
  When a task is created or updated with a deadline $T_{\text{deadline}}$ and a relative reminder offset $\Delta t_{\text{offset}}$ (in seconds before deadline), the backend computes:
  $$T_{\text{reminder}} = T_{\text{deadline}} - \Delta t_{\text{offset}}$$
  If $T_{\text{reminder}} > T_{\text{now}}$, a Google Cloud Task is scheduled with `schedule_time = Timestamp(T_reminder)`.
* **Version-Based Invalidation Strategy**:
  Rather than calling the Cloud Tasks API to locate and delete previously scheduled tasks when deadlines are edited or tasks are archived/completed, the backend uses a version token (`version` integer incremented on task modification).
  The Cloud Task payload contains `{"userId": "...", "taskId": "...", "version": N}`.
  When the dispatch webhook fires:
  1. The backend reads `users/{userId}/tasks/{taskId}`.
  2. If the task does not exist, is marked completed (`isCompleted == true`), is archived (`status == "ARCHIVED"`), or if `task.version != payload.version`, the dispatch request is safely discarded (no-op 200 OK).
  3. If valid, the backend retrieves all active device tokens for `userId` from `users/{userId}/devices` and dispatches the notification via the Firebase Admin SDK.

### Data Model & Firestore Schema

#### Tasks Collection: `users/{userId}/tasks/{taskId}`
Each parent task document encapsulates its metadata, deadline, reminder configuration, and embedded subtask array.

```json
{
  "id": "c1f7a90e-b7f3-4f93-87a2-f8231bbd01a4",
  "userId": "firebase_uid_12345",
  "title": "Prepare Quarterly Review Presentation",
  "description": "Consolidate Q1 operational metrics and financial summaries",
  "priority": "HIGH",
  "status": "ACTIVE",
  "isCompleted": false,
  "deadline": "2025-06-01T15:00:00Z",
  "reminderOffsetSeconds": 3600,
  "reminderExecutionTime": "2025-06-01T14:00:00Z",
  "version": 1,
  "subtasks": [
    {
      "id": "s-01",
      "title": "Export revenue report from billing system",
      "isCompleted": true,
      "order": 1
    },
    {
      "id": "s-02",
      "title": "Draft executive summary slide",
      "isCompleted": false,
      "order": 2
    }
  ],
  "createdAt": "2025-05-18T10:00:00Z",
  "updatedAt": "2025-05-18T10:00:00Z"
}
```

* **Data Sizing & Limits**: The embedded `subtasks` array is capped at 10 items per task for the MVP. At ~100 bytes per subtask, the array consumes under 1.5 KB, well below Firestore's 1 MB document threshold, avoiding multi-document read overhead while keeping the UI focused.

#### Device Tokens Collection: `users/{userId}/devices/{deviceToken}`

```json
{
  "token": "fcm_token_string_here",
  "platform": "ios",
  "updatedAt": "2025-05-18T10:00:00Z"
}
```

### API Specification

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/tasks` | `POST` | User Bearer | Create a new task with optional subtasks and reminder configuration. |
| `/api/v1/tasks` | `GET` | User Bearer | List tasks for the authenticated user; query params: `status` (`ACTIVE`, `ARCHIVED`), `limit`, `pageToken`. |
| `/api/v1/tasks/:id` | `GET` | User Bearer | Retrieve a single task by ID. |
| `/api/v1/tasks/:id` | `PUT` | User Bearer | Update task details, subtasks list, and reschedule reminder if modified. |
| `/api/v1/tasks/:id/complete` | `PATCH` | User Bearer | Toggle completion state of task. Increments task `version`. |
| `/api/v1/tasks/:id/archive` | `PATCH` | User Bearer | Transition task status to `ARCHIVED`. Increments task `version`. |
| `/api/v1/tasks/:id/unarchive` | `PATCH` | User Bearer | Restore task status from `ARCHIVED` to `ACTIVE`. |
| `/api/v1/tasks/:id` | `DELETE` | User Bearer | Permanently remove task document from Firestore. |
| `/api/v1/devices/token` | `POST` | User Bearer | Register or refresh client FCM device token. |
| `/internal/v1/dispatch` | `POST` | Cloud Tasks OIDC | Internal dispatch webhook called by Cloud Tasks to validate task version and trigger FCM push notification. |

## Alternatives Considered

### Alternative A: Subtasks as Separate Subcollections (`users/{userId}/tasks/{taskId}/subtasks/{subtaskId}`)

* **Pros**:
  * Unbounded subtask capacity per task without approaching Firestore document size limitations.
  * Allows fine-grained Firestore security rules and individual subtask real-time listeners.
* **Cons**:
  * Requires N+1 document reads or collection queries to render a single task detail view, increasing read latency and billing costs.
  * Creating a task with subtasks requires Firestore batch writes or multi-document transactions.
* **Reason for Rejection**:
  Personal todo subtasks are naturally bounded checklists (capped at 10 items for MVP). Embedding subtasks directly into the parent task document guarantees single-roundtrip reads and atomic mutations while keeping resource usage well within limits.

### Alternative B: Cron Polling via Cloud Scheduler vs. Point-in-Time Cloud Tasks

* **Pros**:
  * Avoids managing individual task queue records; a single recurring job queries upcoming deadlines periodically.
* **Cons**:
  * High query overhead and cost: the backend would need to scan all pending tasks across all users every 1 to 5 minutes.
  * Notification drift and jitter: tasks scheduled between cron polling intervals could be notified minutes late.
  * Idle resource waste when few or no reminders are due.
* **Reason for Rejection**:
  Google Cloud Tasks provides native millisecond-precision scheduled delivery, executing only when a reminder is actually due. This completely eliminates empty polling scans and ensures timely notification arrival.

### Alternative C: Pure Client-Side Local Notifications

* **Pros**:
  * Works offline without requiring backend or cloud messaging infrastructure.
  * Zero cloud messaging egress costs.
* **Cons**:
  * OS limitations: Android Doze and iOS background execution restrictions frequently delay or suppress local alarm notifications.
  * Multi-device synchronization failure: Reminders created on one device would not trigger on another linked device.
  * Vulnerable to local app cache clearing or OS-level process management.
* **Reason for Rejection**:
  Server-coordinated push notifications via FCM and APNs ensure reliable multi-device delivery and consistent notification reception regardless of whether the mobile client process is active in memory.

## Non-Functional Requirements related to a critical risk

### Security & Privacy
* **Tenant Isolation**: All task document operations enforce strict user isolation: Firestore queries and mutations require the authenticated UID extracted from the validated Firebase ID token to match `userId` in the document path (`users/{userId}/tasks/{taskId}`).
* **Service-to-Service Dispatch Authentication**: The internal reminder webhook (`/internal/v1/dispatch`) accepts requests only from Google Cloud Tasks by verifying the Google-issued OIDC identity token and matching the expected service account email.
* **Key & Token Storage**: Mobile devices persist Firebase Auth refresh tokens and FCM tokens securely in iOS Keychain and Android Keystore via `flutter_secure_storage`.

### Performance & Latency
* **Scale-to-Zero and Latency**: The Go backend compiled binary has minimal memory footprint (<30 MB) and cold starts under 1 second on Cloud Run, ensuring sub-200ms API response times for standard CRUD operations.
* **Firestore Read Optimization**: By storing subtasks within the parent task document, fetching tasks and their checklists always requires a single Firestore read per parent task.
