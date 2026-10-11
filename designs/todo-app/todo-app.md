# Todo Mobile Application

*   **Author:** engineering-team@example.com
*   **Status:** Draft
*   **Date:** 2025-05-18

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
