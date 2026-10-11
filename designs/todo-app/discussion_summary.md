# Discussion Summary: Cloud-Synced Mobile Todo Application

## 1. Objective & Problem Statement
Build a lightweight, cross-platform mobile Todo application for iOS and Android that minimizes onboarding friction by supporting anonymous guest sessions while providing real-time cloud synchronization, task prioritization, deadline reminders, and task lifecycle management (active, archive, delete).

## 2. Goals & Non-Goals

### Goals
- **Instant Onboarding**: Allow users to immediately create and manage tasks via anonymous authentication without an upfront registration wall.
- **Task Management**: Support task heading (title), text description, deadline date/time, and priority levels (e.g., Low, Medium, High).
- **Lifecycle Management**: Enable users to mark tasks complete, archive completed/stale tasks, or delete them.
- **Deadline Notifications**: Reliably deliver push reminders to iOS and Android devices at the scheduled deadline time via Google Cloud Tasks and Firebase Cloud Messaging (FCM/APNs).
- **Account Linking**: Allow users to link their anonymous profile with an identity provider (Google, Apple, or Email) to secure tasks and sync across multiple devices.
- **Standard Platform Alignment**: Utilize Flutter for mobile clients and Go (Echo) on Cloud Run with Firestore.

### Non-Goals
- **Complex Offline Sync Engine**: Offline conflict resolution, CRDTs, or local-first distributed syncing are excluded for MVP. The app will operate in an online-only model for mutations.
- **Collaborative/Shared Lists**: Multi-user shared boards or assigned tasks are deferred to future iterations.
- **Recurring / Complex Task Rules**: Complex recurring task scheduling (e.g., RRULE recurrence engines) is out of scope for MVP.

## 3. Critical User Journeys (CUJs)
1. **CUJ 1: First-Time User Task Creation**
   - User opens the app for the first time.
   - App automatically retrieves/initializes an anonymous session via Firebase Auth, persisted in the secure Keychain/Keystore.
   - User enters a heading, description, selects High priority, sets a deadline for tomorrow at 10:00 AM, and saves.
   - Backend persists the task to Firestore and enqueues a Cloud Task scheduled for tomorrow at 10:00 AM.
2. **CUJ 2: Deadline Notification Delivery**
   - At the scheduled deadline, Cloud Tasks invokes the backend dispatch endpoint.
   - The backend validates the task status and version (ensures it was not completed, deleted, or rescheduled).
   - Backend sends an FCM/APNs push notification to the user's registered device tokens.
   - User taps the push notification and opens the specific task.
3. **CUJ 3: Archiving and Deletion**
   - User views their active task list, swipes or selects a finished task to "Archive".
   - Task transitions to the Archived tab; any pending deadline Cloud Tasks are marked obsolete.
   - User navigates to Archived tasks and permanently deletes items they no longer need.
4. **CUJ 4: Account Linking for Cross-Device Sync**
   - User sees a soft prompt or goes to Settings to "Link Account".
   - User authenticates via Apple Sign-In or Google Sign-In.
   - Anonymous credentials are linked to the permanent UID in Firebase Auth; existing Firestore tasks remain associated with the user UID.
   - User logs in on a second device and immediately sees their task list.

## 4. Current Limits & New Approach
- **Current Limits**: Most existing mobile task apps enforce mandatory account creation before first use, introducing steep drop-off rates. Conversely, lightweight offline-only apps lack cloud backup and cross-device push notifications.
- **New Approach**: Anonymous-first cloud architecture that bridges immediate task capture with seamless account upgrade, backed by scheduled Cloud Tasks for reliable, serverless push dispatch.

## 5. High-Level Architecture

