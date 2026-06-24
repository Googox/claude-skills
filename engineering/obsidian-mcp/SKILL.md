# Obsidian MCP Integration

**Tier:** POWERFUL  
**Category:** Engineering  
**Domain:** AI / Knowledge Management  

---

## Overview

Verbinde Claude Code mit deinem Obsidian-Vault über das Model Context Protocol (MCP). Claude kann damit Notizen lesen, erstellen, durchsuchen und verknüpfen — direkt aus dem Terminal oder IDE, ohne Obsidian manuell zu öffnen.

**Zwei Integrationsmodi:**
- **Filesystem-Modus** — Claude liest/schreibt direkt im Vault-Verzeichnis (kein Plugin nötig)
- **REST API-Modus** — Claude kommuniziert mit Obsidian über das Local REST API Plugin (Obsidian muss laufen)

---

## Core Capabilities

- **Notizen erstellen** — neue `.md`-Dateien mit YAML-Frontmatter im Vault anlegen
- **Notizen lesen & durchsuchen** — Volltext-Suche über den gesamten Vault
- **Backlinks erzeugen** — `[[Wiki-Links]]` zwischen Notizen einfügen
- **Daily Notes** — Tagesnotizen erstellen und befüllen
- **Vault-Struktur analysieren** — Ordner, Tags, verwaiste Notizen finden
- **Templates anwenden** — Obsidian-Templates auf neue Notizen anwenden

---

## When to Use

- Notizen aus Claude-Gesprächen direkt in Obsidian speichern
- Wissen aus dem Vault als Kontext für Claude-Aufgaben nutzen
- Automatisch strukturierte Notizen (Meeting-Protokolle, Code-Docs, Research) erstellen
- Vault-Wartung: doppelte Notizen finden, verwaiste Links aufräumen
- PKM-Workflows (Personal Knowledge Management) automatisieren

---

## Setup: Variante A — Filesystem MCP (empfohlen, kein Plugin nötig)

### Schritt 1: MCP Server installieren

```bash
# Option 1: obsidian-mcp (npm, empfohlen)
npm install -g obsidian-mcp

# Option 2: mcp-obsidian-fs (Python, Standard-Library only)
# Kein Install nötig — Script liegt in scripts/mcp_obsidian_fs.py
python3 engineering/obsidian-mcp/scripts/mcp_obsidian_fs.py --vault /pfad/zu/vault
```

### Schritt 2: Claude Code konfigurieren

Füge in `~/.claude/settings.json` (global) oder `.claude/settings.json` (Projekt) hinzu:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["obsidian-mcp", "/pfad/zu/deinem/vault"]
    }
  }
}
```

**Vault-Pfade nach Betriebssystem:**
- macOS: `/Users/deinname/Library/Mobile Documents/iCloud~md~obsidian/Documents/VaultName`
- macOS (lokal): `/Users/deinname/Documents/ObsidianVault`
- Windows: `C:\\Users\\deinname\\Documents\\ObsidianVault`
- Linux: `/home/deinname/ObsidianVault`

### Schritt 3: Testen

```bash
# Claude Code neu starten, dann:
claude
# In Claude: "Zeige mir alle Notizen in meinem Vault"
```

---

## Setup: Variante B — Local REST API Plugin

### Schritt 1: Obsidian Plugin installieren

1. Obsidian öffnen → Einstellungen → Community Plugins → Durchsuchen
2. **"Local REST API"** suchen und installieren
3. Plugin aktivieren → API-Schlüssel kopieren (erscheint in Plugin-Einstellungen)
4. Standard-Port: `27123`

### Schritt 2: Claude Code konfigurieren

```json
{
  "mcpServers": {
    "obsidian-api": {
      "command": "npx",
      "args": ["-y", "mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "dein-api-schluessel-hier",
        "OBSIDIAN_HOST": "http://localhost:27123"
      }
    }
  }
}
```

### Schritt 3: HTTPS für REST API (optional)

Das Local REST API Plugin erstellt ein selbst-signiertes Zertifikat. Für lokale Nutzung HTTP verwenden oder dem Zertifikat vertrauen:

```json
{
  "env": {
    "OBSIDIAN_API_KEY": "dein-key",
    "OBSIDIAN_HOST": "https://localhost:27124",
    "NODE_EXTRA_CA_CERTS": "/pfad/zu/obsidian-cert.crt"
  }
}
```

---

## Workflow 1: Notizen aus Claude-Gespräch speichern

```
Du: "Erstelle eine Notiz über das Meeting mit dem Frontend-Team. 
     Themen: React Migration, TypeScript strict mode, Q3 Deadlines."

