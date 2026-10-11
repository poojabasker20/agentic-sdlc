# Cloud-Synced Mobile Todo Application

* **Author:** engineering-team
* **Status:** Draft
* **Date:** 2025-05-18

---

## Overview

The Cloud-Synced Mobile Todo Application is a cross-platform mobile task management system built with Flutter (iOS & Android) and a Go (Echo) backend running on Google Cloud Run. It combines immediate, zero-friction anonymous onboarding with robust cloud synchronization, hierarchical subtask decomposition, and precision deadline reminder notifications. Users can capture and organize thoughts instantaneously without an initial registration wall, break complex tasks into actionable checklists, schedule push notifications at custom offsets relative to deadlines, and subsequently link their accounts (via Google or Apple) to ensure persistent access across multiple devices.

## The Problem

Modern mobile task management applications frequently suffer from high onboarding friction and suboptimal notification workflows:
1. **Mandatory Sign-Up Friction**: Most cloud-synced task applications force users through account registration, email verification, or third-party OAuth before creating their first task. This upfront barrier creates significant onboarding friction and drop-off for users who simply want to capture a thought quickly.
2. **Local-Only Trade-Offs**: Lightweight task apps that bypass registration typically store data exclusively on-device, sacrificing cross-device backup, seamless device migration, and reliable cloud-scheduled push notifications.
3. **Inflexible Notification Systems**: Existing task managers often either lack deadline reminders or offer rigid notification triggers, preventing users from receiving advance reminders (e.g., 15 minutes or 1 hour prior to a deadline) tailored to task urgency.
4. **Task Overload Without Decomposition**: Users frequently face complex tasks that cannot be effectively represented by a single title/description, leading to disorganized lists or reliance on separate checklist apps.

The proposed solution provides a seamless bridge: an anonymous-first mobile client paired with a cloud-backed architecture utilizing Firestore, Google Cloud Tasks, and Firebase Cloud Messaging (FCM) / Apple Push Notification service (APNs). Users receive instant utility upon first launch, can decompose tasks into hierarchical subtasks, schedule precision deadline reminders, and preserve their data across devices upon voluntary account linking.

## Goals

* **Zero-Friction Anonymous Onboarding**: Provide an immediate task creation experience upon first app open without mandatory sign-up, persisting credentials via platform Keychain/Keystore.
* **Hierarchical Task & Subtask Management**: Support parent tasks (title, description, deadline, priority) with up to 10 ordered subtasks that maintain independent completion statuses.
* **Configurable Push Deadline Reminders**: Allow users to select customizable reminder offsets (e.g., at deadline, 15 minutes before, 1 hour before, 1 day before) and reliably deliver push notifications to iOS and Android devices via Google Cloud Tasks and FCM/APNs.
* **Task Lifecycle Controls**: Provide full task lifecycle management, enabling users to mark items complete, archive completed or stale tasks, and permanently delete tasks.
* **Seamless Account Linking**: Enable anonymous users to link their guest session with Google or Apple identity providers, preserving all existing tasks and subtasks for cross-device synchronization.
* **Low-Latency Standard Compute**: Run backend services on Google Cloud Run configured with `min-instances: 1` to eliminate cold-start latency for interactive requests and webhook execution.

## Non-Goals

* **Offline Mutation & Bidirectional Sync Engine**: Offline conflict resolution, CRDTs, or local mutation queuing are out of scope for the MVP; write operations require network connectivity (local read-only caching is planned for Phase 2).
* **Multi-User Collaboration & Shared Lists**: Sharing task lists, delegating subtasks, or multi-user editing will not be supported in MVP.
* **Complex Recurring Rules**: Advanced recurrence patterns (such as RRULE RFC 5545 specifications) are deferred to subsequent releases.
* **Attachments & Rich Media**: Storing arbitrary file attachments, images, or voice notes within tasks is excluded from this version.
