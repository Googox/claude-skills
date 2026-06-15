# Hyperframe Structures Reference

Proven frame sequences for common video goals. Copy the structure, fill in scripts, plug in IDs.

---

## Frame Anatomy

Every frame follows this anatomy:

```
FRAME
├── Visual Layer    → avatar look, background, brand kit
├── Audio Layer     → script (TTS) or uploaded audio, voice settings
├── Motion Layer    → motion prompt (Avatar V / photo avatar)
├── Caption Layer   → SRT sidecar (always on), burned-in optional
└── Metadata        → title, callback_id for tracking
```

---

## Structure 1 — Paid Social Ad (Hook → Problem → Solution → CTA)

**Target:** 15–25 seconds total, 9:16, 1080p  
**Use for:** Meta, TikTok, YouTube Shorts, LinkedIn Video  

| # | Frame   | Words | Script Formula |
|---|---------|-------|----------------|
| 1 | Hook    | 8–15  | Question or bold stat that calls out the viewer |
| 2 | Problem | 20–35 | "If you've ever [pain], you know [consequence]." |
| 3 | Solution| 40–60 | "[Product] [does X] so you [get Y] without [Z]." |
| 4 | CTA     | 8–15  | "[Single action] → [single benefit]." |

**Voice settings:**
- Hook: `speed: 1.1, pitch: 2`
- Problem: `speed: 0.95, pitch: -1`
- Solution: `speed: 1.0, pitch: 0`
- CTA: `speed: 1.05, pitch: 1`

---

## Structure 2 — Product Explainer (Hook → Problem → Solution → Proof → CTA)

**Target:** 30–45 seconds total, 16:9 or 9:16, 1080p  
**Use for:** Landing pages, YouTube, demo days  

| # | Frame    | Words | Script Formula |
|---|----------|-------|----------------|
| 1 | Hook     | 10–18 | Provocative question or counterintuitive claim |
| 2 | Problem  | 25–45 | Empathetic description of the status quo pain |
| 3 | Solution | 50–80 | Feature + benefit + differentiator |
| 4 | Proof    | 30–55 | Metric, customer name, or demo moment |
| 5 | CTA      | 8–20  | Time-limited or scarcity-anchored action |

**Proof frame options:**
- Social proof: "Over 10,000 teams switched in 90 days."
- Metric: "Customers cut reporting time from 3 hours to 8 minutes."
- Authority: "Featured in [Publication]."
- Demo: use `create_video_from_cinematic_avatar` with a product screenshot as reference

---

## Structure 3 — Feature Launch (Hook → Solution → Demo → CTA)

**Target:** 20–35 seconds, any aspect ratio  
**Use for:** Product newsletters, in-app announcements, social launch posts  

| # | Frame    | Words | Script Formula |
|---|----------|-------|----------------|
| 1 | Hook     | 8–15  | "We just shipped something you've been asking for." |
| 2 | Solution | 35–55 | "[Feature] lets you [do X] in [Y seconds/clicks]." |
| 3 | Demo     | 30–50 | Walk through the specific interaction in plain language |
| 4 | CTA      | 8–15  | "It's live now — [action]." |

**Demo frame tip:** Use `create_video_from_image` with a product screenshot + script for the demo frame. Animate the screen, avatar speaks alongside.

---

## Structure 4 — Personalised Outreach (Hook → Problem → Solution → CTA)

**Target:** 18–30 seconds, 16:9, 720p (fast generation for scale)  
**Use for:** SDR prospecting, LinkedIn DMs, email video thumbnails  

| # | Frame    | Words | Script Formula |
|---|----------|-------|----------------|
| 1 | Hook     | 8–12  | "[First name], saw [specific thing about their company]." |
| 2 | Problem  | 20–35 | "Most [role] at [company stage] struggle with [pain]." |
| 3 | Solution | 35–55 | "We help [ICP] [achieve outcome] without [trade-off]." |
| 4 | CTA      | 8–15  | "15 minutes this week?" |

**Scale pattern:**
1. Generate a "shell" video for frames 2–4 (same for all prospects)
2. Generate frame 1 (Hook) per-prospect using `create_video_from_avatar` with the personalized script
3. Concatenate: `[hook_N] + [shell_234]` for each prospect

---

## Structure 5 — Tutorial Teaser (Hook → Problem → Preview → CTA)

**Target:** 20–35 seconds, 16:9  
**Use for:** YouTube pre-roll, course marketing, community teasers  

| # | Frame   | Words | Script Formula |
|---|---------|-------|----------------|
| 1 | Hook    | 10–18 | "[Time] to [result]. Here's how." |
| 2 | Problem | 20–35 | "Most people try [wrong approach] and still [fail outcome]." |
| 3 | Preview | 30–45 | "In this video you'll learn: [1], [2], [3]." |
| 4 | CTA     | 8–15  | "Watch now — link in [bio/description]." |

---

## Motion Prompt Templates

Motion prompts control avatar body language (Avatar V / photo avatar only).

| Frame   | Motion Prompt |
|---------|---------------|
| Hook    | "Lean in slightly, raise one eyebrow, direct eye contact with camera" |
| Problem | "Nod slowly, thoughtful expression, slight pause before speaking" |
| Solution| "Open-palm gesture forward, confident posture, slight smile" |
| Proof   | "Point to the side as if referencing a screen, enthusiastic nod" |
| CTA     | "Direct eye contact, single firm nod, slight forward lean at end" |

---

## Background Presets

| Scene Mood | Type   | Value / Asset |
|------------|--------|---------------|
| Clean / minimal | color | `#0f0f0f` (near-black) |
| Warm brand | color | `#1a0a00` (dark amber) |
| Cool tech | color | `#050a18` (deep navy) |
| Branded | image | Upload via `create_asset_upload` |
| Transparent (overlay) | webm output | `outputFormat: "webm"` |

---

## Caption Best Practices

- Always set `caption: {"file_format": "srt"}` on every frame
- For burned-in captions (silent viewing): add `"style": "default"`
- SRT files are returned via `subtitle_url` on the completed video — download and use in post-production for custom styling
- Keep subtitle lines under 42 characters for mobile readability

---

## Multi-Language Matrix

| Source | Target Markets | Languages |
|--------|---------------|-----------|
| English (US) | LatAm | Spanish (Mexico), Portuguese (Brazil) |
| English (US) | Europe | French, German, Spanish (Spain) |
| English (US) | APAC | Japanese, Korean, Chinese (Mandarin, Simplified) |
| English (US) | MENA | Arabic |

Always set `mode: "precision"` for lip-sync quality on marketing content.  
Always set `brandGlossaryId` if you have product-specific terms.  
Always set `enableCaption: true` for translated videos.
