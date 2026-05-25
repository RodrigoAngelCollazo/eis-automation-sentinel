# Environmental Impact Assessment (EIA) Automation Sentinel

[![Build Matrix Status](https://github.com/RodrigoAngelCollazo/eis-automation-sentinel/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/RodrigoAngelCollazo/eis-automation-sentinel/actions)
[![Data Quality Integrity](https://img.shields.io/badge/Data%20Quality-100%25-success)](https://github.com/RodrigoAngelCollazo/eis-automation-sentinel)

An enterprise-grade, Test-Driven Development (TDD) data governance engine engineered to ingest, parse, and validate streaming environmental telemetry. Built under the principles of **Process-as-Code**, this sentinel serves as a strict regulatory gatekeeper—intercepting raw telemetry arrays to enforce EPA-aligned air and water quality bounds before committing them to high-throughput time-series databases.

---

## 🏗️ System Architecture & Data Flow

[ Raw Sensor Telemetry Stream ] ──► Ingestion Layer
│
▼
┌────────────────────────────────────────┐
│    sentinel/guard.py (Pydantic Gate)   │
├────────────────────────────────────────┤
│ 🛠️ Structural Validation                 │
│ 🧪 Regulatory Boundary Assertions      │
└────────────────────────────────────────┘
│
┌───────────────────────┴───────────────────────┐
▼                                               ▼
[ Within Legal Matrix ]                          [ Critical Breach Alert ]
│                                               │
▼                                               ▼
┌──────────────────────────────┐                ┌──────────────────────────────┐
│ Execute DB Transaction Block │                │  Raise Explicit ValueError   │
│  (TimescaleDB Staging Sync)  │                │   (Drop Payload & Flag Log)  │
└──────────────────────────────┘                └──────────────────────────────┘


The data pipeline processes incoming arrays through an isolated validation cycle. To preserve production database integrity, validated records are temporarily written to transactional staging matrices before a highly efficient upsert merge runs against historic analytical nodes.

---

## 📊 Regulated Quality Matrices

The ingestion engine uses Pydantic schema validation to strictly enforce environmental safety compliance across two focal ecosystems:

### 1. Atmospheric Telemetry Boundaries
* **$PM_{2.5}$ Particulate Matter:** Maximum permissible ceiling capped at `15.0 µg/m³`. Exceeding values immediately halt processing.
* **$NO_2$ (Nitrogen Dioxide):** Vector bounds checked against maximum regulatory limits of `40.0 ppb` to flag air degradation spikes.

### 2. Aquatic Telemetry Boundaries
* **pH Acidity Balance:** Hard target constraints restricted to the legal safety bandwidth ($6.5 \le \text{pH} \le 8.5$).
* **Dissolved Oxygen (DO):** Continuous floor monitoring ensuring levels stay safely above `5.0 mg/L` to track ecosystem health.

---

## 📂 Production Directory Layout

* `sentinel/guard.py` — Core Pydantic telemetry models, structural typing rules, and custom threshold validation logic.
* `config.json` — Decoupled configuration repository storing official EPA environmental ceiling and floor parameters.
* `tests/` — Test-Driven Development (TDD) matrix verifying edge cases, zero-values, and critical environmental breach exceptions.
* `pyproject.toml` — Test framework automation configuration and test coverage tracking layouts.
