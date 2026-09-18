#!/usr/bin/env python3
"""
ofc_cli.py — CLI pour Open-Food-Calories (format V2)

Corrige les problèmes du repo actuel :
- README/API.md pointent vers "data/food.json" (V1, n'existe plus) -> ici on lit
  data/Open-food-calories.json (V2, le seul à jour), avec fallback auto sur
  l'ancien nom si jamais tu renommes le fichier.
- Le format V2 a "name": {"fr":..., "en":...} au lieu de "name"/"english_name"
  à plat -> ce script gère nativement le format imbriqué.

Usage (depuis la racine du repo, ou avec --file) :

    python3 ofc_cli.py search pizza
    python3 ofc_cli.py search poulet --lang fr --category meat
    python3 ofc_cli.py get riz-blanc-cuit
    python3 ofc_cli.py categories
    python3 ofc_cli.py stats
    python3 ofc_cli.py search "" --category fruits --limit 20 --json

Aucune dépendance externe (stdlib uniquement) : marche direct avec `python3`.
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_CANDIDATES = [
    "data/Open-food-calories.json",   # V2, à jour
    "Open-food-calories.json",
    "data/food.json",                  # ancien nom référencé (à éviter)
]


def load_data(file_arg: str | None) -> list[dict]:
    paths = [file_arg] if file_arg else DEFAULT_CANDIDATES
    for p in paths:
        if not p:
            continue
        fp = Path(p)
        if fp.exists():
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                print(f"⚠️  {fp} ne contient pas une liste JSON valide.", file=sys.stderr)
                sys.exit(1)
            return data
    print(
        "❌ Fichier de données introuvable. Essayé : "
        + ", ".join(p for p in paths if p)
        + "\nPrécise le chemin avec --file /chemin/vers/Open-food-calories.json",
        file=sys.stderr,
    )
    sys.exit(1)


def entry_name(item: dict, lang: str = "fr") -> str:
    n = item.get("name")
    if isinstance(n, dict):
        return n.get(lang) or n.get("fr") or n.get("en") or item.get("id", "?")
    return str(n) if n else item.get("id", "?")


def matches(item: dict, query: str, lang: str, category: str | None,
            ftype: str | None) -> bool:
    if category and item.get("category") != category:
        return False
    if ftype and item.get("type") != ftype:
        return False
    if not query:
        return True
    q = query.lower()
    n = item.get("name")
    if isinstance(n, dict):
        fr = (n.get("fr") or "").lower()
        en = (n.get("en") or "").lower()
        if lang == "fr":
            return q in fr
        if lang == "en":
            return q in en
        return q in fr or q in en  # lang == "any"
    return q in str(n).lower()


def print_entry(item: dict, verbose: bool = False):
    name = entry_name(item, "fr")
    en = entry_name(item, "en")
    emoji = item.get("emoji", "")
    kcal = item.get("kcal_per_100g", "?")
    print(f"{emoji} {name} ({en}) — {kcal} kcal/100g  [id={item.get('id')}]")
    if verbose:
        for k in ("category", "state", "type", "protein_g", "fat_g",
                   "carbs_g", "fiber_g", "sugars_g", "salt_g", "source",
                   "confidence", "weight_per_unit"):
            if k in item:
                print(f"    {k}: {item[k]}")


def cmd_search(args):
    data = load_data(args.file)
    results = [it for it in data if matches(it, args.query, args.lang,
                                             args.category, args.type)]
    results = results[: args.limit]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if not results:
        print("Aucun résultat.")
        return
    for it in results:
        print_entry(it, verbose=args.verbose)


def cmd_get(args):
    data = load_data(args.file)
    found = next((it for it in data if it.get("id") == args.id), None)
    if not found:
        print(f"❌ Aucun aliment avec id='{args.id}'.", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        print_entry(found, verbose=True)


def cmd_categories(args):
    data = load_data(args.file)
    counts: dict[str, int] = {}
    for it in data:
        c = it.get("category", "uncategorized")
        counts[c] = counts.get(c, 0) + 1
    for c, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"{c:15s} {n}")


def cmd_stats(args):
    data = load_data(args.file)
    total = len(data)
    with_macros = sum(1 for it in data if it.get("protein_g") is not None)
    by_conf: dict[str, int] = {}
    for it in data:
        c = it.get("confidence", "unknown")
        by_conf[c] = by_conf.get(c, 0) + 1
    print(f"Total : {total} entrées")
    print(f"Avec macronutriments renseignés : {with_macros} ({with_macros*100//total}%)")
    print("Confiance :")
    for c, n in sorted(by_conf.items(), key=lambda x: -x[1]):
        print(f"  {c:10s} {n}")


def main():
    parser = argparse.ArgumentParser(description="CLI Open-Food-Calories (V2)")
    parser.add_argument("--file", help="Chemin vers Open-food-calories.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Rechercher des aliments")
    p_search.add_argument("query", help="Terme recherché (vide = tout lister)")
    p_search.add_argument("--lang", choices=["fr", "en", "any"], default="any")
    p_search.add_argument("--category")
    p_search.add_argument("--type", choices=["solid", "liquid", "unit"])
    p_search.add_argument("--limit", type=int, default=15)
    p_search.add_argument("--json", action="store_true")
    p_search.add_argument("--verbose", "-v", action="store_true")
    p_search.set_defaults(func=cmd_search)

    p_get = sub.add_parser("get", help="Obtenir un aliment par id")
    p_get.add_argument("id")
    p_get.add_argument("--json", action="store_true")
    p_get.set_defaults(func=cmd_get)

    p_cat = sub.add_parser("categories", help="Lister les catégories et leur volume")
    p_cat.set_defaults(func=cmd_categories)

    p_stats = sub.add_parser("stats", help="Statistiques globales de la base")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
