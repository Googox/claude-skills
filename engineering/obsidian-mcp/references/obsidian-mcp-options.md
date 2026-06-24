# Obsidian MCP Server Options — Referenz

## Verfügbare MCP Server (Stand: 2026)

### 1. obsidian-mcp (npm)
- **Typ:** Filesystem (kein Plugin nötig)
- **Install:** `npm install -g obsidian-mcp`
- **Reife:** Community, aktiv gewartet
- **Tools:** read, write, search, list, delete
- **Config:**
  ```json
  { "command": "npx", "args": ["obsidian-mcp", "/vault/path"] }
  ```

### 2. mcp-obsidian (npm, REST API)
- **Typ:** HTTP via Local REST API Plugin
- **Install:** `npm install -g mcp-obsidian`
- **Vorteil:** Zugriff auf aktuell offene Datei in Obsidian
- **Nachteil:** Obsidian muss geöffnet sein
- **Config:**
  ```json
  {
    "command": "npx",
    "args": ["-y", "mcp-obsidian"],
    "env": { "OBSIDIAN_API_KEY": "key", "OBSIDIAN_HOST": "http://localhost:27123" }
  }
  ```

### 3. mcp_obsidian_fs.py (dieses Repo)
- **Typ:** Filesystem, Python Standard Library
- **Vorteil:** Kein npm nötig, vollständig auditierbar, offline
- **Tools:** read_note, create_note, update_note, list_notes, search_notes, list_tags, delete_note
- **Config:**
  ```json
  {
    "command": "python3",
    "args": ["scripts/mcp_obsidian_fs.py", "--vault", "/vault/path"]
  }
  ```

---

## Obsidian Local REST API Plugin

### Installation
1. Obsidian → Settings → Community Plugins → Browse
2. Suche: "Local REST API"
3. Install + Enable
4. API Key wird in Plugin-Einstellungen angezeigt

### Endpoints (Auswahl)
| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/vault/{filename}` | Datei lesen |
| PUT | `/vault/{filename}` | Datei schreiben |
| POST | `/vault/{filename}` | Datei anhängen |
| DELETE | `/vault/{filename}` | Datei löschen |
| GET | `/search/simple/?query=text` | Suche |
| GET | `/active/` | Aktive Datei |

### Ports
- HTTP: `27123` (Standard)
- HTTPS: `27124` (selbst-signiertes Zertifikat)

---

## Vergleich der Modi

| Kriterium | Filesystem | REST API |
|-----------|-----------|----------|
| Obsidian muss laufen | Nein | Ja |
| Plugin nötig | Nein | Ja (Local REST API) |
| Aktive Datei abrufen | Nein | Ja |
| Offline-fähig | Ja | Nein |
| Setup-Aufwand | Gering | Mittel |
| Sync-Konflikte | Möglich | Gering (Obsidian verwaltet) |

**Empfehlung:** Filesystem-Modus für die meisten Anwendungsfälle — einfacher, robuster, offline-fähig.

---

## Sicherheit

- MCP-Server laufen lokal (kein Cloud-Zugriff)
- API-Key nie in `.env` oder committed Settings eintragen
- Stattdessen: `settings.local.json` (in `.gitignore`)
- Für sensible Vaults: `--readonly` Flag nutzen
- Vault-Backup vor erster Nutzung empfohlen (Git, iCloud, Time Machine)
