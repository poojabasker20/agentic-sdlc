# Discussion Summary: Cloud-Synced Mobile Todo Application

## 1. Objective & Problem Statement
Build a lightweight, cross-platform mobile Todo application for iOS and Android that minimizes onboarding friction by supporting anonymous guest sessions while providing real-time cloud synchronization, hierarchical subtask breakdown, customizable deadline reminders, priority labeling, and task lifecycle management (active, archive, delete).

## 2. Goals & Non-Goals

### Goals
- **Instant Onboarding**: Allow users to immediately create and manage tasks via anonymous authentication without an upfront registration wall.
- **Task Management & Subtasks**:
  - Support task heading (title), text description, deadline date/time, and priority levels (Low, Medium, High).
  - Enable task decomposition: a parent task can be broken down into multiple smaller subtasks (checklist items) with independent completion statuses.
- **Customizable Reminder Notifications**:
  - Allow users to choose when they want to be reminded relative to the deadline (e.g., at deadline time, 15 minutes before, 1 hour before, 1 day before, or custom offset).
  - Reliably deliver push reminders to iOS and Android devices via Google Cloud Tasks and Firebase Cloud Messaging (FCM) / Apple Push Notification service (APNs).
- **Lifecycle Management**: Enable users to mark tasks and subtasks complete, archive completed/stale tasks, or delete them.
- **Account Linking**: Allow users to link their anonymous profile with an identity provider (Google, Apple, or Email) to secure tasks and sync across multiple devices.
- **Compute & Architecture Standards**:
  - Mobile client built using Flutter.
  - Backend implemented in Go (Echo framework).
  - Backend compute deployed exclusively on Google Cloud Run (containerized, automatic scale-to-zero).
  - Database persistence via Google Cloud Firestore.

### Non-Goals
- **Complex Offline Sync Engine**: Offline conflict resolution, CRDTs (Conflict-free Replicated Data Types), or distributed bidirectional offline syncing are excluded for MVP. The app will operate in an online-only model for mutations, with local read-only caching planned for phase 2.
- **Collaborative / Shared Lists**: Multi-user shared boards or assigned tasks are deferred to future iterations.
- **Complex Recurring Task Rules**: Advanced recurring task recurrence engines (e.g., RRULE support) are out of scope for MVP.

## 3. Critical User Journeys (CUJs)

1. **CUJ 1: First-Time User Task Creation with Subtasks & Custom Reminders**
   - User opens the app for the first time; an anonymous session is initialized via Firebase Auth and saved in the platform Keychain (iOS) or Keystore (Android).
   - User enters a heading, description, selects "High" priority, sets a deadline for tomorrow at 10:00 AM, and chooses a reminder offset of "1 hour before" (9:00 AM).
   - User breaks down the task into smaller subtasks (e.g., "Draft outline", "Review findings").
   - Backend persists the parent task and subtasks to Firestore and enqueues a Google Cloud Task scheduled for tomorrow at 9:00 AM.

2. **CUJ 2: Deadline Notification Delivery**
   - At the scheduled reminder time (e.g., 9:00 AM), Google Cloud Tasks invokes the backend dispatch endpoint.
   - The backend validates the task status and version (ensures it was not completed, deleted, or rescheduled).
   - Backend sends a push notification through Firebase Cloud Messaging (FCM) and Apple Push Notification service (APNs) to the user's registered device tokens.
   - User taps the push notification and opens directly to the specific task and subtasks.

3. **CUJ 3: Subtask Progress & Task Archiving**
   - User checks off individual subtasks as they make progress.
   - Once all subtasks are finished or the task is completed, user archives the task.
   - Task transitions to the Archived tab; pending reminder Cloud Tasks are marked obsolete.
   - User can unarchive or permanently delete items from the archive.

4. **CUJ 4: Account Linking for Cross-Device Sync**
   - User navigates to Settings or responds to an in-app prompt to "Link Account".
   - User authenticates via Apple Sign-In or Google Sign-In.
   - Anonymous credentials are linked to the permanent UID in Firebase Auth; existing Firestore tasks remain attached to the user UID.
   - User signs in on another iOS or Android device and instantly sees all tasks and subtasks.

## 4. Current Limits & New Approach
- **Current Limits**: Most existing mobile task apps enforce mandatory registration walls before first use, causing drop-offs, or they remain purely offline without cross-device notifications.
- **New Approach**: Anonymous-first cloud architecture enabling instantaneous task and subtask entry, coupled with scheduled Google Cloud Tasks for precise, serverless push notification delivery.

## 5. High-Level Architecture

