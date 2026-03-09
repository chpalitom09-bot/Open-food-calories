API Documentation - Open-Food-Calories 🚀

Welcome to the API documentation! Since this project is hosted on GitHub Pages, you can access the data in two ways: Static (the easiest) or Dynamic (via FastAPI).

1. Static Access (Direct JSON)
  
 This is the fastest method. GitHub Pages acts as a free CDN. Use this if you want to load the entire database into your application.
 
 Base URL: [Food DataBase](https://github.com/chpalitom09-bot/Open-food-calories/blob/main/data/food.json) 
 
 Example:
 JavaScript
 
 <pre>
   fetch('https://github.com/chpalitom09-bot/Open-food-calories/blob/main/data/food.json')
  .then(response => response.json())
  .then(data => {
    console.log(`Successfully loaded ${data.length} food items!`);
  });
 </pre>

 
2. Dynamic Access (FastAPI)
   
   If you run the API locally or deploy it to a server (like Render or Vercel), these are the available endpoints.

   <pre>GET /search</pre>

   Search for food items by name.Parameter: q (string) - The search term.Example:

   <pre>/search?q=pizza</pre>

   Response JSON :
<pre> [
  {
    "name": "Pizza",
    "english_name": "Pizza",
    "kcal_per_100g": 266,
    "emoji": "🍕",
    "type": "solid"
  }
]
</pre>


<pre>GET /all</pre>


Returns the full database.

3. Data Schema
  
   Every food object strictly follows this JSON format:

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | Name in French (lowercase) |
| `english_name` | `string` | Name in English |
| `kcal_per_100g` | `int` | Calories per 100g |
| `emoji` | `string` | Representative icon |
| `type` | `string` | `"solid"` or `"liquid"` |
| `weight_per_unit` | `int` | Average weight of one portion (optional) |
