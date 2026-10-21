# GK Quiz Mobile Application MVP

* **Author:** engineering-team
* **Status:** Draft
* **Date:** 2025-05-18

---

## Overview

The GK Quiz Mobile Application is a lean, solo trivia experience built with Flutter and Python (FastAPI). It delivers curated, dynamically updated General Knowledge (GK) quiz packs directly to users on iOS and Android without mandatory sign-up walls or account creation. The design guarantees fair scoring through server-evaluated sessions secured by stateless HMAC cryptographic tokens.

## The Problem

Casual mobile quiz players often face high friction upon first launch—including mandatory sign-ups, social media logins, and cluttered ad interfaces—leading to high drop-off rates before the first question is even played. At the same time, client-evaluated quiz games suffer from trivial score tampering, answer inspection via decompiled bundles or HTTP interception, and forged timestamps.

We need a streamlined MVP trivia app that allows immediate play within seconds of installation while maintaining tamper-resistant score evaluation and zero ongoing server maintenance or database synchronization overhead.

## Goals

* **Zero-Friction Onboarding**: Enable users to start playing a quiz immediately upon opening the app without account registration or sign-in walls.
* **Dynamic Content Delivery**: Deliver 2–3 curated GK quiz packs (e.g., Geography, Science, History) over an API so questions can be added or updated without updating client binaries.
* **Tamper-Resistant Scoring**: Ensure answers cannot be inspected beforehand and prevent client-side score modification via server-evaluated sessions validated with stateless HMAC-SHA256 tokens.
* **Cost-Effective Scalability**: Deploy on Cloud Run and Firestore to ensure $0 MVP operating costs within Google Cloud free-tier allocations.

## Non-Goals

* **Multiplayer / Live Battles**: No real-time player matchmaking, 1v1 duels, or synchronous multiplayer.
* **User Accounts & Cloud Sync**: No user profile management, password auth, social login, or multi-device history synchronization.
* **Monetization & Ad Networks**: No in-app purchases (IAP), paywalls, or third-party ad SDK integrations.
* **Offline Quiz Mode**: No offline quiz pack caching or offline answer evaluation; active internet connectivity is required.

## Critical User Journeys (CUJs)

```yaml
- user: Solo Trivia Player
  goals:
  - goal: Discover and play curated GK quiz packs without account registration
    tasks:
    - task: Browse available quiz packs
      scenario:
        given: The mobile application is installed and connected to the internet
        when: The user launches the application
        then: The app displays 2–3 available GK packs with title, question count, and estimated time limit
    - task: Start a quiz session
      scenario:
        given: The user is on the pack catalog screen
        when: The user selects a pack and taps "Start Quiz"
        then: The app requests a session from the backend, receiving question prompts and choices (without answers) and a signed HMAC session token, initiating a countdown timer
    - task: Play through questions and submit answers
      scenario:
        given: The quiz session is in progress
        when: The user answers all questions or the session timer runs out
        then: The app submits selected answer IDs along with the HMAC session token to the backend for verification
    - task: Review score and correct answer explanations
      scenario:
        given: The backend validates the session token and completion timestamp
        when: Evaluation completes successfully
        then: The app displays total score, time taken, and an itemized breakdown of questions with correct answers and explanations
```
