# ISO 14001 Environmental Management System (EMS) Gateway

[![Compliance Framework](https://img.shields.io/badge/Compliance-ISO%2014001%20%7C%2014064%20%7C%2014067-emerald)](https://github.com/RodrigoAngelCollazo/carbon-footprint-engine)
[![Data Quality Integrity](https://img.shields.io/badge/Data%20Quality-100%25-success)](https://github.com/RodrigoAngelCollazo/carbon-footprint-engine)

An enterprise-grade, Test-Driven Development (TDD) data governance gateway engineered to operationalize **ISO 14001** compliance under strict **Process-as-Code** principles. This sentinel serves as an automated regulatory gatekeeper—intercepting facility operational data to monitor legal compliance, evaluate environmental aspects, and validate continuous improvement targets before committing telemetry matrices to long-term storage.

---

## 🔄 The ISO 14001 Continuous Improvement Loop (PDCA)

Rather than acting as a static accounting tool, this engine integrates directly into an organization's **Plan-Do-Check-Act (PDCA)** cycle to systematically minimize overall environmental impact:

     [ PLAN ] ──► Define Targets & Legal Requirements
        ▲                                 │
        │                                 ▼
     [ ACT ]                      [ DO ] Operational Ingestion
        ▲                                 │
        │                                 ▼
        └───────── [ CHECK ] ◄────────────┘
            sentinel/guard.py Validation Gate

The data pipeline processes incoming records through an isolated validation cycle. If an organization's real-time footprints fail to align with their defined ISO 14001 continuous improvement targets, or if a legal regulatory threshold is crossed, the engine triggers an automatic non-conformance flag.

---

## 🏗️ Technical Pipeline Architecture

             [ Raw Facility & Emission Telemetry ]
                               │
                               ▼
    ┌─────────────────────────────────────────────────────┐
    │             sentinel/guard.py (EMS Gate)            │
    ├─────────────────────────────────────────────────────┤
    │ ✔ ISO 14001: Overarching Governance & Legal Status  │
    │   └── ✔ ISO 14064: Corporate Scope 1 / 2 / 3 Quant  │
    │   └── ✔ ISO 14067: Lifecycle Product Carbon LCA     │
    └──────────────────────────┬──────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
     [ EMS Conformance ]             [ ISO Non-Conformance ]
                │                             │
                ▼                             ▼
 ┌─────────────────────────────┐┌─────────────────────────────┐
 │   TimescaleDB Staging Sync  ││  Raise Explicit ValueError  │
 │  (Commit & Proceed to Act)  ││  (Drop Payload & Alert Log) │
 └─────────────────────────────┘└─────────────────────────────┘

---

## 📋 Implemented Governance & Metric Standards

### 🛡️ Core Framework: ISO 14001 (Environmental Management)
The master validation schema targets organizational lifecycle improvement and legal compliance verification:
* **`legal_compliance_status`**: Enforces strict boolean verification against localized pollution and emission regulatory frameworks.
* **`environmental_aspects`**: Dynamic tracking matrix handling multi-vector waste footprints (solid waste mass, processing effluents).
* **`continuous_improvement_target_co2e`**: Programmable carbon ceiling caps that automatically scale downward year-over-year to enforce absolute impact minimization.

### 📊 Metric Engines Nested Under the Framework
1. **ISO 14064 (Organizational GHG Inventories):** Audits corporate boundary carbon footprints across Scope 1 (Direct Combustion), Scope 2 (Indirect Electricity), and Scope 3 (Value Chain Dynamics).
2. **ISO 14067 (Product Carbon Footprint - PCF):** Tracks cradle-to-grave lifecycle performance from raw materials processing through to product distribution and final disposal.

---

## 📂 System Manifest

* `sentinel/guard.py` — Immutable Pydantic baseline validation schemas executing the combined ISO framework validations.
* `config.json` — Static lookup matrix defining localized grid emission parameters and regulatory thresholds.
* `tests/` — Comprehensive TDD suites ensuring non-conformance boundaries trigger alerts accurately.
