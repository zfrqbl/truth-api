<!-- BANNER -->

<p align="center">
  <img src="https://dummyimage.com/1200x300/0b0d0e/ffffff&text=UnspokenTruth+API+%E2%80%94+Developer+Truths.+No+Filter." alt="UnspokenTruth API Banner"/>
</p>

<p align="center">
<img src="https://img.shields.io/github/repo-size/zfrqbl/truth-api?style=for-the-badge" />
<img src="https://img.shields.io/github/languages/top/zfrqbl/truth-api?style=for-the-badge" />
<img src="https://img.shields.io/github/last-commit/zfrqbl/truth-api?style=for-the-badge" />
<img src="https://img.shields.io/github/issues/zfrqbl/truth-api?style=for-the-badge" />
<img src="https://img.shields.io/github/stars/zfrqbl/truth-api?style=for-the-badge" />
<img src="https://img.shields.io/github/license/zfrqbl/truth-api?style=for-the-badge" />
</p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-Framework-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/Uvicorn-ASGI-black?style=for-the-badge"/>
<img src="https://img.shields.io/badge/YAML-Config-CB171E?style=for-the-badge&logo=yaml&logoColor=white"/>
<img src="https://img.shields.io/badge/JSON-Data-black?style=for-the-badge&logo=json"/>
<img src="https://img.shields.io/badge/Railway-Deploy-0B0D0E?style=for-the-badge"/>
<img src="https://img.shields.io/badge/API-Single%20Endpoint-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Runtime-Stateless-orange?style=for-the-badge"/>
</p>

---

# UnspokenTruth API

### Developer Truths. No Filter.

> One endpoint. Zero parameters. Brutal honesty.

---

## Overview

**UnspokenTruth API** is a minimalist HTTP service that returns painfully accurate developer truths.

It is intentionally designed to be:

* stateless
* deterministic
* config-driven
* infrastructure-light
* operationally trivial

No authentication.
No request body.
No query parameters.

Just:

```
GET /truth
```

---

## Live Endpoint

```
https://api.unspokentruth.dev/truth
```

Example:

```bash
curl https://api.unspokentruth.dev/truth
```

Response:

```json
{
  "truth": "The smallest change can cause the biggest outage.",
  "category": "risk",
  "day": "monday",
  "weight": "high",
  "id": "truth-021"
}
```

---

## Plain Text Mode

Request:

```
Accept: text/plain
```

Response:

```
The smallest change can cause the biggest outage.
```

---

## Core Idea

Most APIs try to do everything.

This API does **one thing perfectly**:

> Return a truth developers recognize instantly.

The value is content, not infrastructure.

---

## Day-Aware Truth Engine

Truths are weighted by weekday.

| Day      | Bias           |
| -------- | -------------- |
| Monday   | heavy truths   |
| Tue–Thu  | medium truths  |
| Friday   | lighter truths |
| Saturday | casual         |
| Sunday   | existential    |

No parameters required. The server decides.

---

## Architecture Philosophy

This project enforces strict engineering discipline:

* no business logic hardcoded
* configuration externalized
* modules isolated
* dependencies injected
* runtime stateless

---

## Tech Stack

| Layer         | Technology |
| ------------- | ---------- |
| Language      | Python     |
| Framework     | FastAPI    |
| Server        | Uvicorn    |
| Configuration | YAML       |
| Data Store    | JSON file  |
| Deployment    | Railway    |

---

## Project Structure

```
app/
 ├── main.py
 ├── settings.yaml
 ├── api/
 ├── core/
 └── domain/
tests/
```

Only one module reads configuration.
All other modules receive injected config.

---

## Configuration

Runtime behavior is controlled entirely via:

```
app/settings.yaml
```

Configurable parameters include:

* rate limits
* endpoints
* headers
* caching policy
* truth file path
* weight tables
* logging format
* validation rules

Startup fails if config is invalid.

---

## Response Contract

```
{
  truth: string
  category: string
  day: string
  weight: string
  id: string
}
```

This schema is permanent and version-stable.

---

## Rate Limiting

Default:

```
100 requests / hour / client
```

Client identity = remote address.
Forwarded headers are not trusted.

---

## Headers

Responses always include:

```
Cache-Control: no-store
Vary: Accept
```

Random responses must never be cached.

---

## Error Model

All errors return structured JSON:

```json
{
  "error": "rate_limited",
  "message": "Too many requests.",
  "request_id": "...",
  "retry_after_seconds": 3600
}
```

---

## Content Rules

Every truth must:

* be ≤2 sentences
* stand alone
* be universally relatable
* be slightly uncomfortable

Must NOT:

* reference companies or tools
* give advice
* require context
* target specific people or roles

---

## Running Locally

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Tests

```
pytest
```

Validation includes:

* config schema
* truth uniqueness
* weighting distribution
* header correctness
* error responses

---

## Deployment

Platform: **Railway**
Trigger: push → main
SSL: automatic

---

## Guarantees

This API will never:

* store users
* track usage
* require login
* collect data
* personalize responses

---

## Non-Goals

Out of scope by design:

* databases
* dashboards
* analytics
* caching layers
* admin panels
* multiple endpoints

---

## Author

**Zafar Iqbal**
GitHub: `zfrqbl`
Email: [zafar.gaditek@gmail.com](mailto:zafar.gaditek@gmail.com)

---

## License

MIT License

---

## Final Truth

If you read this README instead of deploying something, you already know why this API exists.
