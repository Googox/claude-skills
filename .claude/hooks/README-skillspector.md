# SkillSpector-Gate

`skillspector-gate.py` läuft als `PreToolUse`-Hook auf `Bash` und scannt Skills mit
[NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector) (Apache-2.0), bevor sie installiert werden.

## Installation des Scanners (einmalig, manuell)

```bash
git clone https://github.com/NVIDIA/SkillSpector.git ~/.skillspector/src
cd ~/.skillspector/src && uv venv .venv && . .venv/bin/activate && make install
.venv/bin/skillspector scan ./some-skill/ --no-llm
```

Alternativ `SKILLSPECTOR_BIN=/pfad/zu/skillspector` setzen.

## Verhalten

- Erkannt: `git clone`, `npx skills add`, `claude plugin install`, `codex-install`/`openclaw-install`, `cp`/`mv` nach `*/skills/`.
- Blockiert bei: fehlendem Scanner, Scanfehler, Exit != 0, Findings high/critical.
- Notausgang: `SKILLSPECTOR_GATE_OFF=1` (bewusst, wird geloggt).

## Offene Punkte (vor Produktivnutzung prüfen)

- Verifiziert (SkillSpector 11c8b48): harmloser Skill = Exit 0, `SAFE`; präparierter Dummy = Exit 1, `DO_NOT_INSTALL`.
  Das Gate liest `risk_assessment` aus dem JSON. Ändert sich das Schema, blockiert es (fail closed).
- Mittlere Schwere (MEDIUM) lässt das Gate durch, solange der Exit-Code 0 ist.
- Lücke: manuelle Installationen im eigenen Terminal umgehen den Hook.
