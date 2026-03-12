import requests
import json
import os
import time

def obtener_datos():
    print("\nCONECTANDO CON LA BASE DE DATOS")
    
    lista_final = []
    pagina_actual = 1
    objetivo = 200
    
    while len(lista_final) < objetivo:
        print(f"Descargando página {pagina_actual}...")
        
        url_api = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&countries_tags=en:spain&page_size=100&page={pagina_actual}&json=true"
        
        try:
            resp = requests.get(url_api, timeout=20)
            if resp.status_code == 200:
                datos_brutos = resp.json()
                productos_api = datos_brutos.get('products', [])
                
                if not productos_api: 
                    break
                
                for p in productos_api:
                    if len(lista_final) >= objetivo:
                        break
                        
                    nutri = p.get('nutriments', {})
                    
                    item = {
                        "url": p.get('url', ''),
                        "titulo": p.get('product_name', 'PRODUCTO DESCONOCIDO').upper(),
                        "valores_nutricionales_100_g": {
                            "Grasas": f"{nutri.get('fat_100g', 0)} gr",
                            "Saturadas": f"{nutri.get('saturated-fat_100g', 0)} gr",
                            "Hidratos de carbono": f"{nutri.get('carbohydrates_100g', 0)} gr",
                            "Azucares": f"{nutri.get('sugars_100g', 0)} gr",
                            "Proteinas": f"{nutri.get('proteins_100g', 0)} gr",
                            "Sal": f"{nutri.get('salt_100g', 0)} gr",
                            "Valor energetico": f"{nutri.get('energy-kcal_100g', 0)} kcal"
                        },
                        "descripcion": p.get('ingredients_text', 'No disponible'),
                        "categorias": p.get('categories_tags', ['alimentacion'])[:2],
                        "precio_total": 0.0,
                        "precio_por_cantidad": 0.0,
                        "peso_volumen": p.get('quantity', 'n/a'),
                        "origen": p.get('brands', 'Supermercado España')
                    }
                    
                    if item["titulo"] != "PRODUCTO DESCONOCIDO" and nutri.get('proteins_100g'):
                        lista_final.append(item)
                
                print(f"Total acumulado: {len(lista_final)} productos")
                pagina_actual += 1
                time.sleep(1) 
                
            else:
                print(f"Error {pagina_actual}")
                break
                
        except Exception as e:
            print(f"Error: {e}")
            break

    ruta = os.path.join("data", "raw", "productos.json")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(lista_final, f, indent=2, ensure_ascii=False)
    
    print(f"\nSe han guardado {len(lista_final)} productos en {ruta}")
    return lista_final

if __name__ == "__main__":
    obtener_datos()

