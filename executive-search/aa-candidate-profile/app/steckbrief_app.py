#!/usr/bin/env python3
"""A/A Steckbrief-Arbeitsplatz, lokale Anwendung.

Laeuft ausschliesslich auf 127.0.0.1. Lebenslauf, Zuordnungstabelle und
fertiger Steckbrief bleiben auf diesem Rechner. Verlaesst Text den
Rechner (optionaler API-Modus), dann nur pseudonymisiert, und nur wenn
die Rueckstandspruefung sauber ist.

Start:
    python steckbrief_app.py
    python steckbrief_app.py --port 8731 --kein-browser

Nur Standardbibliothek, Python 3.8+.
"""

import argparse
import base64
import json
import os
import secrets
import subprocess
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
sys.path.insert(0, os.path.join(os.path.dirname(HIER), "scripts"))

import cv_extract                      # noqa: E402
import docx_writer                     # noqa: E402
import llm_client                      # noqa: E402
import pseudonymize                    # noqa: E402
import steckbrief_build                # noqa: E402

TOKEN = secrets.token_urlsafe(24)
AUSGABE_WURZEL = os.path.join(os.path.expanduser("~"), "Documents", "AA-Steckbriefe")
KONFIG_PFAD = os.path.join(os.path.expanduser("~"), ".aa-steckbrief", "config.json")

PROMPT_VORLAGE = """Du arbeitest als Research-Unterstuetzung fuer A/A Executive Search.

Aufgabe: Wandle den folgenden pseudonymisierten Lebenslauf in ein strukturiertes
Kandidatenprofil im JSON-Format um.

Harte Regeln:
1. Erfinde nichts. Keine Zahl, kein Titel, kein Erfolg, der nicht im Text steht.
   Fehlt eine Angabe, setze ein offenes Feld in doppelten eckigen Klammern mit
   einer konkreten Ausfuellanweisung, zum Beispiel [[Umsatz und Ergebnis ergaenzen]]
   oder [[Fuehrungsspanne ergaenzen: direkt / gesamt]]. Solche Felder werden im
   Word-Dokument gruen hinterlegt. Schreibe niemals "nicht angegeben" als Fliesstext.
   Ein Feld, fuer das es keine Angabe gibt, laesst du im JSON leer; der Generator
   setzt das gruene Feld dann selbst.
2. Platzhalter in eckigen Klammern wie [KANDIDAT_1] oder [ARBEITGEBER_2] bleiben
   unveraendert stehen. Ersetze sie nicht und rate nicht, wer dahintersteckt.
3. Die Executive Summary hat genau fuenf Saetze in dieser Reihenfolge:
   berufliche Identitaet, staerkster Beleg mit Zahl, zweite tragende Kompetenz,
   Wechselgrund, groesster Vorbehalt offen benannt.
4. Beschoenige nicht. Kurze Verweildauern, Luecken ueber drei Monate und fehlende
   Belege gehoeren in "risiken", nicht in schoene Formulierungen.
5. Keine Angaben zu Geburtsdatum, Foto, Familienstand, Kindern, Staatsangehoerigkeit,
   Religion, Gesundheit, Behinderung. Diese Felder existieren im Schema nicht.
6. Antworte ausschliesslich mit dem JSON-Objekt, ohne Vor- und Nachtext.

JSON-Schema:
{SCHEMA}

Mandatsdaten (uebernimm sie unveraendert in "mandat"):
{MANDAT}

Pseudonymisierter Lebenslauf:
{LEBENSLAUF}

Zusaetzliche Notizen aus dem Interview (koennen leer sein):
{NOTIZEN}
"""

