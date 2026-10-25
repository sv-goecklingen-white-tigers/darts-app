"""Holt die aktuelle Tabelle der Bezirksoberliga 1 von der BDL und schreibt sie in tabelle.json.

Aufruf:  python tabelle_holen.py
Eigene Datei, damit das Hochladen von daten.json die Tabelle nicht überschreibt.
"""
import html
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

URL = "https://www.badischedartliga.de/results/leagueTable_bzo1.html"
DATEI = Path(__file__).with_name("tabelle.json")
ZONE = {"promote_ol": "auf", "promote_kl": "ab"}


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def holen():
    with urllib.request.urlopen(URL, timeout=20) as r:
        seite = r.read().decode("utf-8", "replace")
    zeilen = []
    for cls, inhalt in re.findall(r'<tr class="(promote_\w+)">(.*?)</tr>', seite, re.S):
        z = [text(td) for td in re.findall(r"<td[^>]*>(.*?)</td>", inhalt, re.S)]
        if len(z) < 9:
            continue
        zeilen.append({
            "pl": int(z[0].rstrip(".")), "team": z[1], "sp": int(z[2]),
            "g": int(z[3]), "u": int(z[4]), "v": int(z[5]),
            "sets": z[6].replace(" ", ""), "legs": z[7].replace(" ", ""),
            "pkt": int(z[8]), "str": z[9] if len(z) > 9 else "",
            "zone": ZONE.get(cls, ""),
        })
    if not zeilen:
        raise SystemExit("Keine Tabelle gefunden - hat sich die BDL-Seite geändert?")
    return zeilen


def main():
    tabelle = {"stand": datetime.now().strftime("%d.%m.%Y, %H:%M Uhr"), "quelle": URL, "rows": holen()}
    DATEI.write_text(json.dumps(tabelle, ensure_ascii=False, indent=1), encoding="utf-8")
    for z in tabelle["rows"]:
        print(f'{z["pl"]:>2}. {z["team"]:<32} {z["sp"]} Sp.  {z["pkt"]} Pkt.')


if __name__ == "__main__":
    main()
