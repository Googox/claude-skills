# HeyGen Hyperframes

**Tier:** POWERFUL  
**Category:** Engineering  
**Domain:** AI Video Production / Content Automation  

---

## Overview

Design and generate structured multi-scene AI videos using HeyGen's MCP tools and the Hyperframes methodology. Each video is decomposed into intentional scenes (frames) — Hook, Problem, Solution, Proof, CTA — generated individually via HeyGen and assembled into a cohesive final video. Covers avatar selection, voice design, brand kit application, captions, multi-language output, and batch production automation.

## Core Capabilities

- **Hyperframes framework** — structured 3–6 frame video architecture for ads, explainers, demos, and social content
- **Video Agent (AI mode)** — one-call video generation from a prompt with style templates
- **Avatar video** — explicit avatar + script + voice control per frame
- **Cinematic Avatar** — prompt-driven multi-reference generation (Seedance pipeline)
- **Image animation** — animate brand images or product shots with lip-sync
- **Voice design & cloning** — custom branded voices per persona
- **Multi-language** — translate any frame with voice clone and lip-sync
- **Brand kit** — enforce colors, fonts, logos across all frames
- **Batch production** — Python script to generate all frames in parallel and track status

---

## When to Use

- Producing short-form video ads (15–60 sec) for paid social from a brief
- Creating product explainer videos with a talking avatar
- Generating personalized outreach videos at scale (one video per lead)
- Building multi-language video campaigns from a single English master
- Automating recurring video formats (weekly updates, feature launches)

---

## Hyperframes Architecture

A Hyperframe video is a sequence of discrete scenes stitched together. Each frame has a single job:

```
┌─────────────────────────────────────────────────────────────┐
│  HYPERFRAME VIDEO STRUCTURE                                 │
├───────┬─────────┬──────────┬──────────┬─────────────────── │
│ Frame │ Name    │ Duration │ Job                           │
├───────┼─────────┼──────────┼────────────────────────────── │
│  F1   │ Hook    │ 2–4 s    │ Stop the scroll               │
│  F2   │ Problem │ 4–8 s    │ Name the pain                 │
│  F3   │ Solution│ 6–12 s   │ Introduce your offer          │
│  F4   │ Proof   │ 4–8 s    │ Add credibility or demo       │
│  F5   │ CTA     │ 2–5 s    │ Drive one action              │
└───────┴─────────┴──────────┴────────────────────────────── │
                   Total: 18–37 seconds
```

Each frame is a separate HeyGen video job. After all jobs complete, frames are concatenated in post-production (Kapwing, DaVinci Resolve, FFmpeg).

### Frame Types by Content Goal

| Goal | Recommended Frames |
|------|-------------------|
| Paid social ad | Hook → Problem → Solution → CTA |
| Product explainer | Hook → Problem → Solution → Proof → CTA |
| Feature launch | Hook → Solution → Demo → CTA |
| Outreach video | Hook → Personalised Problem → Solution → CTA |
| Tutorial teaser | Hook → Problem → Preview → CTA |

---

## MCP Workflow

### Step 1 — Discover available styles, avatars, voices

```
mcp__HeyGen__list_video_agent_styles   # Discover visual style templates
mcp__HeyGen__list_avatar_looks         # Discover avatar looks (avatarType: "photo_avatar" or "studio_avatar")
mcp__HeyGen__list_voices               # Discover TTS voices
mcp__HeyGen__list_brand_kits           # Get brandKitId for brand-consistent output
```

Capture the IDs you'll reuse across all frames for consistency:
- `style_id` — applies uniform scene composition and pacing
- `avatar_id` — same presenter across frames
- `voice_id` — same voice across frames
- `brand_kit_id` — brand colors, fonts, logo overlay

### Step 2 — Plan your script per frame

Write a tight script for each frame. Each frame's script should be self-contained — it must make sense even if the viewer jumps in mid-video.