SCHEMA_KURZ = """{
  "mandat": {"position": "", "auftraggeber": "", "profil_id": "", "datum": "", "berater": "", "modus": "vollprofil"},
  "freigabe": {"einwilligung_dokumentiert": true, "einwilligung_datum": ""},
  "kandidat": {"name": "", "wohnregion": "", "mobilitaet": "", "sprachen": [], "fuehrungsspanne": "", "ergebnisverantwortung": "", "verfuegbarkeit": "", "kuendigungsfrist": ""},
  "summary": ["", "", "", "", ""],
  "werdegang": [{"von": "MM.JJJJ", "bis": "MM.JJJJ", "unternehmen": "", "unternehmenstyp": "", "groesse": "", "rolle": "", "verantwortung": "", "ergebnisse": []}],
  "luecken": [],
  "kompetenzen": {"fachlich": [], "fuehrung": [], "branche": []},
  "passung": [{"anforderung": "", "status": "erfuellt | teilweise erfuellt | nicht erfuellt", "beleg": ""}],
  "assessment": null,
  "motivation": "",
  "risiken": [],
  "offene_fragen": [],
  "empfehlung": {"votum": "", "begruendung": ""}
}"""


def json_antwort(handler, nutzlast, status=200):
    koerper = json.dumps(nutzlast, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(koerper)))
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.end_headers()
    handler.wfile.write(koerper)


def fallordner(profil_id):
    sicher = "".join(c for c in (profil_id or "ohne-id") if c.isalnum() or c in "-_") or "ohne-id"
    pfad = os.path.join(AUSGABE_WURZEL, sicher)
    os.makedirs(pfad, exist_ok=True)
    return pfad


def json_aus_antwort(text):
    """Holt das JSON-Objekt aus einer Modellantwort, auch mit Code-Zaun."""
    roh = (text or "").strip()
    if roh.startswith("```"):
        roh = roh.split("\n", 1)[1] if "\n" in roh else roh
        if roh.rstrip().endswith("```"):
            roh = roh.rstrip()[:-3]
    start, ende = roh.find("{"), roh.rfind("}")
    if start == -1 or ende <= start:
        raise ValueError("In der Antwort steht kein JSON-Objekt.")
    return json.loads(roh[start:ende + 1])


def mail_entwurf(dateipfad, empfaenger, betreff, text):
    """Oeffnet einen Mailentwurf. Speichert keine Zugangsdaten."""
    meldungen = []
    try:
        import win32com.client  # type: ignore
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = empfaenger or ""
        mail.Subject = betreff or ""
        mail.Body = text or ""
        if dateipfad and os.path.exists(dateipfad):
            mail.Attachments.Add(os.path.abspath(dateipfad))
        mail.Display()
        return True, "Outlook-Entwurf mit Anhang geoeffnet. Bitte pruefen und senden."
    except Exception as err:            # noqa: BLE001 - jeder Fehler faellt auf den Standardweg zurueck
        meldungen.append("Outlook nicht angesteuert (%s)." % type(err).__name__)

    ordner = os.path.dirname(os.path.abspath(dateipfad)) if dateipfad else AUSGABE_WURZEL
    try:
        if os.name == "nt":
            subprocess.Popen(["explorer", "/select,", os.path.abspath(dateipfad)])
        else:
            subprocess.Popen(["xdg-open", ordner])
        meldungen.append("Ordner mit der Datei geoeffnet.")
    except Exception:                   # noqa: BLE001
        meldungen.append("Ordner konnte nicht geoeffnet werden: %s" % ordner)

    ziel = "mailto:%s?subject=%s&body=%s" % (
        urllib.parse.quote(empfaenger or ""),
        urllib.parse.quote(betreff or ""),
        urllib.parse.quote((text or "") + "\n\nAnhang bitte manuell anfuegen: "
                           + os.path.abspath(dateipfad or "")))
    try:
        webbrowser.open(ziel)
        meldungen.append("Mailentwurf im Standardclient geoeffnet, Anhang manuell anfuegen.")
    except Exception:                   # noqa: BLE001
        meldungen.append("Mailclient konnte nicht geoeffnet werden.")
    return True, " ".join(meldungen)


