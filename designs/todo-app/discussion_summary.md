# Discussion Summary: Todo Mobile Application

## 1. Objective & Background
Build a mobile-first task management application using the Flutter framework that allows users to create tasks with descriptions, check-pointed subtasks, assign priorities, set deadlines, and receive timely notifications. The application must operate seamlessly offline, support guest mode without mandatory initial signup, and synchronize changes automatically across user devices when connectivity and an authenticated account are available.

## 2. Limits of Existing Solutions
- **Online-Only Applications**: Inaccessible without an active network connection, leading to dropped tasks and delayed deadline notifications.
- **Local-Only Applications**: Risk permanent data loss upon device change, damage, or factory reset, with no multi-device synchronization support.
- **Forced Authentication Barriers**: Requiring immediate registration discourages adoption; users want immediate utility.
- **Cloud-Dependent Push Alerts**: Remote-only push notifications via Firebase Cloud Messaging (FCM) or Apple Push Notification service (APNs) fail when devices are offline or delayed during aggressive Operating System (OS) battery optimization (such as Android Doze or iOS background throttling).
- **Monolithic Tasks Without Sub-steps**: Task apps lacking granular subtasks force users to either clutter their main list with micro-items or manage steps outside the application.

## 3. Goals & Non-Goals
### Goals
- **Task Management**: Create, Read, Update, and Delete (CRUD) tasks, and mark tasks as completed with rich descriptions.
- **Check-Pointed Subtasks**: Support ordered checklist subtasks within each task (title and completion state), with visual progress indicators (e.g., "3 of 5 completed").
- **Archive & Unarchive**: Ability to archive tasks to declutter the active view, view archived tasks in a dedicated archive view, and unarchive them at any time.
- **Prioritization**: 3-tier priority system (High, Medium, Low) with default Medium and dynamic sorting/filtering.
- **Deadlines & Configurable Notifications**: Support deadline configuration with user-scheduled alert lead times (e.g., exactly at deadline, 15 minutes before, or 60 minutes before deadline) firing reliably offline via OS-level exact alarms.
- **Offline-First Synchronization**: Immediate local read/write persistence with background cloud synchronization and Last-Write-Wins (LWW) conflict resolution based on timestamps.
- **Authentication & Guest Mode**: Support instant-access Guest Mode (via Firebase Anonymous Authentication / local session) allowing immediate use without signup, with the ability to link/upgrade to a permanent account (Email/Password or Social OAuth) preserving all guest tasks.

### Non-Goals (Minimum Viable Product / MVP)
- Team collaboration, shared task boards, or role-based assignments.
- Complex recurring task schedules (e.g., RRULE recurrence like "every 2nd Tuesday").
- Natural Language Processing (NLP) parsing for task creation (e.g., "Buy milk tomorrow at 5pm").
- Web or desktop client targets (strictly iOS and Android mobile platforms for the MVP).
- Nested subtasks beyond one single checklist level (no infinitely recursive task hierarchies).

## 4. Critical User Journeys (CUJs)
- **CUJ 1: Guest Mode Onboarding & Task Creation**: A new user downloads the app and starts immediately in Guest Mode without seeing a mandatory login screen. The user creates a task with High priority and due date tomorrow with a 60-minute advance reminder alert.
- **CUJ 2: Subtask Check-pointing**: User opens an active complex task ("Prepare Presentation"), adds 3 subtasks ("Draft slides", "Review metrics", "Practice talk"). During the day, the user ticks off each subtask item; the parent task displays an updated completion progress indicator.
- **CUJ 3: Archiving & Unarchiving Tasks**: User finishes or sets aside a task, swipes or selects "Archive". The task is hidden from the main active list but preserved in an "Archived" view. Later, the user inspects archived items and selects "Unarchive" to restore it.
- **CUJ 4: Guest Account Upgrade / Linking**: User later decides to sync across devices, navigates to Settings -> "Link Account", signs in with Google or Email. All guest tasks, subtasks, and preferences are linked seamlessly to the permanent account without data loss.
- **CUJ 5: Configurable Deadline Alert Delivery**: At the scheduled reminder lead time (e.g., 15 minutes or 60 minutes prior to deadline, whether offline or online), the OS triggers an exact local notification banner. User taps notification to open directly into the task details screen.
- **CUJ 6: Multi-Device Synchronization**: Authenticated user completes or archives a task or checks off a subtask on Device A while offline. Upon reconnecting, Cloud Firestore synchronizes state; Device B reflects the changes and cancels/adjusts local alarms.

