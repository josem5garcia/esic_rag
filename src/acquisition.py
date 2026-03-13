import requests
import json
import os
import time

def obtener_datos():
    print("\n🚀 INICIANDO ADQUISICIÓN DE DATOS (RETO 1)...")
    
    lista_final = []
    pagina_actual = 1
    objetivo = 210 
    
    # URL configurada para productos vendidos en España
    url_base = "https://world.openfoodfacts.org/cgi/search.pl?action=process&countries_tags=en:spain&page_size=100&json=true"
    
    while len(lista_final) < objetivo:
        url_api = f"{url_base}&page={pagina_actual}"
        print(f"📡 Conectando a página {pagina_actual} (Llevamos {len(lista_final)} productos)...")
        
        try:
            # Timeout alto (60s) para evitar el error de 'Read timed out'
            resp = requests.get(url_api, timeout=60)
            
            if resp.status_code == 200:
                datos = resp.json()
                productos_api = datos.get('products', [])
                
                if not productos_api:
                    print("⚠️ No hay más productos disponibles en la API.")
                    break
                
                for p in productos_api:
                    if len(lista_final) >= objetivo:
                        break
                    
                    nombre = p.get('product_name', '').strip()
                    if nombre:
                        nutri = p.get('nutriments', {})
                        # Formateamos el producto según lo solicitado
                        item = {
                            "url": p.get('url', ''),
                            "titulo": nombre.upper(),
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
                            "origen": p.get('brands', 'Supermercado')
                        }
                        lista_final.append(item)
                
                pagina_actual += 1
                time.sleep(1) # Pausa técnica para no saturar
                
            else:
                print(f"❌ Error de servidor ({resp.status_code}). Reintentando...")
                time.sleep(5)
                
        except Exception as e:
            print(f"⏳ Error de conexión ({e}). Reintentando en 5 segundos...")
            time.sleep(5)
            continue

    # --- LÓGICA DE GUARDADO INTELIGENTE ---
    # Buscamos la carpeta raíz (un nivel arriba de 'src')
    ruta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_carpeta = os.path.join(ruta_raiz, "data", "raw")
    
    # Creamos la carpeta si no existe
    os.makedirs(ruta_carpeta, exist_ok=True)
    
    ruta_archivo = os.path.join(ruta_carpeta, "productos.json")
    
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        json.dump(lista_final, f, indent=2, ensure_ascii=False)
    
    print(f"\n✨ ¡MISIÓN CUMPLIDA! ✨")
    print(f"Se han guardado {len(lista_final)} productos en: {ruta_archivo}")
    return lista_final

if __name__ == "__main__":
    obtener_datos()