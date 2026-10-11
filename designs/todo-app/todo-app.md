# Todo Mobile Application

*   **Author:** engineering-team@example.com
*   **Status:** Draft
*   **Date:** 2025-05-19

--------------------------------------------------------------------------------

## Overview

The Todo Mobile Application is an offline-first task management application built with Flutter for iOS and Android. It provides users with immediate, frictionless task management out of the box through a persistent Guest Mode, eliminating mandatory onboarding sign-up walls. Users can organize work items through task creation, updates, completion, prioritization (High, Medium, Low), archiving, and configurable deadline reminder alerts. For users wishing to access their tasks across multiple devices, the application provides frictionless account linking (Email/Password and OAuth) backed by Cloud Firestore and Firebase Authentication with Last-Write-Wins (LWW) conflict synchronization.

## The Problem

Modern task management applications frequently suffer from high friction and reliability gaps that undermine daily productivity:
1. **Forced Onboarding Friction**: Many applications mandate immediate user registration before delivering any value. This barrier causes high initial drop-off for users who simply need to jot down an urgent task.
2. **Online-Only Fragility**: Cloud-reliant apps frequently become sluggish or outright unusable in low-connectivity or offline settings (e.g., transit, flights). Crucial actions like creating tasks or checking deadlines fail or block the UI.
3. **Unreliable Deadline Notifications**: Reliance on server-triggered push notifications (APNs/FCM) causes missed reminders when a device is offline, in airplane mode, or subjected to aggressive OS battery optimization (Android Doze, iOS background throttling).
4. **Data Loss in Disconnected Local Apps**: Purely local apps avoid sign-up walls but risk permanent data loss upon device damage, loss, or upgrade, with no path to cloud synchronization.

The Todo Mobile Application addresses these problems with an offline-first architecture powered by Flutter and Firestore persistence, OS-level exact alarm scheduling, and a seamless guest-to-authenticated account upgrade path.

## Goals

*   **Zero-Friction Guest Experience**: Provide instant access to all core task management capabilities upon first launch without requiring sign-up or credentials.
*   **Complete Offline CRUD & Archiving**: Enable full task lifecycle operations—create, read, update, delete, complete, archive, and unarchive—with immediate local persistence (<100ms UI response) regardless of network state.
*   **Reliable Offline Deadline Reminders**: Trigger deadline alerts reliably at user-selected lead times (at deadline, 15m, 1h, 1d prior) using native OS exact alarms even when offline or when the app is terminated.
*   **3-Tier Prioritization & Filtering**: Support High, Medium, and Low priorities with dynamic sorting and filtering to separate active and archived tasks cleanly.
*   **Lossless Account Upgrading**: Allow guest users to link their anonymous session to permanent credentials (Google OAuth or Email/Password) with 100% data retention and automatic cloud synchronization.
*   **Multi-Device Synchronization**: Synchronize tasks across authenticated user devices in the background using Last-Write-Wins (LWW) conflict resolution when online.

## Non-Goals

*   **Multi-User Collaboration & Sharing**: Shared task boards, task assignments, and multi-user comments are out of scope for the MVP.
*   **Complex Recurrence Schedules**: RRULE-based recurring tasks (e.g., repeating every 2nd Tuesday of the month) are out of scope for the MVP.
*   **Natural Language Processing (NLP)**: Free-text date parsing (e.g., "Schedule dentist next Tuesday at 3pm") will not be implemented for MVP task input.
*   **Non-Mobile Form Factors**: Web, desktop (macOS/Windows/Linux), and watchOS platforms are excluded from the initial release; scope is strictly iOS and Android.

## Critical User Journeys (CUJs)

