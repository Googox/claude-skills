#!/usr/bin/env python3
"""Diagnose the Obsidian Local REST API MCP connection for Claude clients.

Runs a bottom-up check of the connection chain and reports exactly which
layer fails: API reachability, authentication, MCP endpoint, client config.

The API key is never printed and never read from argv (which would leak it
into shell history). Supply it via the OBSIDIAN_API_KEY environment variable
or let the script prompt for it.

Usage:
    python3 diagnose-obsidian-mcp.py
    OBSIDIAN_API_KEY=... python3 diagnose-obsidian-mcp.py

Exit codes: 0 = a usable path was found, 1 = no usable path.
"""

import getpass
import json
import os
import platform
import shutil
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

HOST = "127.0.0.1"
HTTP_PORT = 27123
HTTPS_PORT = 27124
TIMEOUT = 5

OK = "[ OK ]"
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[INFO]"


def head(title):
    print("\n" + title)
    print("-" * len(title))


def port_open(host, port):
    """Return True if a TCP connect to host:port succeeds."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        return sock.connect_ex((host, port)) == 0


def request(url, key=None, method="GET", body=None, extra_headers=None, verify=True):
    """Perform an HTTP(S) request. Returns (status, headers, text) or raises."""
    headers = {}
    if key:
        headers["Authorization"] = "Bearer " + key
    if body is not None:
        headers["Content-Type"] = "application/json"
    if extra_headers:
        headers.update(extra_headers)

    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    context = None
    if url.startswith("https://"):
        if verify:
            context = ssl.create_default_context()
        else:
            # Loopback diagnosis only: the plugin serves a self-signed CA by
            # design, so an unverified probe answers "is the server alive?"
            # while the verified probe above answers "is the CA trusted?".
            context = ssl._create_unverified_context()

    with urllib.request.urlopen(req, timeout=TIMEOUT, context=context) as resp:
        return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")


def parse_jsonrpc(text, content_type):
    """Extract a JSON-RPC payload from a plain or SSE-framed response body."""
    if "text/event-stream" in (content_type or ""):
        for line in text.splitlines():
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def check_transport(label, base, key, verify=True):
    """Check one transport: reachability, auth, MCP endpoint, tool list."""
    result = {"base": base, "reachable": False, "authenticated": False,
              "mcp": False, "tools": [], "tls_trusted": None}

    try:
        status, _, text = request(base + "/", verify=verify)
        result["reachable"] = True
        if verify and base.startswith("https://"):
            result["tls_trusted"] = True
        print(f"{OK} {label}: API reachable (HTTP {status})")
    except ssl.SSLError as exc:
        result["tls_trusted"] = False
        print(f"{FAIL} {label}: TLS verification failed ({exc.reason if hasattr(exc, 'reason') else exc})")
        return result
    except urllib.error.HTTPError as exc:
        result["reachable"] = True
        print(f"{OK} {label}: API reachable (HTTP {exc.code})")
    except Exception as exc:
        print(f"{FAIL} {label}: not reachable ({type(exc).__name__}: {exc})")
        return result

    if not key:
        print(f"{WARN} {label}: no API key supplied, skipping auth check")
        return result

    try:
        _, _, text = request(base + "/", key=key, verify=verify)
        payload = json.loads(text) if text.strip().startswith("{") else {}
        if payload.get("authenticated") is True:
            result["authenticated"] = True
            print(f"{OK} {label}: API key accepted")
        else:
            print(f"{FAIL} {label}: API key rejected (authenticated={payload.get('authenticated')})")
            return result
    except Exception as exc:
        print(f"{FAIL} {label}: auth check failed ({type(exc).__name__}: {exc})")
        return result

    init = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "gstack-obsidian-diag", "version": "1.0"}},
    }
    accept = {"Accept": "application/json, text/event-stream"}
    try:
        _, hdrs, text = request(base + "/mcp/", key=key, method="POST",
                                body=init, extra_headers=accept, verify=verify)
        payload = parse_jsonrpc(text, hdrs.get("Content-Type"))
        server = (payload or {}).get("result", {}).get("serverInfo", {})
        if server:
            result["mcp"] = True
            print(f"{OK} {label}: MCP endpoint alive "
                  f"(server: {server.get('name', '?')} {server.get('version', '')})")
        else:
            print(f"{FAIL} {label}: MCP endpoint answered but sent no serverInfo")
            return result
        session = hdrs.get("Mcp-Session-Id") or hdrs.get("mcp-session-id")
    except urllib.error.HTTPError as exc:
        print(f"{FAIL} {label}: MCP endpoint returned HTTP {exc.code} "
              f"(plugin too old, or /mcp/ disabled)")
        return result
    except Exception as exc:
        print(f"{FAIL} {label}: MCP endpoint check failed ({type(exc).__name__}: {exc})")
        return result

    sess_headers = dict(accept)
    if session:
        sess_headers["Mcp-Session-Id"] = session
    try:
        request(base + "/mcp/", key=key, method="POST", verify=verify,
                body={"jsonrpc": "2.0", "method": "notifications/initialized"},
                extra_headers=sess_headers)
    except Exception:
        pass  # Optional handshake step; some servers do not require it.

    try:
        _, hdrs, text = request(base + "/mcp/", key=key, method="POST", verify=verify,
                                body={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                                extra_headers=sess_headers)
        payload = parse_jsonrpc(text, hdrs.get("Content-Type"))
        tools = (payload or {}).get("result", {}).get("tools", [])
        result["tools"] = [t.get("name", "?") for t in tools]
        if tools:
            print(f"{OK} {label}: {len(tools)} tools exposed")
    except Exception as exc:
        print(f"{WARN} {label}: tool list unavailable ({type(exc).__name__})")

    return result


def desktop_config_path():
    system = platform.system()
    home = os.path.expanduser("~")
    if system == "Darwin":
        return os.path.join(home, "Library", "Application Support", "Claude",
                            "claude_desktop_config.json")
    if system == "Windows":
        return os.path.join(os.environ.get("APPDATA", home), "Claude",
                            "claude_desktop_config.json")
    return os.path.join(home, ".config", "Claude", "claude_desktop_config.json")


def check_desktop_config():
    """Inspect claude_desktop_config.json for the stdio-only violation."""
    path = desktop_config_path()
    if not os.path.exists(path):
        print(f"{INFO} No Claude Desktop config at {path}")
        return
    print(f"{INFO} Claude Desktop config: {path}")
    try:
        with open(path, encoding="utf-8") as handle:
            config = json.load(handle)
    except json.JSONDecodeError as exc:
        print(f"{FAIL} Config is not valid JSON ({exc}). Claude Desktop ignores it entirely.")
        return
    except OSError as exc:
        print(f"{WARN} Could not read config ({exc})")
        return

    servers = config.get("mcpServers", {})
    if not servers:
        print(f"{WARN} Config has no mcpServers entries")
        return

    for name, entry in servers.items():
        if not isinstance(entry, dict):
            continue
        if "url" in entry or entry.get("type") in ("http", "sse"):
            print(f"{FAIL} Server '{name}' uses a URL/http entry. "
                  f"claude_desktop_config.json launches stdio processes only, "
                  f"so this entry never connects. THIS IS THE BUG.")
        elif "command" in entry:
            print(f"{OK} Server '{name}' is a stdio entry (command: {entry['command']})")


def check_tooling():
    """Report which client paths are even installable on this machine."""
    for binary, why in (("uvx", "required for the stdio path (Claude Desktop)"),
                        ("uv", "provides uvx"),
                        ("claude", "Claude Code CLI, native HTTP transport"),
                        ("python3", "runtime")):
        found = shutil.which(binary)
        print(f"{OK if found else WARN} {binary}: {found or 'not found'} ({why})")

    if shutil.which("claude"):
        try:
            out = subprocess.run(["claude", "mcp", "list"], capture_output=True,
                                 text=True, timeout=20)
            body = (out.stdout or out.stderr).strip()
            if body:
                print(f"\n{INFO} claude mcp list:")
                for line in body.splitlines()[:15]:
                    print("      " + line)
        except Exception as exc:
            print(f"{WARN} 'claude mcp list' failed ({type(exc).__name__})")


def main():
    print("Obsidian MCP connection diagnosis")
    print("=" * 33)
    print(f"{INFO} Platform: {platform.system()} {platform.release()}")

    key = os.environ.get("OBSIDIAN_API_KEY", "").strip()
    if not key and sys.stdin.isatty():
        key = getpass.getpass("Obsidian API key (hidden, not stored): ").strip()
    if key:
        print(f"{INFO} API key supplied ({len(key)} chars, value never printed)")
    else:
        print(f"{WARN} No API key: auth and MCP checks will be skipped")

    head("Step 1: is Obsidian listening?")
    http_up = port_open(HOST, HTTP_PORT)
    https_up = port_open(HOST, HTTPS_PORT)
    print(f"{OK if http_up else FAIL} TCP {HOST}:{HTTP_PORT} (HTTP)")
    print(f"{OK if https_up else FAIL} TCP {HOST}:{HTTPS_PORT} (HTTPS)")
    if not http_up and not https_up:
        print(f"{FAIL} Neither port is open. Obsidian is closed, the Local REST API "
              f"plugin is disabled, or it binds a different port.")
        print(f"{INFO} Continuing with the client-side checks anyway: a broken client "
              f"config is diagnosable without a running vault.")
    if http_up and not https_up:
        pass
    elif not http_up and https_up:
        print(f"{INFO} HTTP port closed. Enable it under "
              f"Settings > Local REST API > Enable HTTP server to drop TLS from the equation.")


    results = {}
    if http_up:
        head("Step 2: HTTP transport (no TLS)")
        results["http"] = check_transport("http", f"http://{HOST}:{HTTP_PORT}", key)
    if https_up:
        head("Step 3: HTTPS transport, certificate verified")
        results["https_verified"] = check_transport(
            "https (verified)", f"https://{HOST}:{HTTPS_PORT}", key, verify=True)
        if results["https_verified"]["tls_trusted"] is False:
            print(f"{INFO} The plugin CA is not trusted by this machine. Download it from "
                  f"https://{HOST}:{HTTPS_PORT}/obsidian-local-rest-api.crt and trust it, "
                  f"or use the HTTP port.")
            head("Step 3b: HTTPS transport, verification bypassed (probe only)")
            results["https_unverified"] = check_transport(
                "https (unverified)", f"https://{HOST}:{HTTPS_PORT}", key, verify=False)

    head("Step 4: Claude Desktop config")
    check_desktop_config()

    head("Step 5: local tooling")
    check_tooling()

    head("Verdict")
    working = [name for name, res in results.items() if res.get("mcp")]
    if not results:
        print(f"{FAIL} Obsidian was not reachable on either port, so the transport chain "
              f"could not be tested. Open Obsidian, confirm Settings > Local REST API is "
              f"enabled, then re-run. Any client-config problem flagged above is real "
              f"regardless and worth fixing now.")
        return 1
    if not working:
        authed = [n for n, r in results.items() if r.get("authenticated")]
        if authed:
            print(f"{FAIL} API and key are fine, but no MCP endpoint answered. "
                  f"Update the Local REST API plugin: the built-in /mcp/ server is "
                  f"a recent addition. Fall back to the stdio path (uvx mcp-obsidian), "
                  f"which only needs the REST API.")
        else:
            print(f"{FAIL} No transport completed authentication. Re-copy the API key from "
                  f"Settings > Local REST API (watch for trailing whitespace).")
        return 1

    best = "http" if "http" in working else working[0]
    base = results[best]["base"]
    tools = results[best]["tools"]
    print(f"{OK} Usable transport: {base}/mcp/ ({len(tools)} tools)")
    if tools:
        print(f"{INFO} Tools: {', '.join(sorted(tools))}")

    print(f"\n{INFO} Claude Code CLI (native HTTP, run once):")
    print(f'      claude mcp add --transport http --scope user \\')
    print(f'        obsidian {base}/mcp/ \\')
    print(f'        --header "Authorization: Bearer $OBSIDIAN_API_KEY"')

    print(f"\n{INFO} Claude Desktop (stdio only, add to {desktop_config_path()}):")
    port = HTTP_PORT if best == "http" else HTTPS_PORT
    snippet = {"mcpServers": {"obsidian": {
        "command": "uvx", "args": ["mcp-obsidian"],
        "env": {"OBSIDIAN_API_KEY": "<your key>",
                "OBSIDIAN_HOST": HOST, "OBSIDIAN_PORT": str(port)}}}}
    for line in json.dumps(snippet, indent=2).splitlines():
        print("      " + line)
    if not shutil.which("uvx"):
        print(f"{WARN} uvx is missing. Install uv first: https://docs.astral.sh/uv/")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(130)
