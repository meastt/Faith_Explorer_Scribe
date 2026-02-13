---
name: FaithExplorerTikTok
description: Generates viral 6-slide TikTok carousels for Faith Explorer
version: 1.0.0
tools: [gemini-image-gen, postiz-api, shell]
triggers:
  - schedule: "0 10 * * *"
  - command: generate-slides
inputs:
  - hooks.json
outputs:
  - assets/{date}/{lang}/hook*_slide*.png
---

# TikTok Master Skill

## Viral Formula: The "Skeptic to Believer" Pivot
Every post must follow this 6-slide structure:

### Slide 1 (The Hook)
- **Image:** A realistic "iPhone photo" of the app open on a desk next to a Bible and a Quran.
- **Overlay:** Use the "[Person] + [Conflict] -> AI Solution" formula.
- **Example:** "My atheist roommate said religion is all the same. I used Faith Explorer's semantic search to show him he's 80% right."

### Slides 2-5 (The Meat)
- **Image:** Screenshots of the app.
  - Slide 2: Semantic search results
  - Slide 3: Dialogue Simulator with Rev. Sarah
  - Slide 4: Spanish toggle in action
  - Slide 5: Cross-reference chart
- **Overlay:** Explain the "Aha!" moment.

### Slide 6 (The Call to Action)
- **Image:** A serene photo of the user looking at their phone.
- **Overlay:** "Explore 144,000+ verses. Link in bio."

## Image Generation Prompt (Locked Architecture)

Base prompt (never change the environment):
```
iPhone photo, shot from above (flat lay) on a dark oak wooden desk.
A white ceramic coffee mug is on the left. An iPhone 15 Pro is centered.
Natural morning light from a window in St. George, Utah.
Slight lens flare. Natural phone camera quality.
[VARIABLE_SCREEN_CONTENT]
```

### Rules
1. Never use hyper-realistic AI art style — always natural phone camera quality
2. Keep the desk, mug, and lighting consistent across ALL slides
3. Generate both English and Spanish versions of every carousel
4. Use Gemini 2.5 Flash Image (9:16 aspect ratio) to keep cost under $0.25/post