```yaml
- user: Mobile Task Manager (Guest or Authenticated)
  goals:
  - goal: Capture and manage tasks immediately without account registration
    tasks:
    - task: First launch into Guest Mode and task creation
      scenario:
        given: The user opens the app for the first time without an existing account or internet connection.
        when: The user enters the app, taps "New Task", enters title "Submit quarterly report", sets priority to High, and sets a deadline for tomorrow with a 1-hour advance reminder.
        then: The task is saved locally immediately, appears at the top of the active task list, and an exact local alarm is registered with the OS.
    - task: Archiving and restoring completed or deferred tasks
      scenario:
        given: The user has active tasks in their task list.
        when: The user swipes an item or selects "Archive" on an active task.
        then: The task is removed from the active task view and moved to the "Archived Tasks" view, preserving all task metadata and history. The user can navigate to the Archive view and tap "Unarchive" to restore it to the active list.
  - goal: Protect task history and sync across devices
    tasks:
    - task: Upgrading guest profile to permanent cloud account
      scenario:
        given: The user has accumulated multiple tasks and archived items in Guest Mode.
        when: The user navigates to Settings and links their account using Google Sign-In or Email/Password.
        then: The anonymous session credentials are converted to a permanent Firebase account, and all existing local tasks are synced to Cloud Firestore without data loss or duplicate items.
  - goal: Receive timely deadline reminders in any network state
    tasks:
    - task: Offline deadline notification delivery
      scenario:
        given: The device is offline (e.g., Airplane Mode) and the Todo app process is terminated.
        when: The scheduled reminder lead time is reached.
        then: The operating system triggers an exact local banner notification with task details, which opens directly into the task editor screen when tapped.
```

## Technical Plan (Architecture)

### Architectural Overview

The application follows an offline-first, client-centric architecture. Flutter provides the cross-platform UI and state presentation layer, while Firebase Authentication and Cloud Firestore provide persistence, session lifecycle management, and background synchronization.

```text
+-------------------------------------------------------------------------+
|                              Flutter App                                |
|                                                                         |
|  +---------------------+   +---------------------+   +---------------+  |
|  | Active Task List UI |   |  Task Editor Modal  |   |  Archive View |  |
|  +----------+----------+   +----------+----------+   +-------+-------+  |
|             |                         |                      |          |
|             +-------------------------+----------------------+          |
|                                       |                                 |
|                         +-------------v-------------+                   |
|                         |  State Management Layer   |                   |
|                         |    (Riverpod / State)     |                   |
|                         +-------------+-------------+                   |
|                                       |                                 |
|             +-------------------------+----------------------+          |
|             |                                                |          |
|  +----------v-------------+                       +----------v-------+  |
|  | Task Repository        |                       | Notification Svc |  |
|  | (Firestore SDK Cache)  |                       | (Local Alarms)   |  |
|  +----------+-------------+                       +----------+-------+  |
+-------------|------------------------------------------------|----------+
              | (Offline Cache / Sync)                         |
              |                                     +----------v-------+
              |                                     | Native OS Alarms |
              |                                     | - Android Exact  |
              |                                     | - iOS UNCenter   |
              |                                     +------------------+
+-------------v-----------------------------------------------------------+
|                          Firebase Backend                               |
|                                                                         |
|  +------------------------+             +----------------------------+  |
|  | Firebase Auth          |             | Cloud Firestore            |  |
|  | - Anonymous Guest Auth |             | - /users/{uid}/tasks/{id}  |  |
|  | - linkWithCredential() |             | - ServerTimestamps (LWW)   |  |
|  +------------------------+             +----------------------------+  |
+-------------------------------------------------------------------------+
```

### Component Architecture

1. **Presentation Layer (Flutter UI)**:
   - `TaskListScreen`: Primary workspace displaying active tasks, filtered by status and sorted by priority (High > Medium > Low) and due date.
   - `TaskDetailScreen` / `TaskEditorSheet`: Form for title, description, priority selector, due date picker, and notification lead-time options (At due time, 15m before, 1h before, 1d before).
   - `ArchiveScreen`: Separate screen displaying archived tasks with batch or individual "Unarchive" and "Permanent Delete" actions.
   - `SettingsScreen`: Guest upgrade prompt, account linking UI (Google / Email), and notification preferences.

