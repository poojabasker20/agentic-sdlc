# Discussion Summary: Todo Mobile Application

## 1. Objective & Background
Build a mobile-first task management application (Flutter) that allows users to create tasks with descriptions, assign priorities, set deadlines, and receive timely notifications. The application must operate seamlessly offline and synchronize changes automatically across user devices when connectivity is available.

## 2. Limits of Existing Solutions
- **Online-Only Apps**: Inaccessible without an active network connection, leading to dropped tasks and delayed deadline notifications.
- **Local-Only Apps**: Risk permanent data loss upon device change/damage, with no multi-device support.
- **Cloud-Dependent Push Alerts**: Remote-only push notifications (FCM/APNs) fail when devices are offline or delayed during aggressive OS battery optimization (Android Doze / iOS background throttling).

## 3. Goals & Non-Goals
### Goals
- **Task Management**: Create, view, update, delete, and mark tasks as completed with rich descriptions.
- **Prioritization**: 3-tier priority system (High, Medium, Low) with default Medium and dynamic sorting/filtering.
- **Deadlines & Notifications**: Support deadline configuration with user-configurable lead-time reminders (exact time, 15m, 1h, 1d prior) firing reliably offline via OS-level exact alarms.
- **Offline-First Synchronization**: Immediate local read/write persistence with background cloud synchronization and Last-Write-Wins (LWW) conflict resolution.
- **User Authentication**: Secure user login/signup across devices via Firebase Auth.

### Non-Goals (MVP)
- Team collaboration, shared task boards, or role-based assignments.
- Complex recurring task schedules (e.g., RRULE recurrence like "every 2nd Tuesday").
- Natural language parsing for task creation (e.g., "Buy milk tomorrow at 5pm").
- Web or desktop client targets (strictly iOS and Android mobile MVP).

## 4. Critical User Journeys (CUJs)
- **CUJ 1: Create & Prioritize Task Offline**: User opens app without internet, creates a task "Finish design review" with High priority and due date tomorrow at 3:00 PM with a 1-hour advance reminder. Task saves immediately to local cache, and local OS alarm is scheduled.
- **CUJ 2: Deadline Alert Delivery**: At 2:00 PM tomorrow (offline or online), the OS triggers an exact local notification. User taps notification to open directly into the task details screen.
- **CUJ 3: Multi-Device Synchronization**: User marks task as complete on Device A while offline. Upon reconnecting, Firestore synchronizes state; Device B reflects completion and cancels pending local alarms.

## 5. High-Level Architecture
- **Client (Flutter)**:
  - **Presentation Layer**: Flutter UI (Task list, Task detail/editor, Filter/Sort views).
  - **State Management**: Provider / Riverpod for reactive local UI updates.
  - **Notification Scheduler**: Native local notifications via `flutter_local_notifications` using Android `AlarmManager` / iOS `UNUserNotificationCenter` for guaranteed offline firing.
  - **Persistence & Sync**: Firestore Client SDK with local cache persistence enabled.
- **Backend & Cloud (Firebase)**:
  - **Authentication**: Firebase Authentication (Email/Password & Social OAuth).
  - **Database**: Cloud Firestore with collection-per-user rules (`/users/{userId}/tasks/{taskId}`).
  - **Cloud Messaging**: FCM used for lightweight data sync pings between devices to cancel/reschedule alarms.

## 6. Risks & Mitigations
- **OS Battery Optimization**: Android Doze and OEM-specific battery managers can kill alarms.
  - *Mitigation*: Request `SCHEDULE_EXACT_ALARM` permissions and `USE_EXACT_ALARM` on Android 12+, with proper battery optimization exemption prompts.
- **Device Reboot & Clock Drift**: Reboot clears scheduled alarms in AlarmManager; time zone changes can skew triggers.
  - *Mitigation*: Register a `BOOT_COMPLETED` broadcast receiver to re-register active alarms from local storage upon device reboot; store all deadlines in UTC with local offset awareness.
- **Offline Data Sync Conflicts**: Simultaneous edits across multiple offline devices.
  - *Mitigation*: Last-Write-Wins (LWW) utilizing server timestamps and client mutation tracking.

## 7. Cost & Timeline
- **Timeline**: 4–6 weeks standard MVP:
  - Weeks 1–2: Project scaffolding, Auth, local CRUD, and UI layouts.
  - Weeks 3–4: Notification scheduling engine, reboot receivers, priority filtering.
  - Weeks 5–6: Firestore sync, conflict validation, e2e testing, and hardening.
- **Cost**: Low operational cost. Firestore, Firebase Auth, and FCM fit comfortably within free/pay-as-you-go tiers for initial scale.

## 8. Verification Plan & Success Metrics
- **Unit & Widget Tests**:
  - Task model serialization and UTC date handling.
  - Priority sorting logic (High > Medium > Low).
  - State management offline status indicators.
- **Integration & Notification Tests**:
  - Verify exact alarm firing when app is killed, in background, and offline.
  - Verify alarm rescheduling after device restart (reboot simulation).
  - Verify bidirectional cloud sync after network drop and reconnection.
- **Success Metrics**:
  - 100% on-time delivery rate for local notifications when scheduled >= 1 minute in advance.
  - Sub-100ms local UI response time for task creation and updates.