class Handler(BaseHTTPRequestHandler):
    server_version = "AASteckbrief/1.0"

    def log_message(self, format, *args):       # noqa: A002
        sys.stderr.write("%s %s\n" % (self.address_string(), format % args))

    def _token_ok(self):
        kopf = self.headers.get("X-AA-Token", "")
        if kopf and secrets.compare_digest(kopf, TOKEN):
            return True
        abfrage = urllib.parse.urlparse(self.path).query
        wert = urllib.parse.parse_qs(abfrage).get("t", [""])[0]
        return bool(wert) and secrets.compare_digest(wert, TOKEN)

    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost", "[::1]", "::1")

    def do_GET(self):                            # noqa: N802
        if not self._host_ok():
            return json_antwort(self, {"fehler": "Nur lokaler Zugriff."}, 403)
        pfad = urllib.parse.urlparse(self.path).path
        if pfad in ("/", "/index.html"):
            if not self._token_ok():
                return json_antwort(self, {"fehler": "Token fehlt. Bitte die im Terminal "
                                                     "angezeigte Adresse verwenden."}, 403)
            koerper = OBERFLAECHE.replace("__TOKEN__", TOKEN).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(koerper)))
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; style-src 'unsafe-inline'; "
                             "script-src 'unsafe-inline'; connect-src 'self'")
            self.end_headers()
            return self.wfile.write(koerper)
        return json_antwort(self, {"fehler": "Nicht gefunden."}, 404)

    def do_POST(self):                           # noqa: N802
        if not self._host_ok():
            return json_antwort(self, {"fehler": "Nur lokaler Zugriff."}, 403)
        if not self._token_ok():
            return json_antwort(self, {"fehler": "Token ungueltig."}, 403)
        laenge = int(self.headers.get("Content-Length") or 0)
        if laenge > 40 * 1024 * 1024:
            return json_antwort(self, {"fehler": "Anfrage zu gross."}, 413)
        try:
            daten = json.loads(self.rfile.read(laenge).decode("utf-8") or "{}")
        except ValueError as err:
            return json_antwort(self, {"fehler": "Anfrage nicht lesbar: %s" % err}, 400)

        pfad = urllib.parse.urlparse(self.path).path
        aktionen = {
            "/api/extract": self.a_extract,
            "/api/prompt": self.a_prompt,
            "/api/llm": self.a_llm,
            "/api/build": self.a_build,
            "/api/export": self.a_export,
            "/api/mail": self.a_mail,
        }
        aktion = aktionen.get(pfad)
        if not aktion:
            return json_antwort(self, {"fehler": "Unbekannter Endpunkt."}, 404)
        try:
            return json_antwort(self, aktion(daten))
        except Exception as err:                 # noqa: BLE001
            return json_antwort(self, {"fehler": "%s: %s" % (type(err).__name__, err)}, 400)

    # Endpunkte

    def a_extract(self, daten):
        rohdaten = base64.b64decode(daten.get("inhalt_base64") or "")
        text = cv_extract.aus_datei(daten.get("dateiname") or "", rohdaten)
        return {"text": text, "entitaeten": cv_extract.entitaeten_vorschlag(text)}

    def a_prompt(self, daten):
        text = daten.get("text") or ""
        notizen = daten.get("notizen") or ""
        kandidat = (daten.get("kandidat") or "").strip()
        arbeitgeber = [a for a in (daten.get("arbeitgeber") or []) if a.strip()]
        orte = [o for o in (daten.get("orte") or []) if o.strip()]
        mandat = daten.get("mandat") or {}

        pseudo_lebenslauf, mapping = pseudonymize.pseudonymisieren(
            text, kandidat, arbeitgeber, orte)
        pseudo_notizen, mapping = pseudonymize.pseudonymisieren(
            notizen, kandidat, arbeitgeber, orte, mapping)

        prompt = (PROMPT_VORLAGE
                  .replace("{SCHEMA}", SCHEMA_KURZ)
                  .replace("{MANDAT}", json.dumps(mandat, ensure_ascii=False, indent=2))
                  .replace("{LEBENSLAUF}", pseudo_lebenslauf)
                  .replace("{NOTIZEN}", pseudo_notizen or "keine"))
        # Berater und Auftraggeber stehen legitim im Mandatskopf und sind keine
        # Kandidatendaten. Sie sind von der Rueckstandspruefung ausgenommen.
        ausnahmen = [str(mandat.get("berater") or ""), str(mandat.get("auftraggeber") or "")]
        rest = pseudonymize.restbestand(prompt, kandidat, arbeitgeber, orte, ausnahmen)
        return {"prompt": prompt, "mapping": mapping.as_dict(), "rest": rest,
                "sauber": not rest, "ausnahmen": [x for x in ausnahmen if x]}

    def a_llm(self, daten):
        prompt = daten.get("prompt") or ""
        schluessel = llm_client.schluessel_lesen(KONFIG_PFAD)
        if not schluessel:
            return {"fehler": "Kein API-Schluessel hinterlegt. Zwischenablage-Modus nutzen "
                              "oder ANTHROPIC_API_KEY setzen."}
        antwort = llm_client.frage(
            prompt, schluessel,
            modell=daten.get("modell") or llm_client.STANDARD_MODELL,
            kandidat_name=daten.get("kandidat") or "",
            arbeitgeber=daten.get("arbeitgeber") or [],
            orte=daten.get("orte") or [],
            ausnahmen=daten.get("ausnahmen") or [])
        return {"antwort": antwort}

    def a_build(self, daten):
        profil = json_aus_antwort(daten.get("antwort") or "")
        mapping = daten.get("mapping") or {}
        modus = daten.get("modus") or profil.get("mandat", {}).get("modus") or "vollprofil"

        if modus == "vollprofil":
            roh = json.dumps(profil, ensure_ascii=False)
            profil = json.loads(pseudonymize.repersonalisieren(roh, mapping))

        befunde = steckbrief_build.pruefe(profil, modus)
        text = steckbrief_build.render(profil, modus)
        ordner = fallordner(profil.get("mandat", {}).get("profil_id"))
        with open(os.path.join(ordner, "profil.json"), "w", encoding="utf-8") as handle:
            json.dump(profil, handle, ensure_ascii=False, indent=2)
        with open(os.path.join(ordner, "zuordnung.json"), "w", encoding="utf-8") as handle:
            json.dump(mapping, handle, ensure_ascii=False, indent=2)
        return {
            "profil": profil,
            "steckbrief": text,
            "ordner": ordner,
            "befunde": [b.as_dict() for b in befunde],
            "fehler_anzahl": len([b for b in befunde if b.tier == "fehler"]),
        }

    def a_export(self, daten):
        text = daten.get("steckbrief") or ""
        profil_id = daten.get("profil_id") or "ohne-id"
        ordner = fallordner(profil_id)
        docx_pfad = os.path.join(ordner, "Steckbrief_%s.docx" % profil_id)
        docx_writer.schreibe_docx(docx_pfad, docx_writer.steckbrief_zu_absaetzen(text))
        txt_pfad = os.path.join(ordner, "Steckbrief_%s.txt" % profil_id)
        with open(txt_pfad, "w", encoding="utf-8") as handle:
            handle.write(text)
        return {"docx": docx_pfad, "txt": txt_pfad, "ordner": ordner}

    def a_mail(self, daten):
        ok, meldung = mail_entwurf(
            daten.get("pfad") or "",
            daten.get("empfaenger") or "",
            daten.get("betreff") or "Kandidatenprofil, vertraulich",
            daten.get("text") or "")
        return {"ok": ok, "meldung": meldung}


