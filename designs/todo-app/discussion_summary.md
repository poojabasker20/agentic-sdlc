# Discussion Summary: Todo Mobile Application

## 1. Objective & Background
Build a mobile-first task management application (Flutter) that allows users to create tasks with descriptions, assign priorities, set deadlines, and receive timely notifications. The application must operate seamlessly offline, support guest mode without mandatory initial signup, and synchronize changes automatically across user devices when connectivity and an authenticated account are available.

## 2. Limits of Existing Solutions
- **Online-Only Apps**: Inaccessible without an active network connection, leading to dropped tasks and delayed deadline notifications.
- **Local-Only Apps**: Risk permanent data loss upon device change/damage, with no multi-device support.
- **Forced Authentication Barriers**: Requiring immediate registration discourages adoption; users want immediate utility.
- **Cloud-Dependent Push Alerts**: Remote-only push notifications (FCM/APNs) fail when devices are offline or delayed during aggressive OS battery optimization (Android Doze / iOS background throttling).

## 3. Goals & Non-Goals
### Goals
- **Task Management**: Create, view, update, delete, and mark tasks as completed with rich descriptions.
- **Archive & Unarchive**: Ability to archive tasks to declutter the active view, view archived tasks in a dedicated archive view, and unarchive them at any time.
- **Prioritization**: 3-tier priority system (High, Medium, Low) with default Medium and dynamic sorting/filtering.
- **Deadlines & Notifications**: Support deadline configuration with user-configurable lead-time reminders (exact time, 15m, 1h, 1d prior) firing reliably offline via OS-level exact alarms.
- **Offline-First Synchronization**: Immediate local read/write persistence with background cloud synchronization and Last-Write-Wins (LWW) conflict resolution.
- **Authentication & Guest Mode**: Support instant-access Guest Mode (via Firebase Anonymous Auth / local session) allowing immediate use without signup, with the ability to link/upgrade to a permanent account (Email/OAuth) preserving all guest tasks.

### Non-Goals (MVP)
- Team collaboration, shared task boards, or role-based assignments.
- Complex recurring task schedules (e.g., RRULE recurrence like "every 2nd Tuesday").
- Natural language parsing for task creation (e.g., "Buy milk tomorrow at 5pm").
- Web or desktop client targets (strictly iOS and Android mobile MVP).

## 4. Critical User Journeys (CUJs)
- **CUJ 1: Guest Mode Onboarding & Task Creation**: A new user downloads the app and starts immediately in Guest Mode without seeing a mandatory login screen. The user creates a task with High priority and due date tomorrow with a 1-hour advance reminder.
- **CUJ 2: Archiving & Unarchiving Tasks**: User finishes or sets aside a task, swipes or selects "Archive". The task is hidden from the main active list but preserved in an "Archived" view. Later, the user inspects archived items and selects "Unarchive" to restore it.
- **CUJ 3: Guest Account Upgrade / Linking**: User later decides to sync across devices, navigates to Settings -> "Link Account", signs in with Google/Email. All guest tasks and preferences are linked seamlessly to the permanent account without data loss.
- **CUJ 4: Deadline Alert Delivery**: At the scheduled reminder time (offline or online), the OS triggers an exact local notification. User taps notification to open directly into the task details screen.
- **CUJ 5: Multi-Device Synchronization**: Authenticated user completes or archives a task on Device A while offline. Upon reconnecting, Firestore synchronizes state; Device B reflects the changes and cancels/adjusts local alarms.

## 5. High-Level Architecture
- **Client (Flutter)**:
  - **Presentation Layer**: Flutter UI (Task list, Task detail/editor, Archive view, Filter/Sort views).
  - **State Management**: Provider / Riverpod for reactive local UI updates.
  - **Notification Scheduler**: Native local notifications via `flutter_local_notifications` using Android `AlarmManager` / iOS `UNUserNotificationCenter` for guaranteed offline firing.
  - **Persistence & Sync**: Firestore Client SDK with local cache persistence enabled.
- **Backend & Cloud (Firebase)**:
  - **Authentication**: Firebase Authentication supporting Anonymous Auth (Guest Mode) with seamless credential linking (`linkWithCredential`) to Email/Password & Social OAuth.
  - **Database**: Cloud Firestore with collection-per-user rules (`/users/{userId}/tasks/{taskId}`), with `isArchived` flag indexed for filtered queries.
  - **Cloud Messaging**: FCM used for lightweight data sync pings between devices to cancel/reschedule alarms.

## 6. Risks & Mitigations
- **Guest Data Loss on App Uninstall**: Guest users might uninstall without knowing local data isn't tied to an email.
  - *Mitigation*: Provide subtle, non-intrusive in-app banners recommending account linking to back up data.
- **OS Battery Optimization**: Android Doze and OEM-specific battery managers can kill alarms.
  - *Mitigation*: Request `SCHEDULE_EXACT_ALARM` permissions and `USE_EXACT_ALARM` on Android 12+, with proper battery optimization exemption prompts.
- **Device Reboot & Clock Drift**: Reboot clears scheduled alarms in AlarmManager; time zone changes can skew triggers.
  - *Mitigation*: Register a `BOOT_COMPLETED` broadcast receiver to re-register active alarms from local storage upon device reboot; store all deadlines in UTC with local offset awareness.
- **Offline Data Sync Conflicts**: Simultaneous edits across multiple offline devices.
  - *Mitigation*: Last-Write-Wins (LWW) utilizing server timestamps and client mutation tracking.

## 7. Cost & Timeline
- **Timeline**: 4–6 weeks standard MVP:
  - Weeks 1–2: Project scaffolding, Anonymous Auth / Guest Mode, local CRUD & Archive state, UI layouts.
  - Weeks 3–4: Notification scheduling engine, reboot receivers, priority filtering, account linking flow.
  - Weeks 5–6: Firestore sync, conflict validation, e2e testing, and hardening.
- **Cost**: Low operational cost. Firestore, Firebase Auth (including Anonymous Auth), and FCM fit comfortably within free/pay-as-you-go tiers for initial scale.

## 8. Verification Plan & Success Metrics
- **Unit & Widget Tests**:
  - Task model serialization, UTC date handling, and `isArchived` filtering.
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
  - Sub-100ms local UI response time for task creation, archiving, and updates.