**Hook frame rule:** First 2 seconds must trigger a pattern interrupt. Use a question, bold claim, or visual surprise in the `motionPrompt`.

**CTA frame rule:** One action only. Never "visit our site AND follow us." Pick one.

### Step 3 — Generate frames

**Option A — Video Agent (recommended for quick production):**
```
mcp__HeyGen__create_video_agent
  mode: "chat"
  prompt: "[Full hyperframe brief with all 5 frame scripts]"
  style_id: "<from step 1>"
  avatar_id: "<from step 1>"
  voice_id: "<from step 1>"
  brand_kit_id: "<from step 1>"
  orientation: "portrait"   # 9:16 for social, "landscape" for 16:9
```
Surface the session URL: `https://app.heygen.com/video-agent/{session_id}`  
Poll `mcp__HeyGen__get_video_agent_session` until status is `completed`.

**Option B — Explicit avatar per frame (full control):**
```
# For each frame independently:
mcp__HeyGen__create_video_from_avatar
  avatarId: "<look_id>"
  script: "<frame script>"
  voiceId: "<voice_id>"
  aspectRatio: "9:16"
  resolution: "1080p"
  engine: {"type": "avatar_v"}          # Avatar V for highest quality
  motionPrompt: "<motion for this frame>"
  background: {"type": "color", "value": "#0f0f0f"}
  caption: {"file_format": "srt", "style": "default"}
  title: "Campaign-Name — F1-Hook"
```
Poll `mcp__HeyGen__get_video` until `status == "completed"`, then retrieve `video_url`.

**Option C — Cinematic Avatar (no script, prompt-only):**
```
mcp__HeyGen__create_video_from_cinematic_avatar
  prompt: "<scene description>"
  avatarId: ["<look_id_1>", "<look_id_2>"]   # up to 3 reference looks
  references: [{"type": "url", "url": "<product_image_url>"}]
  aspectRatio: "9:16"
  resolution: "1080p"
  autoDuration: true
  enhancePrompt: true
```

**Option D — Image animation (brand / product visual):**
```
mcp__HeyGen__create_video_from_image
  image: {"type": "url", "url": "<image_url>"}
  script: "<frame script>"
  voiceId: "<voice_id>"
  expressiveness: "high"
  aspectRatio: "9:16"
```

### Step 4 — Caption & quality check

All frames should include captions for silent viewing. If using `create_video_from_avatar` or `create_video_from_image`, set `caption: {"file_format": "srt"}` in the request. Captions are returned via `subtitle_url` on the completed video.

### Step 5 — Multi-language output (optional)

Translate any frame to additional languages with voice clone and lip-sync:
```
mcp__HeyGen__create_video_translation
  video: {"type": "url", "url": "<frame_video_url>"}
  outputLanguages: ["Spanish (Mexico)", "Portuguese (Brazil)", "French"]
  mode: "precision"          # higher lip-sync quality
  enableCaption: true
  brandGlossaryId: "<glossary_id>"   # enforce brand term translations
```

### Step 6 — Assemble final video

After all frame `video_url`s are collected, concatenate with FFmpeg:

```bash
# Create file list
for url in "${VIDEO_URLS[@]}"; do
  tmpfile=$(mktemp --suffix=.mp4)
  curl -sL "$url" -o "$tmpfile"
  echo "file '$tmpfile'" >> filelist.txt
done

# Concatenate (lossless re-mux, assumes same codec/resolution)
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

For cross-platform concatenation or format normalization, re-encode:
```bash
ffmpeg -f concat -safe 0 -i filelist.txt \
  -vf "scale=1080:1920,setsar=1" \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k \
  output.mp4
```

---

## Polling Pattern

HeyGen video generation is asynchronous. All creation endpoints return an ID; poll until done.

```python
import time

def wait_for_video(get_fn, video_id: str, timeout: int = 600) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = get_fn(videoId=video_id)
        status = result.get("status")
        if status == "completed":
            return result
        if status == "failed":
            raise RuntimeError(f"Video {video_id} failed: {result.get('error')}")
        time.sleep(10)
    raise TimeoutError(f"Video {video_id} did not complete within {timeout}s")
