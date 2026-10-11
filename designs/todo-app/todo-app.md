# Todo Mobile Application

*   **Author:** Mobile Engineering Team
*   **Status:** Draft
*   **Date:** 2025-05-18

--------------------------------------------------------------------------------

## Overview

The Todo Mobile Application is a mobile-first task management application built with Flutter, designed to help individuals capture, structure, and track tasks reliably across iOS and Android. The application emphasizes immediate access and high reliability through an offline-first architecture, an instant Guest Mode that defers authentication, granular check-pointed subtasks, and exact-alarm local notifications that fire regardless of network connectivity or operating system background throttling. When connected, tasks synchronize seamlessly across devices via Cloud Firestore.

## The Problem

Modern task management applications frequently fail users in high-mobility and low-connectivity environments:

1. **Connectivity Dependencies**: Cloud-reliant apps fail to load or accept input in offline scenarios (such as transit, remote areas, or flight mode). Furthermore, remote push notifications (FCM/APNs) fail to trigger deadline alerts when a device is offline.
2. **Onboarding Friction**: Forcing immediate registration and account creation introduces high drop-off before users experience the app's core utility.
3. **Fragile Local Solutions**: Local-only task apps protect privacy and operate offline, but lack data durability; users risk catastrophic data loss on device replacement, loss, or factory reset.
4. **Monolithic Task Representation**: Basic todo apps lack structured breakdown mechanisms, forcing users to clutter main task lists with micro-items or track intermediate sub-steps externally.
5. **Notification Unreliability**: Mobile operating systems (Android Doze, iOS background execution restrictions) aggressively throttle standard background tasks, causing missed deadlines unless exact system alarm APIs and reboot recovery mechanisms are utilized.

The Todo Mobile Application addresses these problems by offering zero-friction instant onboarding in Guest Mode, offline-first local persistence, check-pointed subtask checklists, and exact hardware-level notifications, backed by seamless cloud sync and account linking.

## Goals

* **Instant Guest Onboarding**: Allow users to immediately launch the app and create tasks without an initial signup or authentication barrier.
* **Offline-First Persistence**: Ensure 100% of task operations (create, read, update, delete, complete, and archive) work seamlessly without an active internet connection.
* **Structured Subtask Checkpoints**: Enable users to break down complex tasks into ordered subtask checklists with live visual progress indicators (e.g., "3 of 5 completed").
* **Reliable Offline Deadline Reminders**: Provide exact, local deadline notifications with user-configurable lead times (e.g., at deadline, 15 minutes before, 60 minutes before) that fire reliably offline and persist across device reboots.
* **Decluttering via Task Archiving**: Allow users to archive completed or inactive tasks to preserve historical records while keeping the primary workspace focused.
* **Seamless Cloud Synchronization & Account Linking**: Automatically sync tasks to Cloud Firestore when online, allowing guest users to link their session to an authenticated identity (Email/Password or Social OAuth) with zero data loss.

## Non-Goals

* **Collaboration & Shared Boards**: No multi-user shared task boards, team assignments, or collaborative editing in the MVP.
* **Advanced Recurring Scheduling**: No support for complex recurring recurrence rules (RRULE patterns, e.g., "every second Tuesday of the month").
* **Natural Language Processing (NLP)**: No natural language input parsing for automated date/priority extraction (e.g., "Buy groceries tomorrow at 5pm").
* **Web and Desktop Targets**: Deployment is strictly focused on native mobile targets (iOS and Android); web and desktop clients are out of scope for the MVP.
* **Deeply Nested Task Hierarchies**: Subtasks are restricted to a single-level checklist; recursive parent-child task nesting is not supported.

## Critical User Journeys (CUJs)

```yaml
- user: Individual Mobile User
  goals:
  - goal: Onboard and capture urgent tasks without friction
    tasks:
    - task: Instant guest access and task creation
      scenario:
        given: A newly installed application opened for the first time without an existing account.
        when: The user launches the app and creates a High-priority task with a due date and a 60-minute advance reminder.
        then: The task is saved locally immediately in Guest Mode, and an exact local alarm is scheduled without prompting for signup.
    - task: Subtask breakdown and progress tracking
      scenario:
        given: An active parent task with multiple action items.
        when: The user adds three subtasks and marks two of them as completed.
        then: The subtasks persist in order, and the parent task displays a visual progress indicator reflecting "2 of 3 completed".
  - goal: Manage active task decluttering and lifecycle
    tasks:
    - task: Archiving and unarchiving tasks
      scenario:
        given: A finished or deferred task present on the active dashboard.
        when: The user executes an archive action on the task.
        then: The task is removed from the active view, placed in the dedicated Archive view, and can later be unarchived back to active status without data loss.
  - goal: Retain data and access tasks across devices
    tasks:
    - task: Seamless guest account linking
      scenario:
        given: A guest user with existing local tasks who wants to enable multi-device sync.
        when: The user navigates to Settings and completes account linking using Google Sign-In or Email/Password.
        then: All existing guest tasks and subtasks are associated with the authenticated account in Cloud Firestore with zero data loss.
    - task: Timely deadline alert delivery in offline mode
      scenario:
        given: A scheduled task with a reminder set 15 minutes prior to the deadline, with device offline and app killed.
        when: The scheduled alert time arrives.
        then: The operating system triggers an exact local notification banner; tapping it launches the app directly into the task details screen.
    - task: Multi-device state synchronization
      scenario:
        given: An authenticated user with the app installed on two devices (Device A and Device B).
        when: The user completes a subtask and archives a task on Device A while offline, then Device A reconnects.
        then: Changes synchronize to Cloud Firestore using Last-Write-Wins (LWW), and Device B updates its list and cancels any associated obsolete alarms.
```