OBERFLAECHE = r"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<title>A/A Steckbrief-Arbeitsplatz</title>
<style>
:root{--bg:#f6f6f4;--fg:#1c1c1a;--line:#d6d4cf;--akz:#8a1c1c;--ok:#1d6b3a;--warn:#8a5a00}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 "Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{background:#1c1c1a;color:#fff;padding:14px 22px}
header b{font-size:17px;letter-spacing:.3px}
header span{opacity:.75;font-size:13px;margin-left:10px}
main{max-width:1080px;margin:0 auto;padding:22px}
section{background:#fff;border:1px solid var(--line);border-radius:6px;padding:18px 20px;margin-bottom:16px}
h2{font-size:15px;margin:0 0 12px;text-transform:uppercase;letter-spacing:.6px;color:var(--akz)}
label{display:block;font-weight:600;font-size:13px;margin:10px 0 4px}
input[type=text],textarea,select{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:4px;font:inherit;background:#fff}
textarea{min-height:120px;font-family:Consolas,monospace;font-size:13px}
button{background:var(--akz);color:#fff;border:0;border-radius:4px;padding:9px 16px;font:inherit;font-weight:600;cursor:pointer;margin:8px 8px 0 0}
button.sek{background:#4a4a46}
button:disabled{opacity:.45;cursor:not-allowed}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}
.hint{font-size:13px;color:#5c5a55;margin:6px 0 0}
.pill{display:inline-block;border:1px solid var(--line);border-radius:14px;padding:3px 10px;margin:3px 4px 0 0;font-size:13px;cursor:pointer;background:#fff;user-select:none}
.pill.an{background:var(--akz);color:#fff;border-color:var(--akz)}
.status{padding:9px 12px;border-radius:4px;margin-top:10px;font-size:13px;display:none}
.status.ok{display:block;background:#e7f3ea;color:var(--ok)}
.status.err{display:block;background:#fbeaea;color:var(--akz)}
.status.warn{display:block;background:#fdf3e0;color:var(--warn)}
pre{background:#fafaf8;border:1px solid var(--line);border-radius:4px;padding:12px;white-space:pre-wrap;font-size:13px;max-height:340px;overflow:auto}
.f{font-size:13px;padding:3px 0;border-bottom:1px solid #eee}
.f b{display:inline-block;min-width:74px}
.f.fehler b{color:var(--akz)}.f.warnung b{color:var(--warn)}.f.hinweis b{color:#5c5a55}
footer{padding:14px 22px;font-size:12px;color:#5c5a55;text-align:center}
</style></head><body>
<header><b>A/A Steckbrief-Arbeitsplatz</b><span>lokal auf diesem Rechner, Klardaten verlassen die Maschine nicht</span></header>
<main>

<section><h2>1 Mandat</h2>
<div class="grid">
<div><label>Position</label><input type="text" id="m_position" placeholder="Geschaeftsfuehrer Vertrieb"></div>
<div><label>Auftraggeber</label><input type="text" id="m_kunde" placeholder="Musterhaus Automobile GmbH"></div>
<div><label>Profil-ID</label><input type="text" id="m_id" placeholder="MHA-GFV-03"></div>
<div><label>Datum</label><input type="text" id="m_datum"></div>
<div><label>Berater</label><input type="text" id="m_berater" placeholder="Aaron Arena"></div>
<div><label>Modus</label><select id="m_modus">
<option value="vollprofil">Vollprofil, Klarname, Freigabe liegt vor</option>
<option value="blindprofil">Blindprofil, anonymisiert</option></select></div>
</div></section>

<section><h2>2 Lebenslauf laden</h2>
<label>Datei (.docx oder .txt)</label><input type="file" id="datei" accept=".docx,.txt,.md">
<p class="hint">PDF wird nicht gelesen. Text im Reader kopieren und unten einfuegen. Die Datei wird lokal gelesen und nicht hochgeladen.</p>
<label>Lebenslauftext</label><textarea id="cvtext" placeholder="Text einfuegen oder Datei waehlen"></textarea>
<label>Interviewnotizen, optional</label><textarea id="notizen" style="min-height:80px" placeholder="Wechselmotiv, Gehaltsrahmen, Kuendigungsfrist, Referenzstand"></textarea>
</section>

<section><h2>3 Pseudonymisieren</h2>
<label>Name der Kandidatin oder des Kandidaten</label><input type="text" id="kandidat" placeholder="Vorname Nachname">
<label>Arbeitgeber, die ersetzt werden (anklicken zum Abwaehlen)</label>
<div id="entitaeten"></div>
<label>Weitere Begriffe, kommagetrennt (Orte, Standorte, Marken)</label>
<input type="text" id="orte" placeholder="Stuttgart, Region Karlsruhe">
<button onclick="promptBauen()">Pseudonymisieren und Prompt erzeugen</button>
<div id="s_prompt" class="status"></div>
<pre id="promptbox" style="display:none"></pre>
<button id="b_copy" class="sek" style="display:none" onclick="kopieren()">Prompt in die Zwischenablage</button>
<button id="b_api" class="sek" style="display:none" onclick="apiSenden()">Ueber API senden, falls Schluessel hinterlegt</button>
</section>

<section><h2>4 Antwort zurueckspielen</h2>
<p class="hint">Prompt in Claude einfuegen, die JSON-Antwort hier hereinkopieren. Die Klardaten werden lokal wieder eingesetzt.</p>
<textarea id="antwort" placeholder="JSON-Antwort des Modells"></textarea>
<button onclick="bauen()">Steckbrief erzeugen und pruefen</button>
<div id="s_build" class="status"></div>
<div id="befunde"></div>
<pre id="vorschau" style="display:none"></pre>
</section>

<section><h2>5 Ausgeben und versenden</h2>
<button id="b_export" disabled onclick="exportieren()">Word-Datei erzeugen</button>
<div id="s_export" class="status"></div>
<div class="grid">
<div><label>Empfaenger</label><input type="text" id="mail_to" placeholder="name@auftraggeber.de"></div>
<div><label>Betreff</label><input type="text" id="mail_betreff" value="Kandidatenprofil, vertraulich"></div>
</div>
<label>Mailtext</label><textarea id="mail_text" style="min-height:90px">Sehr geehrte Damen und Herren,

anbei das Kandidatenprofil zur besprochenen Position. Das Profil ist vertraulich und ausschliesslich fuer die Besetzung dieser Position bestimmt.

Fuer Rueckfragen stehe ich zur Verfuegung.

Mit freundlichen Gruessen
A/A Executive Search</textarea>
<button id="b_mail" disabled onclick="mailen()">Mailentwurf oeffnen</button>
<div id="s_mail" class="status"></div>
</section>

</main>
<footer>Alle Dateien liegen unter Dokumente, AA-Steckbriefe. Zuordnungstabelle und Lebenslauf verlassen diesen Rechner nicht.</footer>

<script>
const T="__TOKEN__";
let MAPPING={}, ENTS=[], AKTIV=new Set(), LETZTER_PFAD="", LETZTE_ID="";
document.getElementById("m_datum").value=new Date().toLocaleDateString("de-DE");

function zeige(id,text,art){const e=document.getElementById(id);e.className="status "+art;e.textContent=text;}
async function post(pfad,daten){
  const r=await fetch(pfad,{method:"POST",headers:{"Content-Type":"application/json","X-AA-Token":T},body:JSON.stringify(daten)});
  const j=await r.json(); if(j.fehler) throw new Error(j.fehler); return j;
}
function orteListe(){return document.getElementById("orte").value.split(",").map(s=>s.trim()).filter(Boolean);}
function mandat(){return{position:v("m_position"),auftraggeber:v("m_kunde"),profil_id:v("m_id"),
  datum:v("m_datum"),berater:v("m_berater"),modus:v("m_modus")};}
function v(id){return document.getElementById(id).value.trim();}

document.getElementById("datei").addEventListener("change",async e=>{
  const f=e.target.files[0]; if(!f) return;
  const b=await f.arrayBuffer();
  const b64=btoa(Array.from(new Uint8Array(b),c=>String.fromCharCode(c)).join(""));
  try{
    const j=await post("/api/extract",{dateiname:f.name,inhalt_base64:b64});
    document.getElementById("cvtext").value=j.text;
    ENTS=j.entitaeten; AKTIV=new Set(ENTS); zeichneEnts();
    zeige("s_prompt","Lebenslauf gelesen, "+j.text.length+" Zeichen, "+ENTS.length+" Arbeitgeber erkannt.","ok");
  }catch(err){zeige("s_prompt",err.message,"err");}
});

function zeichneEnts(){
  const box=document.getElementById("entitaeten"); box.innerHTML="";
  ENTS.forEach(e=>{
    const s=document.createElement("span");
    s.className="pill"+(AKTIV.has(e)?" an":""); s.textContent=e;
    s.onclick=()=>{AKTIV.has(e)?AKTIV.delete(e):AKTIV.add(e);zeichneEnts();};
    box.appendChild(s);
  });
}

async function promptBauen(){
  try{
    const j=await post("/api/prompt",{text:v("cvtext"),notizen:v("notizen"),kandidat:v("kandidat"),
      arbeitgeber:[...AKTIV],orte:orteListe(),mandat:mandat()});
    MAPPING=j.mapping;
    document.getElementById("promptbox").style.display="block";
    document.getElementById("promptbox").textContent=j.prompt;
    document.getElementById("b_copy").style.display="inline-block";
    document.getElementById("b_api").style.display="inline-block";
    if(j.sauber){zeige("s_prompt","Pseudonymisiert. Rueckstandspruefung sauber, "+Object.keys(MAPPING).length+" Ersetzungen.","ok");}
    else{zeige("s_prompt","Achtung, es steht noch Klartext im Prompt: "+j.rest.join(", "),"err");}
  }catch(err){zeige("s_prompt",err.message,"err");}
}

function kopieren(){
  navigator.clipboard.writeText(document.getElementById("promptbox").textContent)
    .then(()=>zeige("s_prompt","Prompt kopiert. In Claude einfuegen, Antwort in Schritt 4 zurueckspielen.","ok"))
    .catch(()=>zeige("s_prompt","Kopieren nicht moeglich, Text bitte manuell markieren.","warn"));
}

async function apiSenden(){
  zeige("s_prompt","Anfrage laeuft, das kann eine Minute dauern.","warn");
  try{
    const j=await post("/api/llm",{prompt:document.getElementById("promptbox").textContent,
      kandidat:v("kandidat"),arbeitgeber:[...AKTIV],orte:orteListe(),
      ausnahmen:[v("m_berater"),v("m_kunde")].filter(Boolean)});
    document.getElementById("antwort").value=j.antwort;
    zeige("s_prompt","Antwort empfangen. Weiter mit Schritt 4.","ok");
  }catch(err){zeige("s_prompt",err.message,"err");}
}

async function bauen(){
  try{
    const j=await post("/api/build",{antwort:v("antwort"),mapping:MAPPING,modus:v("m_modus")});
    document.getElementById("vorschau").style.display="block";
    document.getElementById("vorschau").textContent=j.steckbrief;
    const box=document.getElementById("befunde"); box.innerHTML="";
    j.befunde.forEach(b=>{
      const d=document.createElement("div"); d.className="f "+b.tier;
      d.innerHTML="<b>"+b.tier.toUpperCase()+"</b> "+b.ort+": "+b.text; box.appendChild(d);
    });
    LETZTE_ID=(j.profil.mandat&&j.profil.mandat.profil_id)||v("m_id")||"ohne-id";
    document.getElementById("b_export").disabled=false;
    if(j.fehler_anzahl>0){zeige("s_build",j.fehler_anzahl+" Fehler. Nicht freigabefaehig, bitte beheben.","err");}
    else{zeige("s_build","Keine Fehler. Freigabefaehig. Dateien unter "+j.ordner,"ok");}
  }catch(err){zeige("s_build",err.message,"err");}
}

async function exportieren(){
  try{
    const j=await post("/api/export",{steckbrief:document.getElementById("vorschau").textContent,profil_id:LETZTE_ID});
    LETZTER_PFAD=j.docx; document.getElementById("b_mail").disabled=false;
    zeige("s_export","Word-Datei erzeugt: "+j.docx,"ok");
  }catch(err){zeige("s_export",err.message,"err");}
}

async function mailen(){
  try{
    const j=await post("/api/mail",{pfad:LETZTER_PFAD,empfaenger:v("mail_to"),
      betreff:v("mail_betreff"),text:document.getElementById("mail_text").value});
    zeige("s_mail",j.meldung,"ok");
  }catch(err){zeige("s_mail",err.message,"err");}
}
</script></body></html>"""


def main(argv=None):
    parser = argparse.ArgumentParser(description="A/A Steckbrief-Arbeitsplatz, lokal.")
    parser.add_argument("--port", type=int, default=8731)
    parser.add_argument("--kein-browser", action="store_true")
    args = parser.parse_args(argv)

    os.makedirs(AUSGABE_WURZEL, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    adresse = "http://127.0.0.1:%d/?t=%s" % (args.port, TOKEN)

    print("A/A Steckbrief-Arbeitsplatz laeuft lokal.")
    print("Adresse: %s" % adresse)
    print("Ausgabeordner: %s" % AUSGABE_WURZEL)
    print("Beenden mit Strg+C. Der Zugriffstoken gilt nur fuer diesen Start.")
    if not args.kein_browser:
        webbrowser.open(adresse)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