Claude: [Erstellt /Meetings/2026-06-24-Frontend-Team.md mit YAML-Frontmatter,
         Zusammenfassung und Tags]
```

**Ergebnis-Template** (`assets/meeting-note.md`):
```markdown
---
date: 2026-06-24
type: meeting
participants: [Frontend-Team]
tags: [meeting, react, typescript]
---

# Meeting: Frontend-Team — 2026-06-24

## Themen
- React Migration
- TypeScript strict mode
- Q3 Deadlines

## Entscheidungen
...

## Action Items
- [ ] ...
```

---

## Workflow 2: Vault als Kontext für Recherche

```
Du: "Suche in meinem Vault nach allem über 'MCP' und fasse zusammen,
     was ich bereits darüber weiß."

Claude: [Liest alle relevanten Notizen, gibt strukturierte Zusammenfassung]
```

---

## Workflow 3: Daily Note befüllen

```
Du: "Füge zu meiner heutigen Daily Note hinzu: 
     Obsidian MCP Integration abgeschlossen."

Claude: [Öffnet /Daily Notes/2026-06-24.md oder erstellt sie,
         fügt Eintrag unter ## Done hinzu]
```

---

## Workflow 4: Vault-Wartung

```
Du: "Finde alle Notizen ohne Tags und ohne Backlinks in meinem Vault."

Claude: [Scannt Vault, listet verwaiste Notizen mit Pfaden auf]
```

---

## Verfügbare MCP Tools (nach Server-Typ)

### obsidian-mcp (Filesystem)

| Tool | Beschreibung |
|------|-------------|
| `read_note` | Notiz-Inhalt lesen |
| `create_note` | Neue `.md`-Datei erstellen |
| `update_note` | Bestehende Notiz aktualisieren |
| `list_notes` | Notizen in einem Ordner auflisten |
| `search_notes` | Volltext-Suche im Vault |
| `delete_note` | Notiz löschen |
| `list_tags` | Alle Tags im Vault |

### mcp-obsidian (REST API)

| Tool | Beschreibung |
|------|-------------|
| `obsidian_get_file` | Datei per Pfad lesen |
| `obsidian_put_file` | Datei schreiben |
| `obsidian_search` | Omnisearch-Suche |
| `obsidian_list_directory` | Verzeichnis auflisten |
| `obsidian_get_active_file` | Aktuell offene Datei in Obsidian |
| `obsidian_open_file` | Datei in Obsidian öffnen |

---

## Sicherheitshinweise

- **Vault-Pfad schützen:** Der MCP-Server hat Schreibzugriff auf alle Vault-Dateien
- **API-Schlüssel:** Niemals in `.env`-Dateien committen — in `settings.local.json` ablegen
- **Backup:** Vor dem ersten Einsatz Vault sichern (z.B. via Git oder iCloud)
- **Scope begrenzen:** Für sensible Vaults Read-Only-Mode nutzen (siehe `scripts/`)

---

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| `MCP server not found` | `npm install -g obsidian-mcp` erneut ausführen |
| `Permission denied` | Vault-Pfad und Zugriffsrechte prüfen |
| `REST API connection refused` | Obsidian muss geöffnet sein, Plugin aktiv |
| `SSL certificate error` | HTTP statt HTTPS verwenden: `http://localhost:27123` |
| `Vault path not found` | Absoluten Pfad ohne `~` verwenden |

---

## Erfolgsmetriken

- **Setup-Zeit:** < 5 Minuten für Filesystem-Variante
- **Latenz:** < 200ms für Lese-Operationen (lokal)
- **Zuverlässigkeit:** Funktioniert offline (Filesystem-Variante)
- **Vault-Kompatibilität:** Alle Obsidian-Vault-Versionen unterstützt

---

## Referenzen

- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [Obsidian Local REST API Plugin](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [obsidian-mcp npm package](https://www.npmjs.com/package/obsidian-mcp)
- Konfigurationsbeispiele: `assets/settings-examples/`
- Setup-Script: `scripts/setup_obsidian_mcp.py`
