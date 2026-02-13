📜 Mission Control: The Scribe Marketing Engine

1. Executive Summary
The Goal: To scale Faith Explorer (iOS) to 1M+ views and $X,XXX MRR using autonomous agentic marketing.
The Strategy: We are replicating the "Larry/OpenClaw" viral loop. Instead of manual content creation, we use an autonomous agent (The Scribe) to research theological trends, generate photorealistic TikTok slideshows, and schedule them via API.

2. Core Product: Faith Explorer
To market the app, the agent must understand these unique selling points (USPs):

Scale: 144,000+ verses across 9 religious traditions (Bible, Quran, Tanakh, etc.).

The AI Dialogue Simulator: Real-time interfaith debates between AI personas (Rev. Sarah, Brother Ahmed, etc.).

Semantic Cross-Search: Searching by concept (e.g., "The afterlife") rather than just keywords.

Bilingual: Full Spanish/English toggle (critical for the LATAM growth phase).

3. The Tech Stack (The "Brain" & "Body")
Any agent working on this repo must interface with or maintain the following:

Orchestrator: OpenClaw (Local AI Agent framework).

Brain: Anthropic Claude (via OpenClaw) for reasoning and "Theological IQ."

Visuals: OpenAI gpt-image-1.5 (Batch API) for "iPhone-style" realistic photos.

Distribution: Postiz API for pushing content to TikTok/X drafts.

Analytics: RevenueCat Skill (Clawhub) to monitor MRR and adjust strategy.

4. The Viral Formula (The "Larry" Method)
We do not make "ads." We make "human moments." The Scribe follows these strict rules:

A. The "Conflict" Hook
Every slideshow must start with a human tension point.

Formula: [Relatable Person] + [Theological Conflict/Curiosity] + [App Solution] = Viral Result.
Example: "My Catholic Abuela didn't believe the Quran mentioned Mary more than the New Testament. I used Faith Explorer to show her the truth."

B. The "Locked Architecture" Prompts
To maintain the illusion of a real human "Study Journal," all image generation prompts must lock the environment:

Setting: A specific dark oak desk in St. George, Utah (desert morning light).

Consistency: The same coffee mug and Bible/Quran placement in every slide.

Realism: Use "natural phone camera quality" and "slight lens flare"—never "hyper-realistic AI art."

5. Repository Structure & Files
SOUL.md: The agent's personality, tone, and bilingual instructions.

HEARTBEAT.md: The cron-style schedule (Research -> Gen -> Post).

skills/: Custom markdown files teaching the agent how to use Postiz and OpenAI APIs.

MEMORY.md: A log of what hooks flopped (e.g., "Feature-based hooks") vs. what flew (e.g., "Landlord/Grandma hooks").

6. Success Metrics (KPIs)
Retention: Does the agent learn from low-view posts?

Conversion: Correlation between TikTok "Link in Bio" clicks and RevenueCat trials.

Efficiency: Keeping the cost per post under $0.30 via Batch API usage.

Instruction for Agents: When modifying this repo, prioritize Visual Consistency and Emotional Tension. If a hook doesn't sound like a "human story," it is a failure.