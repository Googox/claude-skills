#!/usr/bin/env python3
"""
CFD Intraday Analyst: Opening-Range-Breakout-Analyse fuer XAU/USD und NAS100.

Reines Analyse-Werkzeug fuer CFD-Trading (z. B. Vantage, MT5). Keine
Broker-Anbindung, keine Orders. Long und Short, London- und NY-Eroeffnung.

Unterbefehle:
    fetch       5-Minuten-Kerzen von Yahoo laden (GC=F / NQ=F als Proxy)
    mt5-import  MT5-CSV-Export (M1 oder M5) einlesen und normalisieren
    entry       Status des Opening-Range-Breakouts: wartend / ausgeloest / abgelaufen
    exit        Stop und Ziel festlegen, BEVOR eingestiegen wird -> plan.json
    size        Positionsgroesse in Lots aus Risiko, Stop-Abstand und Kontraktgroesse
    replay      Rest der Session 10.000-mal aus der eigenen Historie durchspielen
    risk        Tageslimits und Regeln pruefen: PASS oder BLOCK
    journal     Tagesergebnisse erfassen (fuer die Tageslimits)
    selftest    Offline-Selbsttest auf synthetischen Daten

Beispiele:
    python3 cfd_analyst.py fetch --instrument XAUUSD
    python3 cfd_analyst.py entry --instrument NAS100 --session ny --write
    python3 cfd_analyst.py exit --stop or-mid --target 2R --write
    python3 cfd_analyst.py size --write
    python3 cfd_analyst.py replay --write
    python3 cfd_analyst.py risk
    python3 cfd_analyst.py selftest

Methodik (Kerzenschluss als Signal, Stop/Ziel vor dem Einstieg, Replay aus
der eigenen Historie) angelehnt an github.com/Jakeschincariol/day-trader-skill
(MIT). Der Code hier ist eigenstaendig.

Keine Anlageberatung. Python 3.8+, nur Standardbibliothek.
"""

import argparse
import csv
import datetime as dt
import io
import json
import math
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.0.0"
BAR = 300  # 5-Minuten-Kerzen
UTC = dt.timezone.utc
EPS = 1e-9
UA = "Mozilla/5.0 (compatible; cfd-intraday-analyst/1.0)"

PROXY_NOTE = ("Yahoo-Futures-Kurse (%s) sind ein Proxy: absolute Preise weichen vom "
              "Vantage-CFD ab. Abstaende und R-Vielfache sind vergleichbar, Level nicht 1:1.")


class UserError(Exception):
    """Fehler mit einer klaren Meldung fuer den Nutzer (Exit-Code 1)."""


# --------------------------------------------------------------------------
# Zeitzonen ohne zoneinfo: nur die Regeln, die gebraucht werden
# --------------------------------------------------------------------------

TZ_RULES = {
    "Europe/London": ("eu", 0),
    "Europe/Berlin": ("eu", 1),
    "America/New_York": ("us", -5),
}


def _nth_sunday(year, month, n):
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _last_sunday(year, month):
    d = dt.date(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - 6) % 7)


def us_dst(day):
    return _nth_sunday(day.year, 3, 2) <= day < _nth_sunday(day.year, 11, 1)


def eu_dst(day):
    return _last_sunday(day.year, 3) <= day < _last_sunday(day.year, 10)


def utc_offset_hours(tz, day):
    """UTC-Offset einer Zeitzone an einem Kalendertag (Sommerzeit inklusive)."""
    if tz == "UTC":
        return 0
    if tz not in TZ_RULES:
        raise UserError("Zeitzone '%s' nicht unterstuetzt (erlaubt: UTC, %s)" % (tz, ", ".join(TZ_RULES)))
    rule, base = TZ_RULES[tz]
    return base + (1 if (eu_dst(day) if rule == "eu" else us_dst(day)) else 0)


def local_to_epoch(day, hhmm, tz):
    h, m = (int(x) for x in hhmm.split(":"))
    naive = dt.datetime(day.year, day.month, day.day, h, m, tzinfo=UTC)
    return int(naive.timestamp()) - utc_offset_hours(tz, day) * 3600


def epoch_to_local(t, tz):
    u = dt.datetime.fromtimestamp(t, UTC).replace(tzinfo=None)
    loc = u + dt.timedelta(hours=utc_offset_hours(tz, u.date()))
    off2 = utc_offset_hours(tz, loc.date())
    return u + dt.timedelta(hours=off2)


def hm(t, tz):
    return epoch_to_local(t, tz).strftime("%H:%M")


def de_and_local(t, tz):
    """'15:55 Uhr DE (09:55 New York)' - Aaron sitzt in Deutschland."""
    city = {"America/New_York": "New York", "Europe/London": "London"}.get(tz, tz)
    return "%s Uhr DE (%s %s)" % (hm(t, "Europe/Berlin"), hm(t, tz), city)


def parse_now(s):
    """--now 'YYYY-MM-DD HH:MM' in deutscher Zeit (Europe/Berlin)."""
    if not s:
        return int(dt.datetime.now(UTC).timestamp())
    try:
        d = dt.datetime.strptime(s.strip(), "%Y-%m-%d %H:%M")
    except ValueError:
        raise UserError("--now erwartet 'YYYY-MM-DD HH:MM' (deutsche Zeit), z. B. '2026-10-19 15:55'")
    return local_to_epoch(d.date(), d.strftime("%H:%M"), "Europe/Berlin")


# --------------------------------------------------------------------------
# Konfiguration und Dateien
# --------------------------------------------------------------------------

def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise UserError("Datei fehlt: %s" % path)
    except json.JSONDecodeError as e:
        raise UserError("Kein gueltiges JSON in %s: %s" % (path, e))


def write_json(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def load_config(args):
    path = args.config or os.path.join(args.dir, "config.json")
    if not os.path.exists(path):
        raise UserError("Keine Config unter %s. Vorlage kopieren: cp assets/config.example.json %s "
                        "und die Vantage-Kontraktdaten aus MT5 eintragen." % (path, path))
    return read_json(path)


def instrument_cfg(cfg, name):
    inst = cfg.get("instruments", {})
    if name not in inst:
        raise UserError("Instrument '%s' nicht in der Config (vorhanden: %s)" % (name, ", ".join(inst) or "keine"))
    return inst[name]


def session_cfg(cfg, name):
    s = cfg.get("sessions", {})
    if name not in s:
        raise UserError("Session '%s' nicht in der Config (vorhanden: %s)" % (name, ", ".join(s) or "keine"))
    return s[name]


def session_frame(day, sess):
    tz = sess["tz"]
    orm = int(sess.get("or_minutes", 15))
    if orm <= 0 or orm % 5:
        raise UserError("or_minutes muss ein Vielfaches von 5 sein (ist %s)" % orm)
    op = local_to_epoch(day, sess["open"], tz)
    fr = {"day": day.isoformat(), "tz": tz, "open": op, "or_end": op + orm * 60,
          "or_bars": orm // 5,
          "last_entry": local_to_epoch(day, sess["no_entries_after"], tz),
          "flat_by": local_to_epoch(day, sess["flat_by"], tz)}
    if not fr["or_end"] < fr["last_entry"] <= fr["flat_by"]:
        raise UserError("Session-Zeiten unlogisch: Range-Ende < no_entries_after <= flat_by noetig")
    return fr


# --------------------------------------------------------------------------
# Kursdaten: Yahoo (Proxy) und MT5-Export
# --------------------------------------------------------------------------

def normalize(bars, instrument, source, note=""):
    clean = {}
    for t, o, h, l, c in bars:
        if None in (t, o, h, l, c):
            continue
        t = int(t)
        if t % BAR:
            continue
        clean[t] = [float(o), float(h), float(l), float(c)]
    rows = [[t] + clean[t] for t in sorted(clean)]
    return {"instrument": instrument, "source": source, "note": note, "interval": "5m",
            "fetched_at": int(dt.datetime.now(UTC).timestamp()), "bars": rows}


def fetch_yahoo(symbol, rng="60d", timeout=30):
    last_err = None
    for host in ("query2", "query1"):
        url = "https://%s.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=5m" % (
            host, urllib.parse.quote(symbol), rng)
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8"))
            res = data["chart"]["result"][0]
            q = res["indicators"]["quote"][0]
            return list(zip(res.get("timestamp") or [], q["open"], q["high"], q["low"], q["close"]))
        except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError, TypeError) as e:
            last_err = e
    raise UserError("Yahoo nicht erreichbar fuer %s (%s). Alternative: MT5-Export mit mt5-import." % (symbol, last_err))


