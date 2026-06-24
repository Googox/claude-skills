#!/usr/bin/env python3
"""
Minimal Obsidian Filesystem MCP Server (Standard Library only)
Exposes Obsidian vault read/write as MCP tools over stdio.

Usage:
    python3 mcp_obsidian_fs.py --vault /path/to/vault
    python3 mcp_obsidian_fs.py --vault /path/to/vault --readonly

MCP tools exposed:
    read_note        - Read a note by path
    create_note      - Create or overwrite a note
    update_note      - Append or prepend content to a note
    list_notes       - List notes in a folder
    search_notes     - Fulltext search across vault
    list_tags        - Find all tags used in vault
    delete_note      - Delete a note (requires --allow-delete)
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


class ObsidianVault:
    def __init__(self, vault_path: str, readonly: bool = False, allow_delete: bool = False):
        self.root = Path(vault_path).resolve()
        self.readonly = readonly
        self.allow_delete = allow_delete
        if not self.root.exists():
            raise ValueError(f"Vault not found: {vault_path}")

    def _resolve(self, rel_path: str) -> Path:
        """Resolve a relative vault path safely (no path traversal)."""
        # Normalize and prevent traversal
        clean = Path(rel_path.lstrip("/"))
        full = (self.root / clean).resolve()
        if not str(full).startswith(str(self.root)):
            raise PermissionError(f"Path outside vault: {rel_path}")
        return full

    def read_note(self, path: str) -> dict:
        full = self._resolve(path)
        if not full.exists():
            return {"error": f"Note not found: {path}"}
        if not full.suffix == ".md":
            full = full.with_suffix(".md")
        if not full.exists():
            return {"error": f"Note not found: {path}"}
        return {"path": str(full.relative_to(self.root)), "content": full.read_text()}

    def create_note(self, path: str, content: str, overwrite: bool = False) -> dict:
        if self.readonly:
            return {"error": "Vault is in read-only mode"}
        full = self._resolve(path)
        if not full.suffix:
            full = full.with_suffix(".md")
        if full.exists() and not overwrite:
            return {"error": f"Note already exists: {path}. Use overwrite=true to replace."}
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        return {"path": str(full.relative_to(self.root)), "created": True}

    def update_note(self, path: str, content: str, mode: str = "append") -> dict:
        if self.readonly:
            return {"error": "Vault is in read-only mode"}
        full = self._resolve(path)
        if not full.suffix:
            full = full.with_suffix(".md")
        if not full.exists():
            return {"error": f"Note not found: {path}"}
        existing = full.read_text()
        if mode == "prepend":
            full.write_text(content + "\n" + existing)
        else:
            full.write_text(existing.rstrip() + "\n\n" + content)
        return {"path": str(full.relative_to(self.root)), "updated": True}

    def list_notes(self, folder: str = "", recursive: bool = True) -> dict:
        base = self._resolve(folder) if folder else self.root
        if not base.exists():
            return {"error": f"Folder not found: {folder}"}
        pattern = "**/*.md" if recursive else "*.md"
        notes = [str(p.relative_to(self.root)) for p in base.glob(pattern)]
        return {"folder": folder or "/", "notes": sorted(notes), "count": len(notes)}

    def search_notes(self, query: str, case_sensitive: bool = False) -> dict:
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(query, flags)
        except re.error:
            pattern = re.compile(re.escape(query), flags)

        for md_file in self.root.rglob("*.md"):
            try:
                text = md_file.read_text()
                matches = []
                for i, line in enumerate(text.splitlines(), 1):
                    if pattern.search(line):
                        matches.append({"line": i, "text": line.strip()})
                if matches:
                    results.append({
                        "path": str(md_file.relative_to(self.root)),
                        "matches": matches[:5],  # max 5 lines per file
                    })
            except (UnicodeDecodeError, PermissionError):
                continue

        return {"query": query, "results": results, "count": len(results)}

    def list_tags(self) -> dict:
        tag_pattern = re.compile(r"#([\w/\-]+)")
        tags: dict[str, int] = {}
        for md_file in self.root.rglob("*.md"):
            try:
                text = md_file.read_text()
                for tag in tag_pattern.findall(text):
                    tags[tag] = tags.get(tag, 0) + 1
            except (UnicodeDecodeError, PermissionError):
                continue
        sorted_tags = sorted(tags.items(), key=lambda x: -x[1])
        return {"tags": [{"tag": t, "count": c} for t, c in sorted_tags]}

    def delete_note(self, path: str) -> dict:
        if self.readonly:
            return {"error": "Vault is in read-only mode"}
        if not self.allow_delete:
            return {"error": "Delete not enabled. Restart with --allow-delete"}
        full = self._resolve(path)
        if not full.exists():
            return {"error": f"Note not found: {path}"}
        full.unlink()
        return {"path": path, "deleted": True}


class MCPServer:
    def __init__(self, vault: ObsidianVault):
        self.vault = vault
        self.tools = {
            "read_note": {
                "description": "Read a note from the Obsidian vault",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path to note (e.g. 'Daily Notes/2026-06-24.md')"}
                    },
                    "required": ["path"],
                },
            },
            "create_note": {
                "description": "Create a new note in the Obsidian vault",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Relative path for new note"},
                        "content": {"type": "string", "description": "Markdown content"},
                        "overwrite": {"type": "boolean", "description": "Overwrite if exists", "default": False},
                    },
                    "required": ["path", "content"],
                },
            },
            "update_note": {
                "description": "Append or prepend content to an existing note",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "mode": {"type": "string", "enum": ["append", "prepend"], "default": "append"},
                    },
                    "required": ["path", "content"],
                },
            },
            "list_notes": {
                "description": "List notes in the vault or a specific folder",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "folder": {"type": "string", "description": "Subfolder path (empty = root)", "default": ""},
                        "recursive": {"type": "boolean", "default": True},
                    },
                },
            },
            "search_notes": {
                "description": "Full-text search across all notes in the vault",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term or regex pattern"},
                        "case_sensitive": {"type": "boolean", "default": False},
                    },
                    "required": ["query"],
                },
            },
            "list_tags": {
                "description": "List all tags used in the vault with usage counts",
                "inputSchema": {"type": "object", "properties": {}},
            },
            "delete_note": {
                "description": "Delete a note from the vault (requires --allow-delete flag)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"],
                },
            },
        }

    def handle(self, request: dict) -> dict:
        method = request.get("method", "")
        req_id = request.get("id")
        params = request.get("params", {})

        def ok(result):
            return {"jsonrpc": "2.0", "id": req_id, "result": result}

        def err(code, msg):
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}

        if method == "initialize":
            return ok({
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "obsidian-fs-mcp", "version": "1.0.0"},
            })

        if method == "tools/list":
            return ok({"tools": [
                {"name": k, "description": v["description"], "inputSchema": v["inputSchema"]}
                for k, v in self.tools.items()
            ]})

        if method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            try:
                result = self._call_tool(tool_name, args)
                return ok({
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                })
            except Exception as e:
                return err(-32603, str(e))

        if method == "notifications/initialized":
            return None  # notification, no response

        return err(-32601, f"Method not found: {method}")

    def _call_tool(self, name: str, args: dict):
        v = self.vault
        if name == "read_note":
            return v.read_note(args["path"])
        if name == "create_note":
            return v.create_note(args["path"], args["content"], args.get("overwrite", False))
        if name == "update_note":
            return v.update_note(args["path"], args["content"], args.get("mode", "append"))
        if name == "list_notes":
            return v.list_notes(args.get("folder", ""), args.get("recursive", True))
        if name == "search_notes":
            return v.search_notes(args["query"], args.get("case_sensitive", False))
        if name == "list_tags":
            return v.list_tags()
        if name == "delete_note":
            return v.delete_note(args["path"])
        return {"error": f"Unknown tool: {name}"}

    def run(self):
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                request = json.loads(line.strip())
                response = self.handle(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break


def main():
    parser = argparse.ArgumentParser(description="Obsidian Filesystem MCP Server")
    parser.add_argument("--vault", required=True, help="Path to Obsidian vault")
    parser.add_argument("--readonly", action="store_true", help="Disallow write operations")
    parser.add_argument("--allow-delete", action="store_true", help="Enable note deletion")
    args = parser.parse_args()

    vault = ObsidianVault(args.vault, readonly=args.readonly, allow_delete=args.allow_delete)
    server = MCPServer(vault)
    server.run()


if __name__ == "__main__":
    main()
