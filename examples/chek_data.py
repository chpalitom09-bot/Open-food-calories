import json

def check_json():
    with open('data/food.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    names = [item['name'] for item in data]
    duplicates = set([x for x in names if names.count(x) > 1])
    
    print(f"✅ Analyse de {len(data)} aliments terminée.")
    
    if duplicates:
        print(f"⚠️ Doublons trouvés : {duplicates}")
    else:
        print("🚀 Aucun doublon, la base est propre !")

if __name__ == "__main__":
    check_json()
