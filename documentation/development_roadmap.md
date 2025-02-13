# Development Roadmap

## Phase 1: MVP (8-10 Weeks)
- **Core Functionality:** 
  - Implement multi-cloud cost retrieval modules.
  - Basic reporting: total costs, cost breakdown by service/account.
  - CLI command for generating a summary report.
- **Deliverable:** Version 0.1.0 on PyPI with documentation on setup and usage.

## Phase 2: Enhanced Reporting & Anomaly Detection (6 Weeks After MVP)
- **New Features:**
  - Add anomaly detection module (flag cost spikes).
  - Implement budget threshold alerts.
  - Introduce basic forecasting (e.g., linear extrapolation or using AWS forecast).
- **Deliverable:** Version 0.2.x release with improved reporting and alerting.

## Phase 3: Beta Release – Feature Complete (8 Weeks After Phase 2)
- **Expanded Capabilities:**
  - Advanced forecasting and normalization of multi-cloud data.
  - Full CLI support with commands for reporting, anomaly detection, and forecasting.
- **Deliverable:** Beta version (0.9.0) for broader testing.

## Phase 4: Stable v1.0 Release (4 Weeks After Beta)
- **Finalization:**
  - Bug fixes, performance tuning, and comprehensive documentation.
- **Deliverable:** Version 1.0.0 on PyPI – a stable, production-ready release.

## Phase 5: Post-1.0 – Deep Automation Features
- **Future Enhancements:**
  - Introduce optimization recommendations and policy enforcement.
  - Optionally add automation actions (e.g., auto-shutdown for idle resources).
- **Versioning:** Feature enhancements in 1.x series based on user feedback.
