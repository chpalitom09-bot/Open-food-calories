# Open-Food-Calories

A structured JSON database of 5,000+ foods, dishes, and ingredients, with calories and macronutrients, in French and English.

Live demo: https://chpalitom09-bot.github.io/Open-food-calories/

## Table of contents

- [Overview](#overview)
- [Repository structure](#repository-structure)
- [Data format (schema v2)](#data-format-schema-v2)
- [Data quality report](#data-quality-report)
- [Using the raw JSON](#using-the-raw-json)
- [Command-line tool](#command-line-tool)
- [Local REST API](#local-rest-api)
- [Contributing](#contributing)
- [License](#license)

## Overview

- Coverage: 5,037 entries
- Structure: 100% schema-validated, bilingual (French / English)
- Accuracy: cross-referenced against CIQUAL and USDA reference values

| Food | Open-Food-Calories (kcal/100g) | Reference (CIQUAL/USDA) | Estimated gap |
| :--- | :--- | :--- | :--- |
| Riz blanc (cru) | 350 | 350 | 0% |
| Riz blanc (cuit) | 130 | 130 | 0% |
| Pates (crues) | 350 | 353 | ~1% |
| Pates (cuites) | 150 | 158 | ~5% |
| Blanc de poulet | 110 | 110-120 | ~4% |
| Boeuf hache 5% | 125 | 125-129 | ~2% |
| Huile de noisette | 884 | 900 | ~1.7% |
| Magnum (batonnet) | 300 | 310 | ~3% |
| Pain au lait | 300 | 320-340 | ~9% |
| Saute de porc aux legumes | 165 | 150-170 | ~3% |

## Repository structure

```
.
├── data/
│   ├── Open-food-calories.json          # current dataset (schema v2)
│   └── Open-food-calories-10_03_26.json # legacy snapshot (schema v1)
├── data-schema.json                     # JSON Schema for the v2 format
├── CLI/
│   ├── ofc_cli.py                       # command-line search tool
│   └── ofc_server.py                    # local REST API server
├── examples/
│   ├── app.py                           # Streamlit demo app
│   └── chek_data.py                     # duplicate-check script
├── index.html                           # static web app (GitHub Pages)
├── API.md                               # API reference
├── CONTRIBUTING.md                      # contribution guidelines
└── LICENSE
```

The dataset that is actively maintained and used by `index.html` and every tool in this repository is `data/Open-food-calories.json`. The `-10_03_26` file is kept only as a historical snapshot of the older, flat schema and should not be used for new integrations.

## Data format (schema v2)

Every entry in `data/Open-food-calories.json` follows the schema defined in `data-schema.json`.

```json
{
  "id": "riz-blanc-cuit",
  "name": {
    "fr": "Riz blanc (cuit)",
    "en": "White rice (cooked)"
  },
  "category": "grains",
  "state": "cooked",
  "type": "solid",
  "kcal_per_100g": 130,
  "protein_g": 2.7,
  "fat_g": 0.3,
  "carbs_g": 28.0,
  "fiber_g": null,
  "sugars_g": null,
  "saturated_fat_g": null,
  "salt_g": null,
  "alcohol_g": null,
  "weight_per_unit": null,
  "emoji": "rice",
  "source": "CIQUAL",
  "confidence": "high"
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string | Stable identifier, slug form. Never changes once published. |
| `name.fr` | string | Name in French. |
| `name.en` | string | Name in English. |
| `category` | string | One of: `beverages`, `dairy_eggs`, `meat`, `seafood`, `fruits`, `vegetables`, `grains`, `legumes`, `nuts_seeds`, `fats_oils`, `sweets`, `condiments`, `prepared`, `uncategorized`. |
| `state` | string or null | One of: `raw`, `cooked`, `fried`, `dried`, `canned`, or null. |
| `type` | string | One of: `solid`, `liquid`, `unit`. |
| `kcal_per_100g` | number | Calories per 100g or 100ml. |
| `protein_g` | number or null | Grams of protein per 100g/ml. |
| `fat_g` | number or null | Grams of fat per 100g/ml. |
| `carbs_g` | number or null | Grams of carbohydrates per 100g/ml. |
| `fiber_g` | number or null | Grams of fiber per 100g/ml. |
| `sugars_g` | number or null | Grams of sugar per 100g/ml. |
| `saturated_fat_g` | number or null | Grams of saturated fat per 100g/ml. |
| `salt_g` | number or null | Grams of salt per 100g/ml. |
| `alcohol_g` | number or null | Grams of alcohol per 100g/ml. |
| `weight_per_unit` | number or null | Average weight in grams of one piece, when the food is typically counted rather than weighed (an egg, an apple). Null if the food is measured by weight. |
| `emoji` | string | Representative icon. |
| `source` | string or null | Origin of the values: `CIQUAL`, `USDA`, `OFF:<barcode>`, `estimated`, or `legacy`. |
| `confidence` | string | One of: `high`, `medium`, `low`, `unknown`. |

This schema is a breaking change from the original flat format (`name` as a plain string, `english_name`, no `id`, no macronutrients). Any integration built against the old shape needs to be updated to read `name.fr` / `name.en` and, where relevant, the new macronutrient fields.

## Data quality report

Total entries: 5,037

Macronutrient coverage:

- Inherited from the original file: 1,010
- Added from CIQUAL/USDA: 121
- Still missing (null): 3,906

By confidence level:

- `unknown`: 3,906
- `medium`: 1,010
- `high`: 121

By category:

| Category | Entries |
| :--- | :--- |
| uncategorized | 779 |
| beverages | 679 |
| fruits | 542 |
| vegetables | 534 |
| meat | 425 |
| dairy_eggs | 406 |
| grains | 367 |
| sweets | 338 |
| condiments | 271 |
| seafood | 255 |
| nuts_seeds | 148 |
| legumes | 137 |
| prepared | 133 |
| fats_oils | 23 |

Known issues:

- Near-duplicate French names: 776 entries share a name or a close variant (for example multiple cheddar, mozzarella, or oil entries with numeric suffixes). These are distinct products, not errors, but deduplication tooling should account for this.
- Atwater-inconsistent entries: 119 entries where the declared calorie value diverges noticeably from the value calculated from protein/fat/carb grams (for example carotte: declared 41, calculated 31).
- Alcohol not accounted for: 69 alcoholic beverages where the calculated calories do not include the contribution of `alcohol_g`, producing a large gap between declared and calculated values (for example vodka: declared 231, calculated 0).
- Out-of-range value: 1 entry (`epice-mastic-larme-de-mastic`) at exactly 1000 kcal/100g, at the edge of the schema's allowed range.

These are tracked for cleanup; contributions that correct any of the above are welcome, see [Contributing](#contributing).

## Using the raw JSON

### JavaScript

```javascript
const response = await fetch('./data/Open-food-calories.json');
const foods = await response.json();

const item = foods.find(f => f.name.en === 'White rice (cooked)');

if (item) {
  console.log(`${item.name.fr} has ${item.kcal_per_100g} kcal per 100g.`);
}

const weight = 250;
const totalKcal = (item.kcal_per_100g * weight) / 100;
console.log(`Total: ${totalKcal} kcal for ${weight}g`);
```

### Python

```python
import json

with open('data/Open-food-calories.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

search_term = 'oeuf'
results = [food for food in data if search_term.lower() in food['name']['fr'].lower()]

for r in results:
    if r['weight_per_unit']:
        kcal_unit = (r['kcal_per_100g'] * r['weight_per_unit']) / 100
        print(f"{r['name']['fr']}: {kcal_unit} kcal per unit")
    else:
        print(f"{r['name']['fr']}: {r['kcal_per_100g']} kcal per 100g")
```

`weight_per_unit` is null when the food is normally measured by weight (rice, flour), and set to the average weight in grams when the food is normally counted by piece (an egg, an apple). An apple with `kcal_per_100g: 52` and `weight_per_unit: 150` amounts to 78 kcal per apple.

## Command-line tool

`CLI/ofc_cli.py` is a dependency-free command-line client for the dataset. It resolves `data/Open-food-calories.json` relative to its own location, so it works whether it is run from the repository root or from inside `CLI/`.

```
python3 CLI/ofc_cli.py search pizza
python3 CLI/ofc_cli.py search poulet --lang fr --category meat
python3 CLI/ofc_cli.py get riz-blanc-cuit
python3 CLI/ofc_cli.py get riz-blanc-cuit --json
python3 CLI/ofc_cli.py categories
python3 CLI/ofc_cli.py stats
```

Options for `search`:

| Option | Description |
| :--- | :--- |
| `query` | Search term, matched against the name. Leave empty to list without filtering by name. |
| `--lang` | `fr`, `en`, or `any` (default). Restricts which name field is matched. |
| `--category` | Filter by one of the categories listed above. |
| `--type` | Filter by `solid`, `liquid`, or `unit`. |
| `--limit` | Maximum number of results (default 15). |
| `--json` | Output raw JSON instead of formatted text. |
| `--verbose`, `-v` | Print full nutritional detail for each result. |
| `--file` | Override the dataset path. |

## Local REST API

`CLI/ofc_server.py` starts a local HTTP server exposing the dataset, using only the Python standard library, no installation required.

```
python3 CLI/ofc_server.py --port 8000
```

| Route | Description |
| :--- | :--- |
| `GET /all` | Returns the full dataset. |
| `GET /search?q=&lang=&category=&type=&limit=` | Same filters as the CLI search command. |
| `GET /food/<id>` | Returns a single entry by its `id`. |
| `GET /categories` | Returns entry counts per category. |

Examples:

```
curl "http://localhost:8000/search?q=pizza&category=prepared"
curl "http://localhost:8000/food/riz-blanc-cuit"
curl "http://localhost:8000/categories"
```

Responses are JSON, served with `Access-Control-Allow-Origin: *`, so the server can be queried directly from a browser-based prototype during development.

## Contributing

The goal is to grow this dataset well beyond 5,000 entries while keeping it clean. Contributions of new entries, corrections to the issues listed in [Data quality report](#data-quality-report), and improvements to the tooling are all welcome.

All data changes are made in `data/Open-food-calories.json`, following the schema described above and validated by `data-schema.json`. Before opening a pull request:

- Check for an existing entry with the same or a very similar name before adding a new one.
- Provide both `name.fr` and `name.en`.
- Set `state` and `type` accurately; use `liquid` for drinks and oils, `unit` for foods normally counted by piece, `solid` otherwise.
- Set `weight_per_unit` when the food is normally counted by piece, leave it null otherwise.
- Set `source` and `confidence` honestly; use `estimated` and `low`/`medium` rather than guessing a `high`-confidence value.
- Validate the JSON syntax before committing.
- Run `python3 CLI/ofc_cli.py stats` against the updated file to sanity-check totals and confidence levels before opening the pull request.

See `CONTRIBUTING.md` for the full process.

## License

This project is licensed under the MIT License, see [LICENSE](LICENSE) for details.