def mt5_offset_hours(spec, server_day):
    """Serverzeit-Offset: Zahl (z. B. 2) oder 'ny-close' (UTC+2, UTC+3 waehrend US-Sommerzeit)."""
    if spec is None:
        raise UserError("--server-offset fehlt. In MT5 die Serverzeit mit UTC vergleichen "
                        "(siehe references/mt5-export.md) und z. B. 'ny-close' oder '2' angeben.")
    if str(spec).lower() == "ny-close":
        return 3 if us_dst(server_day) else 2
    try:
        return float(spec)
    except ValueError:
        raise UserError("--server-offset: Zahl oder 'ny-close' erwartet, nicht '%s'" % spec)


def parse_mt5_csv(text, server_offset):
    """MT5-Export (<DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> ...), Tab/Komma/Semikolon,
    mit oder ohne Kopfzeile. M1 wird zu M5 verdichtet. Gibt UTC-Kerzen zurueck."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise UserError("MT5-Datei ist leer")
    delim = "\t" if "\t" in lines[0] else (";" if ";" in lines[0] else ",")
    rows = list(csv.reader(io.StringIO("\n".join(lines)), delimiter=delim))
    head = [c.strip().strip("<>").upper() for c in rows[0]]
    if "DATE" in head:
        idx = {k: head.index(k) for k in ("DATE", "TIME", "OPEN", "HIGH", "LOW", "CLOSE") if k in head}
        rows = rows[1:]
        if "TIME" not in idx:
            raise UserError("MT5-Export ohne Zeitspalte: bitte M1 oder M5 exportieren, nicht Tageskerzen")
    else:
        idx = {"DATE": 0, "TIME": 1, "OPEN": 2, "HIGH": 3, "LOW": 4, "CLOSE": 5}
    raw = []
    for r in rows:
        try:
            ds, ts = r[idx["DATE"]].strip(), r[idx["TIME"]].strip()
            d = dt.datetime.strptime(ds.replace("-", ".").replace("/", "."), "%Y.%m.%d")
            parts = ts.split(":")
            local = d.replace(hour=int(parts[0]), minute=int(parts[1]))
            off = mt5_offset_hours(server_offset, local.date())
            t = int(local.replace(tzinfo=UTC).timestamp() - off * 3600)
            o, h, l, c = (float(r[idx[k]]) for k in ("OPEN", "HIGH", "LOW", "CLOSE"))
        except (ValueError, IndexError):
            continue
        raw.append((t, o, h, l, c))
    if len(raw) < 2:
        raise UserError("MT5-Datei: keine lesbaren Kerzen gefunden")
    raw.sort()
    step = min(b[0] - a[0] for a, b in zip(raw, raw[1:]) if b[0] > a[0])
    if step not in (60, 300):
        raise UserError("MT5-Export hat %d-Sekunden-Kerzen. Bitte M1 oder M5 exportieren." % step)
    buckets = {}
    for t, o, h, l, c in raw:
        k = t - t % BAR
        if k not in buckets:
            buckets[k] = [k, o, h, l, c]
        else:
            b = buckets[k]
            b[2], b[3], b[4] = max(b[2], h), min(b[3], l), c
    return [tuple(buckets[k]) for k in sorted(buckets)], step


def load_bars(args, cfg, instrument, max_age=None):
    """Kerzen aus --data, sonst Cache cfd/data/<INSTR>-5m.json, sonst live von Yahoo."""
    path = getattr(args, "data", None)
    if path:
        doc = read_json(path)
    else:
        path = os.path.join(args.dir, "data", "%s-5m.json" % instrument)
        doc = None
        if os.path.exists(path):
            doc = read_json(path)
            age = int(dt.datetime.now(UTC).timestamp()) - int(doc.get("fetched_at", 0))
            if doc.get("source", "").startswith("yahoo") and max_age is not None and age > max_age:
                doc = None
        if doc is None:
            sym = instrument_cfg(cfg, instrument).get("yahoo_symbol")
            if not sym:
                raise UserError("Kein yahoo_symbol fuer %s in der Config und keine --data-Datei" % instrument)
            doc = normalize(fetch_yahoo(sym), instrument, "yahoo:" + sym, PROXY_NOTE % sym)
            write_json(path, doc)
    bars = {int(r[0]): tuple(r[1:5]) for r in doc.get("bars", [])}
    if not bars:
        raise UserError("Keine Kerzen in den Daten fuer %s" % instrument)
    return bars, doc


# --------------------------------------------------------------------------
# entry: Opening-Range-Breakout, Long und Short
# --------------------------------------------------------------------------

def evaluate_entry(bars, fr, now):
    """Reine Funktion: Status des Setups zum Zeitpunkt now (UTC-Epoch)."""
    res = {"day": fr["day"], "open": fr["open"], "or_end": fr["or_end"],
           "last_entry": fr["last_entry"], "flat_by": fr["flat_by"], "direction": None}
    day = dt.date.fromisoformat(fr["day"])
    if day.weekday() >= 5:
        res.update(status="geschlossen", reason="Wochenende")
        return res
    if now < fr["open"]:
        res.update(status="vor-eroeffnung", reason="Session oeffnet %s" % de_and_local(fr["open"], fr["tz"]))
        return res
    later = [t for t in bars if t >= fr["open"]]
    data_end = max(later) + BAR if later else fr["open"]
    eval_now = min(now, data_end)
    res["data_lag_min"] = max(0, (now - eval_now) // 60) if now < fr["flat_by"] else 0
    or_slots = list(range(fr["open"], fr["or_end"], BAR))
    closed = [bars[t] for t in or_slots if t in bars and t + BAR <= eval_now]
    if eval_now < fr["or_end"]:
        res.update(status="range-bildet-sich", or_bars_done=len(closed), or_bars=len(or_slots))
        if closed:
            res.update(or_high=max(b[1] for b in closed), or_low=min(b[2] for b in closed))
        return res
    missing = [t for t in or_slots if t not in bars]
    if missing:
        res.update(status="keine-daten", reason="%d von %d Range-Kerzen fehlen" % (len(missing), len(or_slots)))
        return res
    hi = max(bars[t][1] for t in or_slots)
    lo = min(bars[t][2] for t in or_slots)
    res.update(or_high=hi, or_low=lo)
    last = None
    for t in range(fr["or_end"], fr["last_entry"], BAR):
        if t + BAR > eval_now:
            break
        b = bars.get(t)
        if b is None:
            continue
        last = (t, b)
        if b[3] > hi + EPS or b[3] < lo - EPS:
            res.update(status="ausgeloest", direction="long" if b[3] > hi else "short",
                       trigger_bar=t, entry_t=t + BAR, entry=b[3])
            res["age_bars"] = max(0, (now - (t + BAR)) // BAR)
            return res
    if eval_now >= fr["last_entry"]:
        res.update(status="abgelaufen", reason="kein Schluss ausserhalb der Range bis %s" % hm(fr["last_entry"], fr["tz"]))
        return res
    res["status"] = "wartend"
    if last:
        res.update(last_close=last[1][3], last_bar=last[0],
                   dist_long=hi - last[1][3], dist_short=last[1][3] - lo)
    return res


def fmt_price(x, dec):
    return ("%%.%df" % dec) % x


def cmd_entry(args):
    cfg = load_config(args)
    ic = instrument_cfg(cfg, args.instrument)
    sc = session_cfg(cfg, args.session)
    now = parse_now(args.now)
    day = epoch_to_local(now, sc["tz"]).date()
    fr = session_frame(day, sc)
    bars, doc = load_bars(args, cfg, args.instrument, max_age=0 if not args.now else None)
    res = evaluate_entry(bars, fr, now)
    res.update(instrument=args.instrument, session=args.session, source=doc.get("source"),
               tz=sc["tz"], generated_at=now)
    if args.write and res["status"] in ("ausgeloest", "wartend"):
        write_json(os.path.join(args.dir, "entry.json"), res)
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    dec = int(ic.get("price_decimals", 2))
    tz = sc["tz"]
    print("%s  Session %s  %s  (Quelle: %s)" % (args.instrument, args.session, res["day"], res.get("source")))
    if "or_high" in res and res["status"] != "range-bildet-sich":
        print("Opening Range %s bis %s: Hoch %s, Tief %s" % (
            hm(fr["open"], tz), hm(fr["or_end"], tz), fmt_price(res["or_high"], dec), fmt_price(res["or_low"], dec)))
    st = res["status"]
    if st == "ausgeloest":
        lvl = res["or_high"] if res["direction"] == "long" else res["or_low"]
        print("AUSGELOEST %s um %s bei %s: Kerze schliesst %s der Range (%s)." % (
            res["direction"].upper(), de_and_local(res["entry_t"], tz), fmt_price(res["entry"], dec),
            "ueber" if res["direction"] == "long" else "unter", fmt_price(lvl, dec)))
        if res["age_bars"] >= 2:
            print("Achtung: Signal ist %d Kerzen alt. Ein spaeter Einstieg ist ein anderer Trade." % res["age_bars"])
        print("Nichts wurde platziert. Weiter: exit (Stop und Ziel VOR dem Einstieg).")
    elif st == "wartend":
        if "last_close" in res:
            print("WARTEND  letzter Schluss %s: %s bis Long-Trigger, %s bis Short-Trigger." % (
                fmt_price(res["last_close"], dec), fmt_price(res["dist_long"], dec), fmt_price(res["dist_short"], dec)))
        else:
            print("WARTEND  noch keine abgeschlossene Kerze nach der Range.")
        print("Einstiege bis %s." % de_and_local(fr["last_entry"], tz))
    elif st == "range-bildet-sich":
        print("RANGE BILDET SICH  %d von %d Kerzen fertig (bis %s)." % (
            res["or_bars_done"], res["or_bars"], de_and_local(fr["or_end"], tz)))
    else:
        print("%s  %s" % (st.upper(), res.get("reason", "")))
    if res.get("data_lag_min", 0) > 5:
        print("Hinweis: Daten hinken %d Minuten hinterher." % res["data_lag_min"])
    if str(res.get("source", "")).startswith("yahoo"):
        print(doc.get("note", ""))
    return 0


# --------------------------------------------------------------------------
# exit: Stop und Ziel vor dem Einstieg
# --------------------------------------------------------------------------

def _round_away(x, dec, up):
    f = 10 ** dec
    return (math.ceil(x * f - EPS) if up else math.floor(x * f + EPS)) / f


def _round_half(x, dec):
    f = 10 ** dec
    return math.floor(x * f + 0.5 + EPS) / f


def atr(seq, n=14):
    """seq: Kerzen (o,h,l,c) bis einschliesslich Einstiegskerze."""
    trs = []
    for prev, b in zip(seq, seq[1:]):
        trs.append(max(b[1] - b[2], abs(b[1] - prev[3]), abs(b[2] - prev[3])))
    trs = trs[-n:]
    if not trs:
        raise UserError("Zu wenige Kerzen fuer einen ATR-Stop")
    return sum(trs) / len(trs)


def stop_price(spec, direction, entry, or_hi, or_lo, atr_value=None):
    long = direction == "long"
    if spec == "or-mid":
        return (or_hi + or_lo) / 2.0
    if spec == "or-opposite":
        return or_lo if long else or_hi
    kind, _, val = spec.partition(":")
    try:
        v = float(val)
    except ValueError:
        raise UserError("Stop-Regel '%s' unbekannt (or-mid, or-opposite, atr:K, pct:X, price:X)" % spec)
    if kind == "price":
        return v
    if kind == "pct":
        return entry * (1 - v / 100.0) if long else entry * (1 + v / 100.0)
    if kind == "atr":
        if atr_value is None:
            raise UserError("atr-Stop braucht Kerzen")
        return entry - v * atr_value if long else entry + v * atr_value
    raise UserError("Stop-Regel '%s' unbekannt" % spec)


def target_r(spec):
    s = spec.strip().upper()
    if s.endswith("R"):
        try:
            return float(s[:-1])
        except ValueError:
            pass
    return None


def make_plan(ic, sc, entry_info, stop_spec, target_spec, atr_value=None):
    dec = int(ic.get("price_decimals", 2))
    d = entry_info["direction"]
    if d not in ("long", "short"):
        raise UserError("Richtung muss long oder short sein")
    long = d == "long"
    e = float(entry_info["entry"])
    raw_stop = stop_price(stop_spec, d, e, entry_info.get("or_high"), entry_info.get("or_low"), atr_value)
    stop = _round_away(raw_stop, dec, up=not long)
    if (long and stop >= e) or (not long and stop <= e):
        raise UserError("Stop %s liegt auf der falschen Seite des Einstiegs %s" % (fmt_price(stop, dec), fmt_price(e, dec)))
    risk = abs(e - stop)
    spread = float(ic.get("spread") or 0)
    min_risk = max(2 * spread, e * 0.0002)
    if risk < min_risk:
        raise UserError("Stop zu eng (%s): unter %s ueberlebt er Spread und Grundrauschen nicht" % (
            fmt_price(risk, dec), fmt_price(min_risk, dec)))
    r = target_r(target_spec)
    if r is not None:
        if r <= 0:
            raise UserError("Ziel-R muss positiv sein")
        target = _round_half(e + r * risk if long else e - r * risk, dec)
    elif target_spec.startswith("price:"):
        target = float(target_spec[6:])
    else:
        raise UserError("Ziel '%s' unbekannt (z. B. 2R, 1.5R, price:X)" % target_spec)
    if (long and target <= e) or (not long and target >= e):
        raise UserError("Ziel liegt nicht in Trade-Richtung")
    rr = abs(target - e) / risk
    return {"instrument": entry_info["instrument"], "session": entry_info["session"], "day": entry_info["day"],
            "direction": d, "entry": e, "entry_t": entry_info.get("entry_t"), "stop": stop, "stop_rule": stop_spec,
            "target": target, "target_rule": target_spec, "target_r": round(rr, 4), "risk_per_unit": round(risk, 8),
            "reward_risk": round(rr, 2), "or_high": entry_info.get("or_high"), "or_low": entry_info.get("or_low"),
            "flat_by": entry_info.get("flat_by"), "tz": sc["tz"]}


def cmd_exit(args):
    cfg = load_config(args)
    if args.entry is not None:
        if not (args.instrument and args.session and args.direction):
            raise UserError("Mit --entry auch --instrument, --session und --direction angeben")
        sc = session_cfg(cfg, args.session)
        day = dt.date.fromisoformat(args.day) if args.day else epoch_to_local(parse_now(args.now), sc["tz"]).date()
        fr = session_frame(day, sc)
        info = {"instrument": args.instrument, "session": args.session, "day": day.isoformat(),
                "direction": args.direction, "entry": args.entry, "entry_t": None,
                "or_high": args.or_high, "or_low": args.or_low, "flat_by": fr["flat_by"]}
        if args.stop in ("or-mid", "or-opposite") and (args.or_high is None or args.or_low is None):
            raise UserError("Stop-Regel %s braucht --or-high und --or-low" % args.stop)
    else:
        info = read_json(os.path.join(args.dir, "entry.json"))
        if info.get("status") != "ausgeloest":
            raise UserError("entry.json ist nicht ausgeloest (Status %s). Vorplanen mit --entry PREIS." % info.get("status"))
        sc = session_cfg(cfg, info["session"])
    ic = instrument_cfg(cfg, info["instrument"])
    atr_value = None
    if args.stop.startswith("atr:"):
        bars, _ = load_bars(args, cfg, info["instrument"], max_age=1800)
        upto = info.get("entry_t") or parse_now(args.now)
        seq = [bars[t] for t in sorted(bars) if t + BAR <= upto][-15:]
        atr_value = atr(seq)
    if info.get("entry_t") and info.get("flat_by") and info["entry_t"] >= info["flat_by"]:
        raise UserError("Einstieg liegt nach dem spaetesten Ausstieg (flat_by)")
    plan = make_plan(ic, sc, info, args.stop, args.target, atr_value)
    if args.write:
        write_json(os.path.join(args.dir, "plan.json"), plan)
    if args.format == "json":
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return 0
    dec = int(ic.get("price_decimals", 2))
    print("Exit-Plan: %s %s, Session %s, %s" % (plan["instrument"], plan["direction"].upper(), plan["session"], plan["day"]))
    print("  Einstieg      %s" % fmt_price(plan["entry"], dec))
    print("  Stop          %s  (%s)" % (fmt_price(plan["stop"], dec), plan["stop_rule"]))
    print("  Ziel          %s  (%s)" % (fmt_price(plan["target"], dec), plan["target_rule"]))
    print("  Risiko/Einheit %s Punkte, Chance:Risiko %.2f" % (fmt_price(plan["risk_per_unit"], dec), plan["reward_risk"]))
    if plan.get("flat_by"):
        print("  Raus bis      %s, egal wie" % de_and_local(plan["flat_by"], plan["tz"]))
    print("Ein Stop ist ein Plan, keine Garantie: bei Gaps und schnellen Maerkten fuellt er schlechter.")
    return 0


# --------------------------------------------------------------------------
# size: Lots aus Risiko
# --------------------------------------------------------------------------

def size_position(cfg, plan, balance=None):
    ic = instrument_cfg(cfg, plan["instrument"])
    missing = [k for k in ("contract_size", "min_lot", "lot_step") if ic.get(k) in (None, "", 0)]
    if missing:
        raise UserError("Pflichtfelder fuer %s fehlen in der Config: %s. Werte aus MT5 uebernehmen "
                        "(Marktuebersicht, Rechtsklick auf das Symbol, Spezifikation)." % (plan["instrument"], ", ".join(missing)))
    cs, min_lot, step = float(ic["contract_size"]), float(ic["min_lot"]), float(ic["lot_step"])
    max_lot = ic.get("max_lot")
    rc = cfg.get("risk", {})
    risk_usd = rc.get("risk_per_trade_usd")
    basis = "fest"
    if not risk_usd:
        pct = rc.get("risk_per_trade_pct")
        bal = balance if balance is not None else cfg.get("account", {}).get("balance_usd")
        if not pct or not bal:
            raise UserError("Risiko pro Trade fehlt: risk_per_trade_usd setzen, oder risk_per_trade_pct "
                            "plus balance_usd (bzw. --balance)")
        risk_usd = float(bal) * float(pct) / 100.0
        basis = "%s %% von %s USD" % (pct, bal)
    risk_usd = float(risk_usd)
    spread = float(ic.get("spread") or 0)
    eff = float(plan["risk_per_unit"]) + spread
    raw = risk_usd / (eff * cs)
    lots = math.floor(raw / step + EPS) * step
    capped = False
    if max_lot and lots > float(max_lot):
        lots, capped = math.floor(float(max_lot) / step + EPS) * step, True
    lots = round(lots, 8)
    res = {"instrument": plan["instrument"], "direction": plan["direction"], "risk_usd": round(risk_usd, 2),
           "risk_basis": basis, "contract_size": cs, "spread": spread, "risk_per_unit_eff": round(eff, 8),
           "lots_raw": round(raw, 6), "lots": lots, "capped_by_max_lot": capped, "refusal": None}
    if lots < min_lot - EPS:
        need = min_lot * cs * eff
        res.update(lots=0, refusal="Stop zu weit fuer dein Risiko: schon %s Lot riskiert %.2f USD (erlaubt %.2f USD)"
                   % (min_lot, need, risk_usd))
        return res
    res["loss_at_stop_usd"] = round(lots * cs * eff, 2)
    res["gain_at_target_usd"] = round(lots * cs * (abs(plan["target"] - plan["entry"]) - spread), 2)
    res["notional_usd"] = round(lots * cs * float(plan["entry"]), 2)
    lev = ic.get("leverage")
    if lev:
        res["margin_usd"] = round(res["notional_usd"] / float(lev), 2)
    return res


def cmd_size(args):
    cfg = load_config(args)
    plan = read_json(args.plan or os.path.join(args.dir, "plan.json"))
    res = size_position(cfg, plan, args.balance)
    if args.write and not res["refusal"]:
        write_json(os.path.join(args.dir, "size.json"), res)
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if not res["refusal"] else 2
    print("Positionsgroesse %s %s" % (res["instrument"], res["direction"].upper()))
    print("  Risiko pro Trade  %.2f USD (%s)" % (res["risk_usd"], res["risk_basis"]))
    print("  Stop-Abstand      %s + Spread %s = %s je Einheit, Kontraktgroesse %s" % (
        plan["risk_per_unit"], res["spread"], res["risk_per_unit_eff"], res["contract_size"]))
    if res["refusal"]:
        print("ABGELEHNT: %s" % res["refusal"])
        return 2
    print("  Lots              %s (rechnerisch %s)%s" % (res["lots"], res["lots_raw"],
                                                       ", gedeckelt durch max_lot" if res["capped_by_max_lot"] else ""))
    print("  Verlust am Stop   %.2f USD, Gewinn am Ziel %.2f USD (nach Spread)" % (res["loss_at_stop_usd"], res["gain_at_target_usd"]))
    if "margin_usd" in res:
        print("  Margin ca.        %.2f USD (Nominal %.2f USD)" % (res["margin_usd"], res["notional_usd"]))
    print("Nichts wurde platziert. Weiter: risk.")
    return 0


# --------------------------------------------------------------------------
# replay: 10.000 Durchlaeufe plus echte Historie
# --------------------------------------------------------------------------

def build_pool(bars, sc, before_day):
    tz = sc["tz"]
    days = sorted({epoch_to_local(t, tz).date() for t in bars})
    pool = []
    for d in days:
        if d >= before_day or d.weekday() >= 5:
            continue
        fr = session_frame(d, sc)
        prev = bars.get(fr["open"] - BAR)
        seq = [bars.get(t) for t in range(fr["open"], fr["flat_by"], BAR)]
        if prev is None or any(b is None for b in seq):
            continue
        ratios, pc = [], prev[3]
        for b in seq:
            ratios.append((b[0] / pc, b[1] / pc, b[2] / pc, b[3] / pc))
            pc = b[3]
        pool.append({"day": d.isoformat(), "frame": fr, "bars": seq, "prev": prev, "ratios": ratios})
    return pool


def _pct(sorted_vals, p):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * p
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def run_replays(pool, k, entry, stop, target, direction, n=10000, seed=19, window=2):
    rng = random.Random(seed)
    N = len(pool[0]["ratios"])
    long = direction == "long"
    risk = abs(entry - stop)
    tr = abs(target - entry) / risk
    out = {"target": 0, "stop": 0, "neither": 0, "green": 0}
    rs, closes = [], []
    for _ in range(n):
        p, outcome = entry, None
        for j in range(k, N):
            s = pool[rng.randrange(len(pool))]
            jj = min(N - 1, max(0, j + rng.randint(-window, window)))
            _, rh, rl, rc = s["ratios"][jj]
            h, l, c = p * rh, p * rl, p * rc
            if outcome is None:
                hit_stop = l <= stop if long else h >= stop
                hit_tgt = h >= target if long else l <= target
                if hit_stop:
                    outcome = "stop"
                elif hit_tgt:
                    outcome = "target"
            p = c
        closes.append(p)
        if outcome == "target":
            r = tr
        elif outcome == "stop":
            r = -1.0
        else:
            outcome = "neither"
            r = ((p - entry) if long else (entry - p)) / risk
        out[outcome] += 1
        if outcome == "target" or (outcome == "neither" and r > 0):
            out["green"] += 1
        rs.append(r)
    closes.sort()
    return {"n": n, "seed": seed, "window": window, "bars_left": N - k,
            "target_pct": 100.0 * out["target"] / n, "stop_pct": 100.0 * out["stop"] / n,
            "neither_pct": 100.0 * out["neither"] / n, "green_pct": 100.0 * out["green"] / n,
            "avg_r": sum(rs) / n, "close_median": _pct(closes, 0.5),
            "close_p05": _pct(closes, 0.05), "close_p95": _pct(closes, 0.95)}


def history(pool, plan):
    """Dieselbe Regel auf jeder vergangenen Session: was wirklich passiert ist."""
    rule, tr = plan["stop_rule"], plan["target_r"]
    frac = plan["risk_per_unit"] / plan["entry"]
    res = {"sessions": len(pool), "no_trigger": 0,
           "long": {"fired": 0, "target": 0, "stop": 0, "neither": 0, "r_sum": 0.0},
           "short": {"fired": 0, "target": 0, "stop": 0, "neither": 0, "r_sum": 0.0}}
    for s in pool:
        fr, seq = s["frame"], s["bars"]
        nb = fr["or_bars"]
        hi = max(b[1] for b in seq[:nb])
        lo = min(b[2] for b in seq[:nb])
        last_idx = (fr["last_entry"] - fr["open"]) // BAR
        trig = None
        for i in range(nb, min(last_idx, len(seq))):
            c = seq[i][3]
            if c > hi:
                trig = ("long", i)
                break
            if c < lo:
                trig = ("short", i)
                break
        if not trig:
            res["no_trigger"] += 1
            continue
        d, i = trig
        long = d == "long"
        e = seq[i][3]
        if rule in ("or-mid", "or-opposite"):
            st = stop_price(rule, d, e, hi, lo)
        elif rule.startswith("atr:"):
            st = stop_price(rule, d, e, hi, lo, atr([s["prev"]] + seq[:i + 1]))
        else:
            st = e * (1 - frac) if long else e * (1 + frac)
        risk = abs(e - st)
        if risk <= 0:
            continue
        tg = e + tr * risk if long else e - tr * risk
        outcome, r = "neither", None
        for b in seq[i + 1:]:
            if (long and b[2] <= st) or (not long and b[1] >= st):
                outcome, r = "stop", -1.0
                break
            if (long and b[1] >= tg) or (not long and b[2] <= tg):
                outcome, r = "target", tr
                break
        if r is None:
            last = seq[-1][3]
            r = ((last - e) if long else (e - last)) / risk
        h = res[d]
        h["fired"] += 1
        h[outcome] += 1
        h["r_sum"] += r
    for d in ("long", "short"):
        h = res[d]
        h["avg_r"] = h["r_sum"] / h["fired"] if h["fired"] else None
        del h["r_sum"]
    return res


def verdict(target_pct, stop_pct, r):
    decided = target_pct + stop_pct
    if decided <= 0:
        return "Keine Aussage: kein Durchlauf erreicht Stop oder Ziel."
    share = 100.0 * target_pct / decided
    be = 100.0 / (1 + r)
    diff = share - be
    base = "Ziel zuerst in %.1f %% der entschiedenen Durchlaeufe, Break-even bei %.1f %%." % (share, be)
    if abs(diff) < 5:
        head = "Nahe am Muenzwurf" if abs(r - 1) < 0.05 else "Nahe am Break-even"
    elif abs(diff) < 15:
        head = "Tendiert zum Ziel" if diff > 0 else "Tendiert zum Stop"
    else:
        head = "Deutlich Richtung Ziel" if diff > 0 else "Deutlich Richtung Stop"
    return "%s: %s" % (head, base)


def cmd_replay(args):
    cfg = load_config(args)
    plan = read_json(args.plan or os.path.join(args.dir, "plan.json"))
    sc = session_cfg(cfg, plan["session"])
    ic = instrument_cfg(cfg, plan["instrument"])
    bars, doc = load_bars(args, cfg, plan["instrument"], max_age=1800)
    day = dt.date.fromisoformat(plan["day"])
    fr = session_frame(day, sc)
    pool = build_pool(bars, sc, day)
    if len(pool) < args.min_sessions:
        raise UserError("Nur %d vollstaendige Sessions in den Daten, mindestens %d noetig. "
                        "Mehr Historie per MT5-Export (mt5-import)." % (len(pool), args.min_sessions))
    entry_t = plan.get("entry_t") or fr["or_end"] + BAR
    k = (entry_t - fr["open"]) // BAR
    if k >= len(pool[0]["ratios"]):
        raise UserError("Einstieg liegt nach dem spaetesten Ausstieg: nichts mehr zu simulieren")
    mc = run_replays(pool, k, plan["entry"], plan["stop"], plan["target"], plan["direction"],
                     args.replays, args.seed, args.window)
    hist = history(pool, plan)
    v = verdict(mc["target_pct"], mc["stop_pct"], plan["target_r"])
    res = {"plan": plan, "source": doc.get("source"), "pool_sessions": len(pool),
           "pool_from": pool[0]["day"], "pool_to": pool[-1]["day"], "mc": mc, "history": hist, "verdict": v}
    if args.write:
        write_json(os.path.join(args.dir, "replay.json"), res)
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    dec = int(ic.get("price_decimals", 2))
    print("%d Durchlaeufe, %d Kerzen bis %s, Seed %d, Pool %d Sessions (%s bis %s, %s)." % (
        mc["n"], mc["bars_left"], de_and_local(fr["flat_by"], sc["tz"]), mc["seed"], len(pool),
        res["pool_from"], res["pool_to"], res["source"]))
    print("  Ziel zuerst   %5.1f %%" % mc["target_pct"])
    print("  Stop zuerst   %5.1f %%" % mc["stop_pct"])
    print("  keins von beiden %5.1f %%  (bei flat_by noch offen)" % mc["neither_pct"])
    print("  im Plus       %5.1f %%" % mc["green_pct"])
    print("  Kurs bei flat_by: Median %s, 90 %% zwischen %s und %s" % (
        fmt_price(mc["close_median"], dec), fmt_price(mc["close_p05"], dec), fmt_price(mc["close_p95"], dec)))
    print("  Durchschnitt  %+.3f R" % mc["avg_r"])
    h = hist[plan["direction"]]
    print("Historie, gleiche Regel auf %d echten Sessions: %s-Signal %d-mal, Ziel %d, Stop %d, offen %d%s." % (
        hist["sessions"], plan["direction"], h["fired"], h["target"], h["stop"], h["neither"],
        (", Schnitt %+.3f R" % h["avg_r"]) if h["avg_r"] is not None else ""))
    o = hist["short" if plan["direction"] == "long" else "long"]
    print("  Gegenrichtung: %d Signale, Ziel %d, Stop %d. Kein Signal: %d Sessions." % (
        o["fired"], o["target"], o["stop"], hist["no_trigger"]))
    print(v)
    if mc["neither_pct"] > 40:
        print("%.1f %% der Durchlaeufe enden ohne Treffer: der Kurs bei flat_by entscheidet diese." % mc["neither_pct"])
    print("Simulation aus der eigenen Historie, keine Prognose. News (CPI, FOMC, NFP) machen Dinge, die der Pool nicht kennt.")
    return 0


# --------------------------------------------------------------------------
# risk: PASS oder BLOCK
# --------------------------------------------------------------------------

def load_journal(path):
    if not os.path.exists(path):
        return []
    j = read_json(path)
    return j.get("trades", []) if isinstance(j, dict) else j


def risk_check(cfg, plan, size, journal, now):
    rc = cfg.get("risk", {})
    sc = session_cfg(cfg, plan["session"])
    fr = session_frame(dt.date.fromisoformat(plan["day"]), sc)
    checks = []

    def add(name, ok, detail, hard=True):
        checks.append({"check": name, "ok": bool(ok), "hard": hard, "detail": detail})

    add("Stop und Ziel gesetzt", plan.get("stop") and plan.get("target"), "Stop %s, Ziel %s" % (plan.get("stop"), plan.get("target")))
    mrr = float(rc.get("min_reward_risk", 1.0))
    add("Chance:Risiko", plan["reward_risk"] >= mrr - EPS, "%.2f (Minimum %.2f)" % (plan["reward_risk"], mrr))
    today = epoch_to_local(now, sc["tz"]).date().isoformat()
    add("Plan ist von heute", plan["day"] == today, "Plan %s, heute %s" % (plan["day"], today))
    add("Im Einstiegsfenster", fr["or_end"] <= now <= fr["last_entry"],
        "%s bis %s" % (de_and_local(fr["or_end"], sc["tz"]), de_and_local(fr["last_entry"], sc["tz"])))
    if plan.get("entry_t"):
        age = max(0, (now - plan["entry_t"]) // BAR)
        add("Signal frisch", age <= int(rc.get("max_signal_age_bars", 2)), "%d Kerzen alt" % age)
    lots = size.get("lots", 0) if size else 0
    add("Positionsgroesse vorhanden", lots > 0, "%s Lots" % lots)
    if size and lots > 0:
        add("Verlust am Stop im Limit", size["loss_at_stop_usd"] <= size["risk_usd"] + 0.005,
            "%.2f USD (Limit %.2f USD)" % (size["loss_at_stop_usd"], size["risk_usd"]))
    todays = [t for t in journal if t.get("date") == today]
    mt = int(rc.get("max_trades_per_day", 3))
    add("Trades heute", len(todays) < mt, "%d von maximal %d" % (len(todays), mt))
    mdl = rc.get("max_daily_loss_usd")
    if mdl:
        pnl = sum(float(t.get("pnl_usd", 0)) for t in todays)
        worst = pnl - (size.get("loss_at_stop_usd", 0) if size else 0)
        add("Tagesverlust-Limit", worst >= -float(mdl) - 0.005,
            "heute %.2f USD, im Stop-Fall %.2f USD (Limit -%.2f USD)" % (pnl, worst, float(mdl)))
    else:
        add("Tagesverlust-Limit", False, "max_daily_loss_usd nicht gesetzt", hard=False)
    spread = float(size.get("spread", 0)) if size else 0
    share = float(rc.get("max_spread_share_of_stop", 0.2))
    if spread:
        add("Spread im Verhaeltnis zum Stop", spread <= share * plan["risk_per_unit"] + EPS,
            "Spread %s = %.0f %% des Stop-Abstands (max %.0f %%)" % (spread, 100 * spread / plan["risk_per_unit"], 100 * share))
    blocked = [c for c in checks if c["hard"] and not c["ok"]]
    return {"result": "BLOCK" if blocked else "PASS", "checks": checks}


def cmd_risk(args):
    cfg = load_config(args)
    plan = read_json(os.path.join(args.dir, "plan.json"))
    spath = os.path.join(args.dir, "size.json")
    size = read_json(spath) if os.path.exists(spath) else None
    res = risk_check(cfg, plan, size, load_journal(os.path.join(args.dir, "journal.json")), parse_now(args.now))
    if args.format == "json":
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        for c in res["checks"]:
            mark = "ok   " if c["ok"] else ("BLOCK" if c["hard"] else "WARN ")
            print("  %s %-32s %s" % (mark, c["check"], c["detail"]))
        print(res["result"])
        if res["result"] == "PASS":
            print("PASS ist eine Regelpruefung, keine Empfehlung. Die Order gibst du selbst in MT5 ein.")
    return 0 if res["result"] == "PASS" else 2


def cmd_journal(args):
    path = os.path.join(args.dir, "journal.json")
    trades = load_journal(path)
    if args.action == "add":
        if args.pnl is None or not args.instrument:
            raise UserError("journal add braucht --instrument und --pnl")
        day = args.date or dt.datetime.now(UTC).date().isoformat()
        trades.append({"date": day, "instrument": args.instrument, "pnl_usd": float(args.pnl), "note": args.note or ""})
        write_json(path, {"trades": trades})
    rows = [t for t in trades if not args.date or t.get("date") == args.date]
    if args.format == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for t in rows:
            print("%s  %-7s %+9.2f USD  %s" % (t.get("date"), t.get("instrument"), float(t.get("pnl_usd", 0)), t.get("note", "")))
        print("%d Eintraege, Summe %+.2f USD" % (len(rows), sum(float(t.get("pnl_usd", 0)) for t in rows)))
    return 0


# --------------------------------------------------------------------------
# fetch / mt5-import
# --------------------------------------------------------------------------

def cmd_fetch(args):
    cfg = load_config(args)
    sym = instrument_cfg(cfg, args.instrument).get("yahoo_symbol")
    if not sym:
        raise UserError("Kein yahoo_symbol fuer %s in der Config" % args.instrument)
    doc = normalize(fetch_yahoo(sym, args.range), args.instrument, "yahoo:" + sym, PROXY_NOTE % sym)
    out = args.out or os.path.join(args.dir, "data", "%s-5m.json" % args.instrument)
    write_json(out, doc)
    b = doc["bars"]
    print("%d Kerzen %s (%s) gespeichert: %s" % (len(b), args.instrument, sym, out))
    if b:
        print("Zeitraum %s bis %s UTC" % (dt.datetime.fromtimestamp(b[0][0], UTC).strftime("%Y-%m-%d %H:%M"),
                                          dt.datetime.fromtimestamp(b[-1][0], UTC).strftime("%Y-%m-%d %H:%M")))
    print(doc["note"])
    return 0


def cmd_mt5_import(args):
    try:
        with open(args.file, encoding="utf-8-sig") as fh:
            text = fh.read()
    except UnicodeDecodeError:
        with open(args.file, encoding="utf-16") as fh:
            text = fh.read()
    except FileNotFoundError:
        raise UserError("Datei fehlt: %s" % args.file)
    bars, step = parse_mt5_csv(text, args.server_offset)
    doc = normalize(bars, args.instrument, "mt5:" + os.path.basename(args.file),
                    "MT5-Export, Serverzeit-Offset %s" % args.server_offset)
    out = args.out or os.path.join(args.dir, "data", "%s-5m.json" % args.instrument)
    write_json(out, doc)
    print("%d M5-Kerzen (aus %s) gespeichert: %s" % (len(doc["bars"]), "M1" if step == 60 else "M5", out))
    return 0


# --------------------------------------------------------------------------
# selftest: offline, synthetische Daten
# --------------------------------------------------------------------------

def _selftest_config():
    return {
        "account": {"currency": "USD", "balance_usd": 10000},
        "risk": {"risk_per_trade_usd": 50, "max_daily_loss_usd": 150, "max_trades_per_day": 3,
                 "min_reward_risk": 1.5, "max_signal_age_bars": 2, "max_spread_share_of_stop": 0.2},
        "instruments": {"TEST": {"contract_size": 100, "min_lot": 0.01, "lot_step": 0.01, "max_lot": 50,
                                 "price_decimals": 2, "spread": 0, "leverage": 20}},
        "sessions": {"ny": {"tz": "America/New_York", "open": "09:30", "or_minutes": 15,
                            "no_entries_after": "11:30", "flat_by": "15:55"},
                     "london": {"tz": "Europe/London", "open": "08:00", "or_minutes": 15,
                                "no_entries_after": "11:00", "flat_by": "16:00"}},
    }


def _synthetic_bars(last_day, n_days=35, seed=7):
    """Synthetische 5-Minuten-Kerzen 05:00-21:00 UTC an Werktagen. Nur fuer den Selbsttest."""
    rng = random.Random(seed)
    bars, p = {}, 100.0
    d = last_day - dt.timedelta(days=n_days * 7 // 5 + 3)
    while d <= last_day:
        if d.weekday() < 5:
            t0 = int(dt.datetime(d.year, d.month, d.day, 5, 0, tzinfo=UTC).timestamp())
            for t in range(t0, t0 + 16 * 3600, BAR):
                o = p
                c = o * (1 + rng.gauss(0, 0.0015))
                h = max(o, c) * (1 + abs(rng.gauss(0, 0.0007)))
                l = min(o, c) * (1 - abs(rng.gauss(0, 0.0007)))
                bars[t] = (o, h, l, c)
                p = c
        d += dt.timedelta(days=1)
    return bars


def selftest():
    fails = []

    def check(name, cond, info=""):
        print("  %s %s%s" % ("ok  " if cond else "FAIL", name, (" (" + str(info) + ")") if not cond and info else ""))
        if not cond:
            fails.append(name)

    print("Zeitzonen")
    check("NY-Open 06.03.2026 = 14:30 UTC (Winterzeit)",
          local_to_epoch(dt.date(2026, 3, 6), "09:30", "America/New_York") == int(dt.datetime(2026, 3, 6, 14, 30, tzinfo=UTC).timestamp()))
    check("NY-Open 09.03.2026 = 13:30 UTC (US-Sommerzeit seit 08.03.)",
          local_to_epoch(dt.date(2026, 3, 9), "09:30", "America/New_York") == int(dt.datetime(2026, 3, 9, 13, 30, tzinfo=UTC).timestamp()))
    check("London-Open 27.03.2026 = 08:00 UTC",
          local_to_epoch(dt.date(2026, 3, 27), "08:00", "Europe/London") == int(dt.datetime(2026, 3, 27, 8, 0, tzinfo=UTC).timestamp()))
    check("London-Open 30.03.2026 = 07:00 UTC (BST seit 29.03.)",
          local_to_epoch(dt.date(2026, 3, 30), "08:00", "Europe/London") == int(dt.datetime(2026, 3, 30, 7, 0, tzinfo=UTC).timestamp()))
    check("NY-Open 19.10.2026 = 15:30 Uhr DE",
          hm(local_to_epoch(dt.date(2026, 10, 19), "09:30", "America/New_York"), "Europe/Berlin") == "15:30")

    cfg = _selftest_config()
    ic, sc = cfg["instruments"]["TEST"], cfg["sessions"]["ny"]
    day = dt.date(2026, 10, 19)
    bars = _synthetic_bars(day)
    fr = session_frame(day, sc)
    op = fr["open"]
    planted = [(100.0, 101.0, 99.0, 100.5), (100.5, 101.5, 99.5, 101.0), (101.0, 101.8, 100.2, 101.2),
               (101.2, 101.7, 100.9, 101.5), (101.5, 102.3, 101.4, 102.1)]
    for i, b in enumerate(planted):
        bars[op + i * BAR] = b

    print("entry (Long-Breakout, eingepflanzt)")
    r = evaluate_entry(bars, fr, op + 4 * BAR + 120)
    check("vor Kerzenschluss: wartend", r["status"] == "wartend", r["status"])
    r = evaluate_entry(bars, fr, op + 5 * BAR)
    check("nach Kerzenschluss: ausgeloest long", r["status"] == "ausgeloest" and r["direction"] == "long", r)
    check("Range 99.00 bis 101.80", abs(r["or_high"] - 101.8) < EPS and abs(r["or_low"] - 99.0) < EPS)
    check("Einstieg 102.10 um 15:55 Uhr DE", abs(r["entry"] - 102.1) < EPS and hm(r["entry_t"], "Europe/Berlin") == "15:55")
    check("vor Eroeffnung", evaluate_entry(bars, fr, op - 60)["status"] == "vor-eroeffnung")
    check("Range bildet sich", evaluate_entry(bars, fr, op + 2 * BAR)["status"] == "range-bildet-sich")

    print("entry (Short-Breakout)")
    sb = dict(bars)
    sb[op + 3 * BAR] = (101.2, 101.3, 98.5, 98.8)
    rs = evaluate_entry(sb, fr, op + 4 * BAR)
    check("ausgeloest short bei 98.80", rs["status"] == "ausgeloest" and rs["direction"] == "short" and abs(rs["entry"] - 98.8) < EPS, rs)

    print("exit")
    info = dict(r, instrument="TEST", session="ny")
    plan = make_plan(ic, sc, info, "or-mid", "2R")
    check("Stop Range-Mitte 100.40", abs(plan["stop"] - 100.4) < EPS, plan["stop"])
    check("Ziel 2R = 105.50", abs(plan["target"] - 105.5) < EPS, plan["target"])
    sinfo = dict(rs, instrument="TEST", session="ny")
    splan = make_plan(ic, sc, sinfo, "or-opposite", "1.5R")
    check("Short: Stop am Range-Hoch 101.80", abs(splan["stop"] - 101.8) < EPS, splan["stop"])
    check("Short: Ziel 1.5R = 94.30", abs(splan["target"] - 94.3) < EPS, splan["target"])
    try:
        make_plan(ic, sc, info, "price:103", "2R")
        check("Stop auf falscher Seite wird abgelehnt", False)
    except UserError:
        check("Stop auf falscher Seite wird abgelehnt", True)

    print("size")
    sz = size_position(cfg, plan)
    check("0.29 Lots bei 50 USD Risiko, 1.70 Abstand, Kontrakt 100", abs(sz["lots"] - 0.29) < EPS, sz["lots"])
    check("Verlust am Stop 49.30 USD", abs(sz["loss_at_stop_usd"] - 49.3) < 0.001, sz.get("loss_at_stop_usd"))
    wide = dict(plan, risk_per_unit=60.0)
    check("zu weiter Stop wird abgelehnt", size_position(cfg, wide)["refusal"] is not None)
    cfg2 = json.loads(json.dumps(cfg))
    cfg2["instruments"]["TEST"]["contract_size"] = None
    try:
        size_position(cfg2, plan)
        check("fehlende Kontraktgroesse stoppt", False)
    except UserError:
        check("fehlende Kontraktgroesse stoppt", True)

    print("risk")
    now = r["entry_t"] + 60
    rk = risk_check(cfg, plan, sz, [], now)
    check("PASS bei sauberem Plan", rk["result"] == "PASS", [c for c in rk["checks"] if not c["ok"]])
    full = [{"date": day.isoformat(), "pnl_usd": -10}] * 3
    check("BLOCK bei 3 Trades heute", risk_check(cfg, plan, sz, full, now)["result"] == "BLOCK")
    loss = [{"date": day.isoformat(), "pnl_usd": -120}]
    check("BLOCK am Tagesverlust-Limit", risk_check(cfg, plan, sz, loss, now)["result"] == "BLOCK")
    check("BLOCK nach Einstiegsfenster", risk_check(cfg, plan, sz, [], fr["last_entry"] + 60)["result"] == "BLOCK")

    print("replay")
    pool = build_pool(bars, sc, day)
    check("Pool >= 20 Sessions", len(pool) >= 20, len(pool))
    k = (plan["entry_t"] - op) // BAR
    a = run_replays(pool, k, plan["entry"], plan["stop"], plan["target"], "long", 2000, 19)
    b = run_replays(pool, k, plan["entry"], plan["stop"], plan["target"], "long", 2000, 19)
    check("reproduzierbar mit gleichem Seed", a == b)
    check("Anteile summieren sich auf 100 %", abs(a["target_pct"] + a["stop_pct"] + a["neither_pct"] - 100) < 1e-6)
    hst = history(pool, plan)
    check("Historie zaehlt alle Sessions",
          hst["long"]["fired"] + hst["short"]["fired"] + hst["no_trigger"] <= hst["sessions"], hst)
    check("Urteil Muenzwurf bei 30/30 und 1R", verdict(30, 30, 1.0).startswith("Nahe am Muenzwurf"))
    check("Urteil Break-even bei 25/50 und 2R", verdict(25, 50, 2.0).startswith("Nahe am Break-even"))

    print("mt5-import")
    csv_text = ("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n"
                + "".join("2026.10.19\t16:%02d:00\t1.0\t%.1f\t0.5\t1.%d\t10\t0\t5\n" % (m, 2.0 + m, m) for m in range(30, 40)))
    mb, step = parse_mt5_csv(csv_text, "ny-close")
    t1330 = int(dt.datetime(2026, 10, 19, 13, 30, tzinfo=UTC).timestamp())
    check("M1 erkannt und zu M5 verdichtet", step == 60 and len(mb) == 2, (step, len(mb)))
    check("Serverzeit 16:30 (ny-close, US-Sommerzeit) = 13:30 UTC", mb[0][0] == t1330, mb[0][0])
    check("M5-Hoch ist Maximum der M1-Kerzen", abs(mb[0][2] - 36.0) < EPS and abs(mb[0][4] - 1.34) < EPS, mb[0])
    try:
        parse_mt5_csv(csv_text, None)
        check("fehlender Serverzeit-Offset stoppt", False)
    except UserError:
        check("fehlender Serverzeit-Offset stoppt", True)

    print("")
    print("%d Fehler" % len(fails) if fails else "Alle Pruefungen bestanden.")
    return 1 if fails else 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(description="ORB-Analyse fuer XAU/USD und NAS100 (CFD). Keine Orders.")
    p.add_argument("--version", action="version", version=VERSION)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", default="cfd", help="Arbeitsordner (Standard: cfd)")
    common.add_argument("--config", help="Config-Datei (Standard: <dir>/config.json)")
    common.add_argument("--format", choices=("text", "json"), default="text")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("fetch", parents=[common], help="Yahoo-Kerzen laden (Proxy)")
    s.add_argument("--instrument", required=True)
    s.add_argument("--range", default="60d")
    s.add_argument("--out")
    s.set_defaults(func=cmd_fetch)

    s = sub.add_parser("mt5-import", parents=[common], help="MT5-CSV-Export einlesen")
    s.add_argument("file")
    s.add_argument("--instrument", required=True)
    s.add_argument("--server-offset", help="'ny-close' (UTC+2/+3) oder Stunden, z. B. 2")
    s.add_argument("--out")
    s.set_defaults(func=cmd_mt5_import)

    s = sub.add_parser("entry", parents=[common], help="Breakout-Status")
    s.add_argument("--instrument", required=True)
    s.add_argument("--session", required=True)
    s.add_argument("--data", help="Kerzen-Datei (fetch/mt5-import); sonst live Yahoo")
    s.add_argument("--now", help="'YYYY-MM-DD HH:MM' deutsche Zeit, zum Nachspielen")
    s.add_argument("--write", action="store_true")
    s.set_defaults(func=cmd_entry)

    s = sub.add_parser("exit", parents=[common], help="Stop und Ziel planen")
    s.add_argument("--stop", default="or-mid", help="or-mid | or-opposite | atr:K | pct:X | price:X")
    s.add_argument("--target", default="2R", help="z. B. 2R, 1.5R, price:X")
    s.add_argument("--entry", type=float, help="Einstieg vorplanen statt entry.json")
    s.add_argument("--instrument")
    s.add_argument("--session")
    s.add_argument("--direction", choices=("long", "short"))
    s.add_argument("--or-high", type=float)
    s.add_argument("--or-low", type=float)
    s.add_argument("--day")
    s.add_argument("--data")
    s.add_argument("--now")
    s.add_argument("--write", action="store_true")
    s.set_defaults(func=cmd_exit)

    s = sub.add_parser("size", parents=[common], help="Lots berechnen")
    s.add_argument("--plan")
    s.add_argument("--balance", type=float, help="Kontostand USD (fuer risk_per_trade_pct)")
    s.add_argument("--write", action="store_true")
    s.set_defaults(func=cmd_size)

    s = sub.add_parser("replay", parents=[common], help="10.000 Durchlaeufe + Historie")
    s.add_argument("--plan")
    s.add_argument("--data")
    s.add_argument("--replays", type=int, default=10000)
    s.add_argument("--seed", type=int, default=19)
    s.add_argument("--window", type=int, default=2)
    s.add_argument("--min-sessions", type=int, default=20)
    s.add_argument("--write", action="store_true")
    s.set_defaults(func=cmd_replay)

    s = sub.add_parser("risk", parents=[common], help="PASS oder BLOCK")
    s.add_argument("--now")
    s.set_defaults(func=cmd_risk)

    s = sub.add_parser("journal", parents=[common], help="Tagesergebnisse")
    s.add_argument("action", choices=("add", "show"))
    s.add_argument("--instrument")
    s.add_argument("--pnl", type=float)
    s.add_argument("--date")
    s.add_argument("--note")
    s.set_defaults(func=cmd_journal)

    s = sub.add_parser("selftest", help="Offline-Selbsttest")
    s.set_defaults(func=lambda a: selftest())
    return p


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        return 1
    try:
        return args.func(args)
    except UserError as e:
        print("Fehler: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
