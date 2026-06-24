#!/usr/bin/env python3
"""
Obsidian MCP Setup Script
Generates Claude Code settings.json configuration for Obsidian MCP integration.
Usage:
    python3 setup_obsidian_mcp.py --vault /path/to/vault
    python3 setup_obsidian_mcp.py --vault /path/to/vault --mode rest --api-key YOUR_KEY
    python3 setup_obsidian_mcp.py --vault /path/to/vault --scope project
"""
import argparse
import json
import os
import platform
import sys
from pathlib import Path


def detect_vault_path() -> str | None:
    """Try to auto-detect common Obsidian vault locations."""
    system = platform.system()
    home = Path.home()

    candidates = []
    if system == "Darwin":
        candidates = [
            home / "Library/Mobile Documents/iCloud~md~obsidian/Documents",
            home / "Documents",
            home / "Obsidian",
        ]
    elif system == "Windows":
        candidates = [
            home / "Documents",
            home / "OneDrive/Documents",
        ]
    else:
        candidates = [
            home / "Documents",
            home / "Obsidian",
            home / "notes",
        ]

    for path in candidates:
        if path.exists():
            # Look for vault markers (.obsidian folder)
            for child in path.iterdir() if path.is_dir() else []:
                if (child / ".obsidian").exists():
                    return str(child)
    return None


def build_filesystem_config(vault_path: str) -> dict:
    return {
        "mcpServers": {
            "obsidian": {
                "command": "npx",
                "args": ["obsidian-mcp", vault_path],
            }
        }
    }


def build_rest_api_config(api_key: str, host: str = "http://localhost:27123") -> dict:
    return {
        "mcpServers": {
            "obsidian": {
                "command": "npx",
                "args": ["-y", "mcp-obsidian"],
                "env": {
                    "OBSIDIAN_API_KEY": api_key,
                    "OBSIDIAN_HOST": host,
                },
            }
        }
    }


def get_settings_path(scope: str) -> Path:
    if scope == "global":
        home = Path.home()
        system = platform.system()
        if system == "Windows":
            return home / "AppData/Roaming/Claude/settings.json"
        return home / ".claude/settings.json"
    return Path.cwd() / ".claude/settings.json"


def merge_into_settings(settings_path: Path, new_config: dict) -> dict:
    existing = {}
    if settings_path.exists():
        with open(settings_path) as f:
            existing = json.load(f)

    existing.setdefault("mcpServers", {})
    existing["mcpServers"].update(new_config.get("mcpServers", {}))
    return existing


def main():
    parser = argparse.ArgumentParser(
        description="Generate Claude Code MCP config for Obsidian"
    )
    parser.add_argument(
        "--vault",
        help="Path to Obsidian vault directory (auto-detected if omitted)",
    )
    parser.add_argument(
        "--mode",
        choices=["filesystem", "rest"],
        default="filesystem",
        help="Integration mode: filesystem (default) or rest (requires Local REST API plugin)",
    )
    parser.add_argument(
        "--api-key",
        help="Obsidian Local REST API key (required for --mode rest)",
    )
    parser.add_argument(
        "--host",
        default="http://localhost:27123",
        help="REST API host (default: http://localhost:27123)",
    )
    parser.add_argument(
        "--scope",
        choices=["global", "project"],
        default="global",
        help="Write to global ~/.claude/settings.json or project .claude/settings.json",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print config without writing to disk",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output raw JSON only (for piping)",
    )
    args = parser.parse_args()

    # Resolve vault path
    vault_path = args.vault
    if not vault_path and args.mode == "filesystem":
        vault_path = detect_vault_path()
        if vault_path:
            print(f"Auto-detected vault: {vault_path}", file=sys.stderr)
        else:
            print(
                "ERROR: Could not auto-detect vault. Use --vault /path/to/vault",
                file=sys.stderr,
            )
            sys.exit(1)

    if vault_path and not Path(vault_path).exists():
        print(f"ERROR: Vault path does not exist: {vault_path}", file=sys.stderr)
        sys.exit(1)

    # Build config
    if args.mode == "rest":
        if not args.api_key:
            print(
                "ERROR: --api-key required for --mode rest. "
                "Find it in Obsidian → Settings → Local REST API",
                file=sys.stderr,
            )
            sys.exit(1)
        config = build_rest_api_config(args.api_key, args.host)
    else:
        config = build_filesystem_config(vault_path)

    settings_path = get_settings_path(args.scope)

    if args.json_output:
        print(json.dumps(config, indent=2))
        return

    if args.dry_run:
        merged = merge_into_settings(settings_path, config)
        print(f"\n[DRY RUN] Would write to: {settings_path}\n")
        print(json.dumps(merged, indent=2))
        return

    # Write config
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    merged = merge_into_settings(settings_path, config)

    with open(settings_path, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

    print(f"\nObsidian MCP configured successfully!")
    print(f"Settings written to: {settings_path}")
    print(f"Mode: {args.mode}")
    if vault_path:
        print(f"Vault: {vault_path}")
    print("\nNext steps:")
    if args.mode == "filesystem":
        print("  1. npm install -g obsidian-mcp")
    else:
        print("  1. Ensure Obsidian is running with Local REST API plugin active")
    print("  2. Restart Claude Code")
    print('  3. Ask Claude: "Zeige mir alle Notizen in meinem Vault"')


if __name__ == "__main__":
    main()
