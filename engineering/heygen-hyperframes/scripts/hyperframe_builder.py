#!/usr/bin/env python3
"""
hyperframe_builder.py — plan and track a HeyGen Hyperframes video campaign.

No LLM or HTTP calls. Reads a JSON campaign spec, validates it, outputs
an execution plan and a status-tracking file you update as frames complete.

Usage:
  python3 hyperframe_builder.py plan   campaign.json
  python3 hyperframe_builder.py status campaign.json [--json]
  python3 hyperframe_builder.py concat campaign.json > filelist.txt
  python3 hyperframe_builder.py brief  --type ad|explainer|demo|outreach
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

FRAME_TYPES = {
    "hook":     {"max_words": 18,  "max_seconds": 4,  "job": "Stop the scroll"},
    "problem":  {"max_words": 45,  "max_seconds": 8,  "job": "Name the pain"},
    "solution": {"max_words": 80,  "max_seconds": 12, "job": "Introduce your offer"},
    "proof":    {"max_words": 55,  "max_seconds": 9,  "job": "Add credibility or demo"},
    "cta":      {"max_words": 20,  "max_seconds": 5,  "job": "Drive one action"},
    "demo":     {"max_words": 70,  "max_seconds": 12, "job": "Show the product in action"},
    "preview":  {"max_words": 40,  "max_seconds": 7,  "job": "Tease what comes next"},
}

TEMPLATE_STRUCTURES = {
    "ad":        ["hook", "problem", "solution", "cta"],
    "explainer": ["hook", "problem", "solution", "proof", "cta"],
    "demo":      ["hook", "solution", "demo", "cta"],
    "outreach":  ["hook", "problem", "solution", "cta"],
    "tutorial":  ["hook", "problem", "preview", "cta"],
}

ASPECT_RATIOS = {"9:16", "16:9", "1:1", "4:5", "5:4"}
RESOLUTIONS   = {"720p", "1080p", "4k"}
ENGINES       = {"avatar_iv", "avatar_v", "cinematic", "image"}


@dataclass
class FrameSpec:
    name: str
    frame_type: str
    script: str
    avatar_id: Optional[str] = None
    voice_id: Optional[str] = None
    motion_prompt: Optional[str] = None
    background_color: Optional[str] = None
    background_asset_id: Optional[str] = None
    engine: str = "avatar_iv"
    expressiveness: Optional[str] = None
    # Filled in after generation
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    subtitle_url: Optional[str] = None
    status: str = "pending"   # pending | generating | completed | failed


@dataclass
class CampaignSpec:
    name: str
    aspect_ratio: str
    resolution: str
    avatar_id: str
    voice_id: str
    frames: list[FrameSpec] = field(default_factory=list)
    style_id: Optional[str] = None
    brand_kit_id: Optional[str] = None
    output_languages: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _word_count(text: str) -> int:
    return len(text.split())


def validate_campaign(spec: dict) -> list[str]:
    errors = []

    if spec.get("aspect_ratio") not in ASPECT_RATIOS:
        errors.append(f"aspect_ratio must be one of {ASPECT_RATIOS}")
    if spec.get("resolution") not in RESOLUTIONS:
        errors.append(f"resolution must be one of {RESOLUTIONS}")
    if not spec.get("avatar_id"):
        errors.append("avatar_id is required (run list_avatar_looks to find one)")
    if not spec.get("voice_id"):
        errors.append("voice_id is required (run list_voices or clone_voice first)")

    frames = spec.get("frames", [])
    if not frames:
        errors.append("frames list is empty — add at least 3 frames")

    for i, f in enumerate(frames):
        label = f"frames[{i}] ({f.get('name', '?')})"
        ft = f.get("frame_type", "")
        if ft not in FRAME_TYPES:
            errors.append(f"{label}: frame_type '{ft}' unknown — choose from {list(FRAME_TYPES)}")
            continue
        limits = FRAME_TYPES[ft]
        script = f.get("script", "")
        wc = _word_count(script)
        if wc > limits["max_words"]:
            errors.append(
                f"{label}: script is {wc} words (max {limits['max_words']} for {ft}). "
                "Tighten the copy — long scripts cause pacing problems."
            )
        engine = f.get("engine", "avatar_iv")
        if engine not in ENGINES:
            errors.append(f"{label}: engine '{engine}' unknown — choose from {ENGINES}")
        if f.get("expressiveness") and engine != "avatar_iv":
            errors.append(f"{label}: expressiveness is only valid with engine 'avatar_iv'")

    return errors


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_plan(spec_path: str):
    with open(spec_path) as fh:
        spec = json.load(fh)

    errors = validate_campaign(spec)
    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  • {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Campaign: {spec['name']}")
    print(f"Format:   {spec['aspect_ratio']} @ {spec['resolution']}")
    print(f"Avatar:   {spec['avatar_id']}")
    print(f"Voice:    {spec['voice_id']}")
    if spec.get("brand_kit_id"):
        print(f"Brand Kit:{spec['brand_kit_id']}")
    if spec.get("output_languages"):
        print(f"Languages:{', '.join(spec['output_languages'])}")
    print()

    total_min = 0
    total_max = 0
    print(f"{'#':<3} {'Frame':<12} {'Type':<10} {'Words':>5}  {'Est. Duration':<15} Script Preview")
    print("-" * 75)
    for i, f in enumerate(spec["frames"]):
        ft = f.get("frame_type", "?")
        limits = FRAME_TYPES.get(ft, {"max_words": 999, "max_seconds": 999})
        wc = _word_count(f.get("script", ""))
        # ~130 wpm speaking rate for TTS
        est_sec = round(wc / 130 * 60)
        est_range = f"{max(1, est_sec-1)}–{est_sec+1}s"
        total_min += max(1, est_sec - 1)
        total_max += est_sec + 1
        preview = f.get("script", "")[:40].strip()
        if len(f.get("script", "")) > 40:
            preview += "…"
        warn = " ⚠" if wc > limits["max_words"] else ""
        print(f"{i+1:<3} {f.get('name',''):<12} {ft:<10} {wc:>5}{warn}  {est_range:<15} {preview}")

    print("-" * 75)
    print(f"    Total estimated video: {total_min}–{total_max}s")
    print()
    print("Next steps:")
    print("  1. Run each frame's MCP call (see SKILL.md Step 3)")
    print("  2. Update campaign.json with video_id and status after each call")
    print("  3. python3 hyperframe_builder.py status campaign.json")
    print("  4. python3 hyperframe_builder.py concat campaign.json > filelist.txt && ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4")


def cmd_status(spec_path: str, as_json: bool = False):
    with open(spec_path) as fh:
        spec = json.load(fh)

    frames = spec.get("frames", [])
    summary = {
        "pending":    [f for f in frames if f.get("status", "pending") == "pending"],
        "generating": [f for f in frames if f.get("status") == "generating"],
        "completed":  [f for f in frames if f.get("status") == "completed"],
        "failed":     [f for f in frames if f.get("status") == "failed"],
    }

    if as_json:
        print(json.dumps({k: [f.get("name") for f in v] for k, v in summary.items()}, indent=2))
        return

    total = len(frames)
    done  = len(summary["completed"])
    print(f"Campaign: {spec['name']} — {done}/{total} frames complete")
    print()
    for f in frames:
        status = f.get("status", "pending")
        icon = {"pending": "⏳", "generating": "🔄", "completed": "✅", "failed": "❌"}.get(status, "?")
        vid_id = f.get("video_id", "—")
        print(f"  {icon} {f.get('name',''):<14} [{f.get('frame_type',''):<9}]  id={vid_id}")
        if f.get("video_url"):
            print(f"       url: {f['video_url']}")
        if f.get("subtitle_url"):
            print(f"       srt: {f['subtitle_url']}")

    print()
    if summary["failed"]:
        print(f"FAILED ({len(summary['failed'])}): {', '.join(f.get('name','') for f in summary['failed'])}")
        print("Re-generate failed frames and update campaign.json with new video_id/status.")
    elif done == total:
        print("All frames complete. Run concat command to build filelist.txt.")
    else:
        remaining = total - done
        print(f"{remaining} frame(s) still pending/generating. Check HeyGen dashboard or poll get_video.")


def cmd_concat(spec_path: str):
    with open(spec_path) as fh:
        spec = json.load(fh)

    frames = spec.get("frames", [])
    incomplete = [f for f in frames if f.get("status") != "completed"]
    if incomplete:
        names = ", ".join(f.get("name", "?") for f in incomplete)
        print(f"# ERROR: frames not yet completed: {names}", file=sys.stderr)
        sys.exit(1)

    for f in frames:
        url = f.get("video_url", "")
        if not url:
            print(f"# WARNING: no video_url for frame {f.get('name')}", file=sys.stderr)
            continue
        print(f"file '{url}'")

    print("# Pipe this to ffmpeg:")
    print("# ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4", file=sys.stderr)


def cmd_brief(video_type: str):
    if video_type not in TEMPLATE_STRUCTURES:
        print(f"Unknown type '{video_type}'. Choose from: {list(TEMPLATE_STRUCTURES)}", file=sys.stderr)
        sys.exit(1)

    frame_sequence = TEMPLATE_STRUCTURES[video_type]
    frames = []
    for ft in frame_sequence:
        limits = FRAME_TYPES[ft]
        frames.append({
            "name": ft.capitalize(),
            "frame_type": ft,
            "script": f"[Write your {ft} script here — max {limits['max_words']} words, ~{limits['max_seconds']}s. Job: {limits['job']}]",
            "engine": "avatar_iv",
            "motion_prompt": None,
            "background_color": "#0f0f0f",
            "status": "pending"
        })

    template = {
        "name": f"My {video_type.capitalize()} Campaign",
        "aspect_ratio": "9:16",
        "resolution": "1080p",
        "avatar_id": "<look_id from list_avatar_looks>",
        "voice_id": "<voice_id from list_voices or clone_voice>",
        "style_id": "<optional — from list_video_agent_styles>",
        "brand_kit_id": "<optional — from list_brand_kits>",
        "output_languages": [],
        "frames": frames
    }
    print(json.dumps(template, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="HeyGen Hyperframes campaign planner and tracker"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="Validate campaign.json and print execution plan")
    p_plan.add_argument("spec", help="Path to campaign JSON file")

    p_status = sub.add_parser("status", help="Show frame completion status")
    p_status.add_argument("spec", help="Path to campaign JSON file")
    p_status.add_argument("--json", action="store_true", dest="as_json", help="Machine-readable JSON output")

    p_concat = sub.add_parser("concat", help="Emit FFmpeg filelist.txt for completed frames")
    p_concat.add_argument("spec", help="Path to campaign JSON file")

    p_brief = sub.add_parser("brief", help="Generate a starter campaign.json template")
    p_brief.add_argument("--type", required=True, choices=list(TEMPLATE_STRUCTURES),
                         help="Video type: ad, explainer, demo, outreach, tutorial")

    args = parser.parse_args()

    if args.command == "plan":
        cmd_plan(args.spec)
    elif args.command == "status":
        cmd_status(args.spec, as_json=args.as_json)
    elif args.command == "concat":
        cmd_concat(args.spec)
    elif args.command == "brief":
        cmd_brief(args.type)


if __name__ == "__main__":
    main()
