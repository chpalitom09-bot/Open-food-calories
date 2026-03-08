That's a bold and impressive goal! Moving from 2,000 to 20,000 items changes the scale of the project—it becomes a "Big Data" resource for the community.

Here is a professional, comprehensive CONTRIBUTING.md in English, specifically tailored for a massive 20,000+ food objective.

Contributing to Open-Food-Calories 🥗
First of all, thank you for considering contributing! We have a massive goal: Building an open-source database of 20,000+ foods and dishes. Your help is essential to reach this milestone and provide developers worldwide with high-quality, free nutritional data.



🎯 Our Goal: 20,000+ Entries
To reach this scale, we are looking for:

International Cuisines: Traditional dishes from every continent.

Branded Products: Common supermarket items (global or local).

Raw Ingredients: Every variety of fruit, vegetable, grain, and meat.

Beverages: From specialty coffees to local sodas.



📝 How to Contribute
1. Adding New Data
All data must be added to <pre>data/food.json.</pre> To maintain consistency at scale, every entry must follow this exact schema:

JSON
<pre>
{
  "name": "Nom de l'aliment",
  "english_name": "English name",
  "kcal_per_100g": 0,
  "emoji": "🥗",
  "type": "solid",
  "weight_per_unit": 0
}
  </pre>
  
  
Quality Standards:

Reliability: Cross-reference calories using trusted sources (e.g., USDA, CIQUAL, or official labels).

Bilingualism: Provide the name in both French and English.

Liquid vs Solid: Use "liquid" for drinks and oils, "solid" for everything else.

The Unit Rule: If the food is often eaten as a whole (1 egg, 1 apple, 1 biscuit), please provide the average weight in grams in weight_per_unit. Otherwise, keep it at 0.



2. Data Validation
With a goal of 20,000 items, we cannot afford syntax errors or duplicates.

No Duplicates: Check if the food already exists (even under a slightly different name).

JSON Syntax: Ensure your commas and brackets are perfect. Use [JSONLint](https://jsonlint.com/) to verify.



🚀 Pull Request Process
Fork the repository.

Create a branch for your batch of additions (git checkout -b feat/add-mediterranean-dishes).

Add your data to data/food.json.

Run the check script: (If available) python examples/check_data.py.

Commit with a clear message (git commit -m "Added 50 Japanese specialty dishes").

Push to your fork and open a Pull Request.

🛠 Pro-Tips for Batch Adding


If you are planning to add hundreds of items at once:

Open an Issue first: Tell us which category you are working on to avoid two people working on the same list.

Use Tools: If you are scraping data or converting from another dataset, ensure the mapping to our JSON format is 100% accurate.



⚖️ License
By contributing to this project, you agree that your contributions will be licensed under the MIT License.
