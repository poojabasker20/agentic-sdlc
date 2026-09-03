# Document Specification: `PRD.pdf`


---

> *Auto-parsed Multimodal PDF artifact for Agentic SDLC context grounding.*


---

## Page 1

PRD-001: Core Greeting API Service
Status: Approved
Owner: Nordea Platform Team
Target Repository: poojabasker20/springboot-hello-world
Current Version: 1.0.0
## 1. Executive Summary & Vision
The Greeting API provides lightweight, low-latency greeting endpoints for client applications and
downstream microservices. It serves as the baseline reference implementation for RESTful
service development and contract testing within the organization.
## 2. Target Personas
● Public Client: External web or mobile applications requesting generic or personalized
greetings.
● Internal Microservice: Backend systems making service-to-service calls to verify
network egress/ingress and payload serialization.
## 3. Product Scope & Functional Requirements

| Capability | Supported<br>Method | Path / Query | Response Payload Schema |
| --- | --- | --- | --- |
| Default Greeting | GET | / | {"message": "Hello,<br>World!", "recipient":<br>"World"} |
| Query Greeting | GET | /hello?name={name} | {"message": "Hello,<br>{name}!", "recipient":<br>"{name}"} |
| Path Greeting | GET | /hello/{name} | {"message": "Hello,<br>{name}!", "recipient":<br>"{name}"} |

## 4. Non-Functional Requirements (SLAs & Quality Attributes)

---

## Page 2


| Category | Specification & Target Metric |
| --- | --- |
| Response Latency | p99 < 50ms under nominal load of 500 RPS. |
| Availability | 99.99% uptime across active-active deployment nodes. |
| Architecture State | Fully stateless design with zero session persistence to support<br>horizontal auto-scaling. |

## 5. Acceptance Criteria (BDD Scenarios)

| Scenario | Given | When | Then |
| --- | --- | --- | --- |
| 1. Default Root Greeting | A client calls the root<br>path without<br>parameters. | The client sends<br>GET /. | Status 200 OK is returned<br>with body {"message":<br>"Hello, World!", "recipient":<br>"World"} |
| 2. Personalized Query<br>Greeting | A valid parameter<br>name=Alice. | The client sends<br>GET<br>/hello?name=Alice. | Status 200 OK is returned<br>with body {"message":<br>"Hello, Alice!", "recipient":<br>"Alice"} |

## 6. Assumptions & Out-of-Scope Items

| Classification | Details |
| --- | --- |
| Technical Assumptions | Spring Boot 3.x web stack running on Java 17/21 LTS runtime with<br>Apache Maven build tooling. |
| Out of Scope | Persistent database storage, distributed Redis caching, and user<br>authentication token issuance (managed by external Ingress<br>Gateway). |
