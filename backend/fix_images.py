import json
import os

def fix_images():
    # Map categories to keywords for LoremFlickr
    # Format: https://loremflickr.com/400/400/{keyword}
    
    category_map = {
        # Products.json
        "Supermercado": "supermarket,food",
        "Restaurante": "meal,food",
        "Farmacia": "medicine,pills",
        "Panadería": "bakery,bread",
        "Cafetería": "coffee,latte",
        "Tienda de Abarrotes": "grocery,food",
        "Veterinaria": "pet,dog,cat",
        "Comidas Rápidas": "burger,fastfood",
        "Pizzería": "pizza",
        
        # Jumbo Products
        "Refrigeración": "refrigerator,fridge",
        "Lavadoras": "washing machine",
        "Televisores": "tv,television",
        "Celulares": "smartphone,mobile",
        "Despensa": "grocery,pantry",
        "Lácteos": "milk,cheese,dairy",
        "Frutas y Verduras": "fruit,vegetable",
        "Carnes": "meat,beef,chicken",
        "Aseo": "cleaning,detergent",
        "Cuidado Personal": "shampoo,soap"
    }

    base_path = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_path, "data")
    
    files = ["products.json", "jumbo_products.json"]
    
    for filename in files:
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ {filename} not found.")
            continue
            
        print(f"🔄 Processing {filename}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        updated_count = 0
        for item in data:
            category = item.get("category")
            # Generate a new URL based on category + random lock to prevent caching same image for all
            # LoremFlickr supports ?lock=ID
            keyword = category_map.get(category, "product")
            
            # Create a deterministic but unique URL per item ID
            new_image = f"https://loremflickr.com/400/400/{keyword}?lock={item['id']}"
            
            item["image"] = new_image
            updated_count += 1
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Updated {updated_count} images in {filename}")

if __name__ == "__main__":
    fix_images()
