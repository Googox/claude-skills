#!/usr/bin/env python3
"""PreToolUse gate: scan agent skills with NVIDIA SkillSpector before installation.

Fail closed: no scanner, unparsable target, scan error or high/critical finding -> deny.
Escape hatch (explicit, logged to stderr): SKILLSPECTOR_GATE_OFF=1.
"""
import json
import os
import re
import shutil
import subprocess
import sys

SKILL_DIRS = (".claude/skills", ".codex/skills", ".openclaw/skills", "/skills/")
INSTALL_HINTS = (
    r"\bgit\s+clone\b",
    r"\bnpx\s+skills\s+add\b",
    r"\bclaude\s+plugin\s+(install|add)\b",
    r"codex-install\.(sh|bat)",
    r"openclaw-install\.sh",
)
URL_RE = re.compile(r"(https?://\S+|git@\S+:\S+)")


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"SkillSpector-Gate: {reason}"}}))
    sys.exit(0)


def find_scanner():
    cands = [os.environ.get("SKILLSPECTOR_BIN", ""),
             os.path.expanduser("~/.skillspector/src/.venv/bin/skillspector"),
             shutil.which("skillspector") or ""]
    return next((c for c in cands if c and os.access(c, os.X_OK)), None)


def targets_for(cmd):
    """Return (targets, is_install). Targets are URLs or local paths to scan."""
    is_install = any(re.search(p, cmd) for p in INSTALL_HINTS)
    targets = [u.rstrip(";&|)\"'") for u in URL_RE.findall(cmd)] if is_install else []
    m = re.search(r"\b(cp|mv)\s+(-\S+\s+)*(\S+)\s+(\S+)\s*$", cmd)
    if m and any(d in m.group(4) for d in SKILL_DIRS):
        is_install, targets = True, [m.group(3)]
    return targets, is_install


def main():
    ev = json.load(sys.stdin)
    cmd = ev.get("tool_input", {}).get("command", "")
    targets, is_install = targets_for(cmd)
    if not is_install:
        return
    if os.environ.get("SKILLSPECTOR_GATE_OFF") == "1":
        print("SkillSpector-Gate: DEAKTIVIERT per SKILLSPECTOR_GATE_OFF", file=sys.stderr)
        return
    if not targets:
        deny("Installationsbefehl erkannt, aber kein scanbares Ziel (URL/Pfad) ableitbar. "
             "Erst manuell scannen: skillspector scan <ziel> --no-llm")
    scanner = find_scanner()
    if not scanner:
        deny("skillspector nicht installiert (fail closed). Installation: siehe .claude/hooks/README-skillspector.md")
    for t in targets:
        try:
            r = subprocess.run([scanner, "scan", t, "--no-llm", "--format", "json"],
                               capture_output=True, text=True, timeout=300)
        except (subprocess.TimeoutExpired, OSError) as e:
            deny(f"Scan von {t} fehlgeschlagen ({e.__class__.__name__}).")
        try:
            risk = json.loads(r.stdout)["risk_assessment"]
        except (ValueError, KeyError):
            deny(f"Scan von {t}: Ausgabe nicht lesbar (Exit {r.returncode}); blockiert. {r.stderr[:300]}")
        if risk.get("max_issue_severity") in ("HIGH", "CRITICAL") or risk.get("recommendation") == "DO_NOT_INSTALL":
            deny(f"{t}: {risk.get('recommendation')} (Score {risk.get('score')}, max {risk.get('max_issue_severity')}). "
                 f"Bericht: skillspector scan {t} --no-llm")
        if r.returncode != 0:
            deny(f"Scan von {t} Exit {r.returncode}; blockiert.")


if __name__ == "__main__":
    main()
