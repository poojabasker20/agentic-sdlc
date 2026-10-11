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
