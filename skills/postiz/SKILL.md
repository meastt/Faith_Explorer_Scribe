---
name: PostizIntegration
description: Schedules TikTok and X drafts via the Postiz API
version: 1.0.0
tools: [postiz-api]
triggers:
  - schedule: "30 10 * * *"
  - command: post-drafts
env:
  - POSTIZ_API_KEY
  - POSTIZ_WORKSPACE_ID
---

# Postiz Skill

## Overview
Pushes generated slide carousels to Postiz as "Self-Only" drafts for TikTok and X.
Michael reviews and approves before they go live.

## API Reference

**Base URL:** `https://app.postiz.com/api/v1`

### Authentication
All requests require:
```
Authorization: Bearer {POSTIZ_API_KEY}
Content-Type: application/json
```

### Endpoints

#### Upload Media
```
POST /media
Content-Type: multipart/form-data

Fields:
  - file: (binary) the image file
  - workspace_id: {POSTIZ_WORKSPACE_ID}

Response: { "id": "media_xxx" }
```

#### Create Draft Post
```
POST /posts
{
  "workspace_id": "{POSTIZ_WORKSPACE_ID}",
  "type": "draft",
  "platform": "tiktok" | "twitter",
  "title": "Post title",
  "media": ["media_xxx", "media_yyy"],
  "visibility": "self"
}

Response: { "id": "post_xxx", "status": "draft" }
```

## Workflow
1. Upload each slide image via `/media`
2. Collect media IDs
3. Create one draft per platform (TikTok, X) with all 6 slides attached
4. Log the draft IDs and status to MEMORY.md