```
+-------------------------------------------------------------+
|                 Mobile Client (Flutter)                     |
|  - iOS & Android Targets                                    |
|  - Firebase Auth SDK (Anonymous + Federated Linking)        |
|  - Firebase Cloud Messaging (FCM) / APNs Client SDK         |
|  - Secure Storage (iOS Keychain / Android Keystore)         |
+------------------------------+------------------------------+
                               | HTTPS / REST
                               v
+-------------------------------------------------------------+
|                 Backend API (Go / Echo)                     |
|                   Hosted on Google Cloud Run                |
|  - Auth Middleware (Verify Firebase ID Tokens)              |
|  - Task & Subtask CRUD Endpoints                            |
|  - Notification Scheduler (Google Cloud Tasks Client)       |
|  - Dispatch Webhook Handler (Internal task executor)        |
+--------------+-------------------------------+--------------+
               |                               |
               v                               v
    +--------------------+           +-------------------+
    |    Firestore DB    |           | Google Cloud Tasks|
    |  - Users Collection|           |  - Scheduled Task |
    |  - Tasks & Subtasks|           |    Queue          |
    +--------------------+           +---------+---------+
                                               | Triggers at Reminder Time
                                               v
                                     +-------------------+
                                     |  Dispatch Handler |
                                     |  (FCM / APNs)     |
                                     +-------------------+
```

### Architectural Decisions

1. **Compute Platform**:
   - **Google Cloud Run**: Containerized Go service offering automatic scale-to-zero, low cold-start latency (<1s in Go), standard Docker packaging, and straightforward deployment. Selected as the dedicated compute platform.

2. **Push Notification Services**:
   - **Firebase Cloud Messaging (FCM)**: Unified push notification delivery platform used to route push notifications to Android devices and forward to iOS devices.
   - **Apple Push Notification service (APNs)**: Apple's native transport used by FCM to deliver notifications to iOS devices.

3. **Data Model**:
   - Tasks stored under `users/{userId}/tasks/{taskId}`.
   - Subtasks embedded as an ordered array of subtask objects (`id`, `title`, `isCompleted`, `order`) within the parent task document to ensure single-document atomic updates and eliminate multi-document read latency.

4. **Customizable Notification Scheduling**:
   - Task stores `deadline` and `reminderOffset` (e.g., -3600 seconds for 1 hour before).
   - Execution time = `deadline - reminderOffset`.
   - Google Cloud Tasks queue enqueues the job at this target execution timestamp.
   - Dispatch handler validates task version/timestamp before dispatching through FCM/APNs.

## 6. Risks & Mitigations

| Risk | Severity | Mitigation |
| :--- | :--- | :--- |
| **Notification Failure on Offline Devices** | Medium | Because notifications are cloud-driven push notifications via FCM/APNs, a device without network connection at the reminder time cannot receive the notification until reconnected. Accepted trade-off of the online-only MVP model. |
| **Anonymous Account Data Loss** | Medium | If an anonymous user deletes the app before linking, data cannot be recovered. Mitigated by persisting tokens in the platform Keychain/Keystore and displaying non-intrusive linking banners. |
| **Task Rescheduling Churn** | Low | Modifying deadlines or reminder offsets creates orphaned Cloud Tasks. Mitigated by validating the task version and reminder timestamp at execution time rather than issuing expensive Cloud Task cancellation calls. |
| **Large Subtask Lists** | Low | Embedding subtasks within the parent task document is bounded (e.g., maximum 50 subtasks per task) to remain well below Firestore's 1 MB document limit. |

## 7. Cost & Timeline
- **Infrastructure Cost**: Fully fits within Google Cloud and Firebase free tiers for MVP volumes (Cloud Run scale-to-zero, Firestore 50k reads/day, Google Cloud Tasks 1M ops/month, free FCM/APNs delivery).
- **Timeline**: 4–6 weeks for MVP:
  - Week 1–2: Backend API (Go, Echo, Firestore, Google Cloud Tasks, subtask models) & Auth middleware.
  - Week 3–4: Flutter UI (hierarchical task/subtask management, reminder offset picker, FCM integration).
  - Week 5: Push dispatch validation, end-to-end integration tests, account linking.
  - Week 6: Polishing, QA, and deployment to Google Cloud Run.

## 8. Verification & Success Criteria
- **Unit & Integration Tests**: Backend unit test coverage >80%; API integration tests validating CRUD operations for tasks and nested subtasks.
- **Cloud Task Dispatch Verification**: Automated tests validating that task creation/updates with custom reminder offsets enqueue Google Cloud Tasks with the exact expected target timestamps.
- **Push Delivery Testing**: End-to-end device testing verifying FCM/APNs notification receipt at the chosen reminder offset on both iOS and Android.
- **Account Linking Flow**: Verification that anonymous sessions migrate cleanly when linked to Google and Apple accounts without losing tasks or subtasks.

## 9. Future Roadmap & Iterations
- **Phase 2 - Offline Read-Only Cache**: Integrate a local SQLite cache (via `sqflite` or `drift` in Flutter) so users can view previously fetched tasks and subtasks without network connectivity.
- **Phase 3 - Shared Lists**: Allow task sharing and collaboration between linked user accounts.