```

For Video Agent sessions, poll `get_video_agent_session` and check for `status == "completed"` or `status == "waiting_for_input"` (chat mode pause).

---

## Voice Strategy

### Use a consistent voice persona across all frames
Switching voices mid-video sounds jarring. Lock one `voice_id` per campaign.

### Clone a voice for brand identity
```
mcp__HeyGen__clone_voice
  voiceName: "Brand Voice — Sarah"
  audio: {"type": "url", "url": "<30-60s clean audio sample url>"}
  removeBackgroundNoise: true
```
Poll `mcp__HeyGen__get_voice` until `status == "complete"`.

### Design a custom voice (no sample required)
```
mcp__HeyGen__design_voice
  # Prompt-based voice design — describe tone, pace, accent
```

### Voice settings per frame
Use `voiceSettings` to fine-tune delivery per frame:
- Hook: `speed: 1.1, pitch: 2` — energetic
- Problem: `speed: 0.95, pitch: -1` — serious
- CTA: `speed: 1.05, pitch: 1` — confident

---

## Asset Upload for Backgrounds

For branded backgrounds or product shots, upload as a HeyGen asset first:

```
mcp__HeyGen__create_asset_upload
  filename: "brand-bg.jpg"
  contentType: "image/jpeg"
  sizeBytes: <exact_byte_size>

# → returns asset_id + upload_url

# PUT the file bytes to upload_url (from your environment)

mcp__HeyGen__complete_asset_upload
  assetId: "<asset_id>"
```

Then reference the `asset_id` in `background: {"type": "image", "asset_id": "<asset_id>"}`.

---

## Production Checklist

```
[ ] Frame scripts written and timed (read aloud; must fit target duration)
[ ] Avatar look ID confirmed (list_avatar_looks, check supported_api_engines for Avatar V)
[ ] Voice ID confirmed or clone/design job completed
[ ] Style ID selected (list_video_agent_styles)
[ ] Brand kit ID set (list_brand_kits)
[ ] Aspect ratio locked (9:16 social / 16:9 widescreen / 1:1 square)
[ ] Resolution set (1080p standard; 4k for premium)
[ ] Background assets uploaded (create_asset_upload → complete_asset_upload)
[ ] Captions enabled on all frames
[ ] All frame video_urls collected and verified status == "completed"
[ ] Frames concatenated and output.mp4 verified
[ ] Translations queued for target markets (create_video_translation)
```

---

## Common Pitfalls

- **Long scripts per frame** — Each frame must be short. If you need 30+ words for the Hook, cut it. Attention drop-off is steepest in the first 4 seconds.
- **Missing `fetch-depth`** — Not a git issue; for HeyGen: always wait for `status == "completed"` before calling `video_url`. URL is null until rendering finishes.
- **Avatar V incompatibility** — Check `supported_api_engines` on the avatar look before setting `engine: {"type": "avatar_v"}`. Sending `avatar_v` for an ineligible look is rejected.
- **Mixed resolutions** — All frames must be the same resolution and aspect ratio before FFmpeg concatenation. Normalize with `-vf scale=W:H` if mixing sources.
- **`webm` + background** — Selecting `outputFormat: "webm"` (transparent alpha) auto-removes the background; any `background` setting is rejected.
- **Translation on a non-completed video** — Source `video_url` must be accessible. Pass the completed video URL, not the job ID.
- **No brand glossary** — Technical or brand terms (product names, trademarks) will be translated literally. Always set `brandGlossaryId` when translating marketing content.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Time from brief to first draft video | < 30 minutes |
| Frames generated per campaign | 3–6 |
| Languages per campaign | 1–5 |
| Cost per video (API credits) | Varies by resolution and engine |
| Re-generation rate (quality rejection) | < 20% |
