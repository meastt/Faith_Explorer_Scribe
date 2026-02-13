# Setup: API Keys & Accounts Needed

Copy `.env.example` to `.env` and fill in each key below.

## Required Keys

### 1. Anthropic (Claude AI)
- **Key:** `ANTHROPIC_API_KEY`
- **Get it:** https://console.anthropic.com/settings/keys
- **Used for:** The Scribe's brain — reasoning, hook writing, strategy

### 2. Google Gemini (Image Generation)
- **Key:** `GEMINI_API_KEY`
- **Get it:** https://aistudio.google.com/apikey
- **Used for:** Gemini 2.5 Flash Image slide generation (the "Locked Architecture" photos)
- **Estimated cost:** ~$0.039/image = ~$0.23 per 6-slide carousel

### 3. Postiz (Social Scheduling)
- **Keys:** `POSTIZ_API_KEY` + `POSTIZ_WORKSPACE_ID`
- **Get it:** https://app.postiz.com → Settings → API Keys
- **Used for:** Creating TikTok and X draft posts
- **Setup:** Connect your TikTok and X accounts in the Postiz dashboard first

### 4. RevenueCat (Revenue Metrics)
- **Keys:** `REVENUECAT_API_KEY` + `REVENUECAT_PROJECT_ID`
- **Get it:** https://app.revenuecat.com → Project Settings → API Keys
- **Used for:** Tracking MRR, subscribers, downloads, trial conversions

### 5. X / Twitter (Trend Research)
- **Key:** `X_BEARER_TOKEN`
- **Get it:** https://developer.x.com/en/portal/dashboard → Project → Keys & Tokens
- **Used for:** Searching trending theological discussions for hook ideas
- **Tier needed:** Basic ($100/mo) or Free (limited to 500K tweets/mo read)

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r scripts/requirements.txt

# 2. Copy and fill in your keys
cp .env.example .env
# Edit .env with your actual keys

# 3. Run the pipeline (will skip steps with missing keys)
python scripts/pipeline.py
```

## Checklist

- [ ] Anthropic API key added
- [ ] Gemini API key added
- [ ] Postiz API key + workspace ID added
- [ ] Postiz: TikTok account connected
- [ ] Postiz: X account connected
- [ ] RevenueCat API key + project ID added
- [ ] X Bearer Token added
- [ ] Ran `python scripts/pipeline.py` successfully