2. **State Management & Domain Layer**:
   - `TaskStateNotifier`: Reactive state controller managing the in-memory task lists, filter parameters (`active`, `archived`, `all`), and sorting rules.
   - `AuthNotifier`: Tracks current user authentication state (Guest/Anonymous vs. Permanent).

3. **Data Access & Offline Persistence Layer**:
   - `TaskRepository`: Interacts with Cloud Firestore with local disk persistence explicitly enabled (`Settings(persistenceEnabled: true)`).
   - All mutations write immediately to the local cache, delivering sub-100ms response times and firing instant stream updates to the UI.
   - When the device has internet access, the Firestore Client SDK automatically drains its mutation queue to the cloud.

4. **Notification & Alarm Engine**:
   - `NotificationService`: Wraps `flutter_local_notifications` plugin.
   - For Android: Schedules alerts via `AlarmManager` using `exactAndAllowWhileIdle` to bypass Android Doze mode. Listens to `ACTION_BOOT_COMPLETED` via a native BroadcastReceiver (`RescheduleAlarmsReceiver`) to reconstruct alarms from local storage following a reboot.
   - For iOS: Schedules requests via `UNUserNotificationCenter` with `UNCalendarNotificationTrigger`.
   - Lifecycle triggers: Creating or updating a task with a deadline registers/reschedules the exact alarm. Marking a task completed or archiving it cancels the associated alarm.

### Data Model & Firestore Schema

Tasks are stored in a user-scoped collection to isolate tenant data and simplify security rules:

```
/users/{userId}/tasks/{taskId}
```

#### Task Document Schema

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `id` | String | Unique UUIDv4 identifier for the task |
| `userId` | String | Firebase Auth UID of the owning user |
| `title` | String | Task title (max 200 characters) |
| `description` | String | Optional markdown-supported details |
| `priority` | String | `HIGH`, `MEDIUM`, or `LOW` (default: `MEDIUM`) |
| `isCompleted` | Boolean | Completion status (default: `false`) |
| `isArchived` | Boolean | Archive state flag (default: `false`) |
| `dueDate` | Timestamp / null | Scheduled deadline in UTC |
| `reminderOffsetMinutes` | Integer / null | Reminder lead time (0, 15, 60, 1440) |
| `createdAt` | Timestamp | Initial creation timestamp |
| `updatedAt` | Timestamp | ServerTimestamp used for Last-Write-Wins (LWW) conflict resolution |

#### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/tasks/{taskId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### Guest Mode & Account Upgrade Flow

1. **Initial Launch**: If no current auth user exists, the app invokes `FirebaseAuth.instance.signInAnonymously()`. This provisions an anonymous `uid` immediately, allowing full read/write operations against `/users/{uid}/tasks` in the local Firestore cache.
2. **Account Linking**: When the guest user chooses to link their account via Google Sign-In or Email/Password:
   - The app acquires the `AuthCredential` from the chosen provider.
   - Calls `FirebaseAuth.instance.currentUser.linkWithCredential(credential)`.
   - The user's `uid` remains identical, converting the anonymous record directly into a permanent identity.
   - Firestore task paths (`/users/{uid}/tasks`) require zero migration, preventing data loss, race conditions, or orphaned documents.

### Conflict Resolution & Multi-Device Sync

- Cloud Firestore handles multi-device synchronization using field-level Last-Write-Wins (LWW) based on `updatedAt` server timestamps.
- When an authenticated user completes, edits, or archives a task on Device A, Firestore syncs the change to Device B upon connectivity.
- On Device B, the real-time collection stream emits the updated task. The `NotificationService` observes state updates: if a synced task is marked completed or archived, any matching pending local notification on Device B is automatically cancelled.
