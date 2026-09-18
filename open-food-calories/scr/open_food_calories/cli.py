import argparse
import json
import sys

from .loader import load_data

SORT_FIELDS = {
    "name": lambda it, lang: entry_name(it, lang).lower(),
    "kcal": lambda it, lang: _num(it.get("kcal_per_100g")),
    "protein": lambda it, lang: _num(it.get("protein_g")),
    "fat": lambda it, lang: _num(it.get("fat_g")),
    "carbs": lambda it, lang: _num(it.get("carbs_g")),
}


def _num(value):
    return value if isinstance(value, (int, float)) else -1


def entry_name(item, lang="fr"):
    n = item.get("name")
    if isinstance(n, dict):
        return n.get(lang) or n.get("fr") or n.get("en") or item.get("id", "?")
    return str(n) if n else item.get("id", "?")


def matches(item, query, lang, category, ftype):
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
        return q in fr or q in en
    return q in str(n).lower()


def print_entry(item, lang="any", verbose=False):
    name_fr = entry_name(item, "fr")
    name_en = entry_name(item, "en")
    emoji = item.get("emoji", "")
    kcal = item.get("kcal_per_100g", "?")
    if lang == "fr":
        label = name_fr
    elif lang == "en":
        label = name_en
    else:
        label = f"{name_fr} ({name_en})"
    print(f"{emoji} {label} - {kcal} kcal/100g  [id={item.get('id')}]")
    if verbose:
        for k in ("category", "state", "type", "protein_g", "fat_g",
                   "carbs_g", "fiber_g", "sugars_g", "salt_g", "source",
                   "confidence", "weight_per_unit"):
            if k in item:
                print(f"    {k}: {item[k]}")


def cmd_search(args):
    data = load_data(refresh=args.refresh, offline=args.offline)
    results = [it for it in data if matches(it, args.query, args.lang,
                                             args.category, args.type)]
    if args.sort:
        key_fn = SORT_FIELDS[args.sort]
        results.sort(key=lambda it: key_fn(it, args.lang), reverse=args.desc)
    results = results[: args.limit]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if not results:
        print("No results.")
        return
    for it in results:
        print_entry(it, lang=args.lang, verbose=args.verbose)


def cmd_get(args):
    data = load_data(refresh=args.refresh, offline=args.offline)
    found = next((it for it in data if it.get("id") == args.id), None)
    if not found:
        print(f"No entry with id '{args.id}'.", file=sys.stderr)
        sys.exit(1)
    if args.json:
        print(json.dumps(found, ensure_ascii=False, indent=2))
    else:
        print_entry(found, verbose=True)


def cmd_categories(args):
    data = load_data(refresh=args.refresh, offline=args.offline)
    counts = {}
    for it in data:
        c = it.get("category", "uncategorized")
        counts[c] = counts.get(c, 0) + 1
    for c, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"{c:15s} {n}")


def cmd_stats(args):
    data = load_data(refresh=args.refresh, offline=args.offline)
    total = len(data)
    with_macros = sum(1 for it in data if it.get("protein_g") is not None)
    by_conf = {}
    for it in data:
        c = it.get("confidence", "unknown")
        by_conf[c] = by_conf.get(c, 0) + 1
    print(f"Total: {total} entries")
    if total:
        print(f"With macronutrients: {with_macros} ({with_macros * 100 // total}%)")
    print("Confidence:")
    for c, n in sorted(by_conf.items(), key=lambda x: -x[1]):
        print(f"  {c:10s} {n}")


def _add_common_args(p):
    p.add_argument("--json", action="store_true", help="Output raw JSON")
    p.add_argument("--refresh", action="store_true",
                    help="Force re-download of the dataset instead of using the cache")
    p.add_argument("--offline", action="store_true",
                    help="Use the cached or bundled dataset only, never hit the network")


def main():
    parser = argparse.ArgumentParser(
        prog="open-food-calories",
        description="Search the Open-Food-Calories database from the command line",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search for foods")
    p_search.add_argument("query", nargs="?", default="",
                            help="Search term (empty lists everything matching the filters)")
    p_search.add_argument("--lang", choices=["fr", "en", "any"], default="any",
                            help="Language to search and display (default: any)")
    p_search.add_argument("--category")
    p_search.add_argument("--type", choices=["solid", "liquid", "unit"])
    p_search.add_argument("--sort", choices=list(SORT_FIELDS.keys()))
    p_search.add_argument("--desc", action="store_true", help="Sort in descending order")
    p_search.add_argument("--limit", type=int, default=15)
    p_search.add_argument("--verbose", "-v", action="store_true")
    _add_common_args(p_search)
    p_search.set_defaults(func=cmd_search)

    p_get = sub.add_parser("get", help="Get a food by id")
    p_get.add_argument("id")
    _add_common_args(p_get)
    p_get.set_defaults(func=cmd_get)

    p_cat = sub.add_parser("categories", help="List categories and their counts")
    _add_common_args(p_cat)
    p_cat.set_defaults(func=cmd_categories)

    p_stats = sub.add_parser("stats", help="Show database statistics")
    _add_common_args(p_stats)
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
