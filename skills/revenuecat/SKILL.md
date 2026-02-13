---
name: RevenueCatMetrics
description: Pulls MRR, subscriber, and download metrics from RevenueCat
version: 1.0.0
tools: [revenuecat-api]
triggers:
  - schedule: "0 11 * * *"
  - command: check-metrics
env:
  - REVENUECAT_API_KEY
  - REVENUECAT_PROJECT_ID
---

# RevenueCat Skill

## Overview
Monitors Faith Explorer's revenue and growth metrics daily. Flags declines to inform the next day's hook strategy.

## API Reference

**Base URL:** `https://api.revenuecat.com/v2`

### Authentication
```
Authorization: Bearer {REVENUECAT_API_KEY}
Content-Type: application/json
```

### Endpoints

#### Overview Metrics
```
GET /projects/{REVENUECAT_PROJECT_ID}/metrics/overview

Response:
{
  "mrr": 123.45,
  "active_subscribers": 42,
  "new_trials": 8,
  "downloads": 156
}
```

## Decision Logic
- If MRR drops day-over-day: flag in MEMORY.md and pivot hooks to "more controversial" angles
- If new trials spike: note which hook style drove the spike
- If downloads plateau: try more Spanish-language content