## 5. High-Level Architecture
- **Client (Flutter)**:
  - **Presentation Layer**: Flutter User Interface (UI) featuring Task list, Task detail/editor with interactive subtask checklist, Archive view, and Filter/Sort views.
  - **State Management**: Provider / Riverpod for reactive local UI updates.
  - **Notification Scheduler**: Native local notifications via `flutter_local_notifications` using Android `AlarmManager` / iOS `UNUserNotificationCenter` for guaranteed offline firing.
  - **Persistence & Sync**: Cloud Firestore Client Software Development Kit (SDK) with local cache persistence enabled.
- **Backend & Cloud (Firebase)**:
  - **Authentication**: Firebase Authentication supporting Anonymous Authentication (Guest Mode) with seamless credential linking (`linkWithCredential`) to Email/Password & Social OAuth.
  - **Database**: Cloud Firestore with collection-per-user rules (`/users/{userId}/tasks/{taskId}`). Tasks embed an ordered array of subtask objects (`subtasks: [{id: string, title: string, isCompleted: boolean}]`) to guarantee atomic local updates and seamless Last-Write-Wins (LWW) conflict resolution.
  - **Cloud Messaging**: Firebase Cloud Messaging (FCM) used for lightweight data sync pings between devices to cancel/reschedule alarms.

## 6. Risks & Mitigations
- **Guest Data Loss on App Uninstall**: Guest users might uninstall without knowing local data isn't tied to an email.
  - *Mitigation*: Provide subtle, non-intrusive in-app banners recommending account linking to back up data.
- **Operating System (OS) Battery Optimization**: Android Doze and OEM-specific battery managers can kill alarms.
  - *Mitigation*: Request `SCHEDULE_EXACT_ALARM` permissions and `USE_EXACT_ALARM` on Android 12+, with proper battery optimization exemption prompts.
- **Device Reboot & Clock Drift**: Reboot clears scheduled alarms in AlarmManager; time zone changes can skew triggers.
  - *Mitigation*: Register a `BOOT_COMPLETED` broadcast receiver to re-register active alarms from local storage upon device reboot; store all deadlines in Coordinated Universal Time (UTC) with local offset awareness.
- **Offline Data Sync Conflicts**: Simultaneous edits across multiple offline devices.
  - *Mitigation*: Last-Write-Wins (LWW) utilizing server timestamps and client mutation tracking.

## 7. Cost & Timeline
- **Timeline**: 4–6 weeks standard Minimum Viable Product (MVP):
  - Weeks 1–2: Project scaffolding, Anonymous Auth / Guest Mode, local CRUD, Subtask checklist UI, Archive state.
  - Weeks 3–4: Notification scheduling engine, reboot receivers, priority filtering, account linking flow.
  - Weeks 5–6: Cloud Firestore sync, conflict validation, end-to-end (E2E) testing, and hardening.
- **Cost**: Low operational cost. Cloud Firestore, Firebase Authentication (including Anonymous Auth), and Firebase Cloud Messaging (FCM) fit comfortably within free/pay-as-you-go tiers for initial scale.

## 8. Verification Plan & Success Metrics
- **Unit & Widget Tests**:
  - Task model serialization including embedded subtask list serialization.
  - Subtask toggle state changes and parent progress calculation.
  - Priority sorting logic (High > Medium > Low) across active and archived views.
  - Anonymous-to-Permanent account credential linking logic.
- **Integration & Notification Tests**:
  - Verify exact alarm firing when app is killed, in background, and offline.
  - Verify alarm cancellation when a task is marked completed or archived.
  - Verify alarm rescheduling after device restart (reboot simulation).
  - Verify bidirectional cloud sync after network drop and reconnection.
- **Success Metrics**:
  - 100% data retention when converting a Guest user to an authenticated account.
  - 100% on-time delivery rate for local notifications when scheduled >= 1 minute in advance.
  - Sub-500ms local UI response time for task and subtask checklist interactions.