```
+-------------------------------------------------------------+
|                 Mobile Client (Flutter)                     |
|  - iOS & Android Targets                                    |
|  - Firebase Auth SDK (Anonymous + Federated Linking)        |
|  - Firebase Messaging SDK (FCM / APNs)                      |
|  - Secure Storage (Keychain / Keystore token caching)       |
+------------------------------+------------------------------+
                               | HTTPS / REST
                               v
+-------------------------------------------------------------+
|                 Backend API (Go / Echo)                     |
|                   Hosted on Cloud Run                       |
|  - Auth Middleware (Verify Firebase ID Tokens)              |
|  - Task CRUD & Lifecycle Endpoints                          |
|  - Notification Scheduler (Cloud Tasks Client)              |
|  - Dispatch Webhook Handler (Internal task executor)        |
+--------------+-------------------------------+--------------+
               |                               |
               v                               v
    +--------------------+           +-------------------+
    |     Firestore      |           |    Cloud Tasks    |
    |  - Users Collection|           |  - Scheduled Task |
    |  - Tasks Collection|           |    Queue          |
    +--------------------+           +---------+---------+
                                               | Triggers at Deadline
                                               v
                                     +-------------------+
                                     |  Dispatch Handler |
                                     |  (FCM / APNs)     |
                                     +-------------------+
```

### Key Architectural Decisions
1. **Frontend**: Flutter cross-platform mobile client providing native look and feel on iOS and Android.
2. **Backend**: Go service running on Cloud Run, adhering to corporate platform standards.
3. **Storage**: Google Cloud Firestore for scalable, low-latency NoSQL document storage scoped under `users/{userId}/tasks/{taskId}`.
4. **Notification Dispatch**: Managed Google Cloud Tasks enqueued with `scheduleTime` matching task deadlines. Upon execution, the task targets an internal authenticated Go endpoint that sends push notifications via Firebase Admin SDK.
5. **Idempotency & Invalidation**: Tasks maintain a `version` or `deadlineUpdatedAt` timestamp. When the Cloud Task fires, the handler confirms that the task is still active and the deadline has not changed before sending the push.

## 6. Risks & Mitigations

| Risk | Severity | Mitigation |
| :--- | :--- | :--- |
| **Notification Failure on Offline Devices** | Medium | Because notifications are cloud-driven push notifications, a device without network connection at deadline time cannot receive the notification until reconnected. Noted as an accepted trade-off of the online-only model. |
| **Anonymous Account Data Loss** | Medium | If an anonymous user deletes the app or resets device storage before linking, data cannot be recovered. Mitigated by persisting tokens in the platform Keychain/Keystore and displaying non-intrusive linking banners. |
| **Task Rescheduling Churn** | Low | Updating deadlines frequently could result in orphaned Cloud Tasks. Mitigated via task versioning/timestamp checks at execution time, avoiding expensive cancellation API calls. |
| **Push Token Expiration** | Low | Flutter client registers fresh FCM device tokens on startup and updates the user record in Firestore. |

## 7. Cost & Timeline
- **Infrastructure Cost**: Fully fits within Google Cloud and Firebase free tiers for MVP volumes (Cloud Run scale-to-zero, Firestore 50k reads/day, Cloud Tasks 1M ops/month, free FCM delivery).
- **Timeline**: 4–6 weeks for MVP:
  - Week 1–2: Backend API (Go, Firestore, Cloud Tasks) & Auth integration.
  - Week 3–4: Flutter UI, task lifecycle, and FCM integration.
  - Week 5: Push dispatch validation, end-to-end testing, and account linking flows.
  - Week 6: Polishing, QA, and deployment preparation.

## 8. Verification & Success Criteria
- **Unit & Integration Tests**: Backend unit test coverage >80% on business logic; API integration tests validating CRUD operations and authorization boundaries.
- **Cloud Task Dispatch Verification**: Automated tests validating that task creation/updates enqueue Cloud Tasks with correct payloads and schedule times.
- **Push Delivery Testing**: End-to-end device testing verifying FCM/APNs notification receipt and deep-linking on both iOS and Android.
- **Anonymous Linking Test**: Verification that guest user data seamlessly migrates when linked to Google and Apple accounts without data loss or duplicate records.

## 9. Open Questions & Future Considerations
- In future phases, should a lightweight local SQLite cache be added to support offline read-only viewing?
- Future consideration for customizable reminder offsets (e.g., remind 15 minutes or 1 hour before deadline).
