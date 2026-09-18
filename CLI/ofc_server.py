#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

DATA: list[dict] = []

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

CANDIDATES = [
    REPO_ROOT / "data" / "Open-food-calories.json",
    REPO_ROOT / "Open-food-calories.json",
    SCRIPT_DIR / "data" / "Open-food-calories.json",
    Path("data/Open-food-calories.json"),
    Path("Open-food-calories.json"),
]


def load_data(file_arg: str | None) -> list[dict]:
    paths = [Path(file_arg)] if file_arg else CANDIDATES
    for fp in paths:
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(
        "Fichier introuvable. Essayé : " + ", ".join(str(p) for p in paths)
    )


def entry_matches(item, q, lang, category, ftype):
    if category and item.get("category") != category:
        return False
    if ftype and item.get("type") != ftype:
        return False
    if not q:
        return True
    q = q.lower()
    n = item.get("name")
    if isinstance(n, dict):
        fr, en = (n.get("fr") or "").lower(), (n.get("en") or "").lower()
        if lang == "fr":
            return q in fr
        if lang == "en":
            return q in en
        return q in fr or q in en
    return q in str(n).lower()


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        parts = [p for p in parsed.path.split("/") if p]

        if not parts or parts[0] == "all":
            self._send_json(DATA)
            return

        if parts[0] == "categories":
            counts = {}
            for it in DATA:
                c = it.get("category", "uncategorized")
                counts[c] = counts.get(c, 0) + 1
            self._send_json(counts)
            return

        if parts[0] == "search":
            q = qs.get("q", [""])[0]
            lang = qs.get("lang", ["any"])[0]
            category = qs.get("category", [None])[0]
            ftype = qs.get("type", [None])[0]
            limit = int(qs.get("limit", ["20"])[0])
            results = [it for it in DATA if entry_matches(it, q, lang, category, ftype)]
            self._send_json(results[:limit])
            return

        if parts[0] == "food" and len(parts) == 2:
            found = next((it for it in DATA if it.get("id") == parts[1]), None)
            if found:
                self._send_json(found)
            else:
                self._send_json({"error": f"id '{parts[1]}' introuvable"}, status=404)
            return

        self._send_json({"error": "route inconnue", "routes": ["/all", "/search", "/food/<id>", "/categories"]}, status=404)


def main():
    global DATA
    parser = argparse.ArgumentParser(description="Mini API REST Open-Food-Calories")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--file", help="Chemin vers Open-food-calories.json")
    args = parser.parse_args()

    DATA = load_data(args.file)
    print(f"✅ {len(DATA)} aliments chargés.")
    print(f"🚀 API disponible sur http://localhost:{args.port}  (Ctrl+C pour arrêter)")
    print("   Exemples : /all  /search?q=pizza  /food/riz-blanc-cuit  /categories")

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur.")


if __name__ == "__main__":
    main()
