# Importar las librerías necesarias
import requests
from bs4 import BeautifulSoup
import re

# Definir las funciones necesarias

def obtener_ISBN_desde_API():
    try:
        response = requests.get("https://bookpricetracker.risusapp.com/api/bookPriceUpdate")
        if response.status_code == 200:
            ISBN = response.text.strip()  # Eliminar espacios en blanco alrededor del ISBN
            print("ISBN obtenido de la API:", ISBN)
            return ISBN
        else:
            print("Error: No se pudo obtener el ISBN de la API. Código de estado:", response.status_code)
            return None
    except Exception as e:
        print("Error al obtener el ISBN de la API:", e)
        return None

def scrape_libro_por_ISBN(ISBN):
    try:
        base_url = "https://www.fnac.es/SearchResult/ResultList.aspx?Search="
        url = base_url + ISBN
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            imagen_div = soup.find('img', class_='Article-itemVisualImg')
            if imagen_div:
                url_producto = "https://www.fnac.es" + imagen_div['data-url']
            else:
                print("Error: No se pudo encontrar la URL del producto.")
                return None, None, None
            
            disponibilidad_span = soup.find('div', class_='Dispo-txt')
            if disponibilidad_span:
                disponibilidad_html = str(disponibilidad_span)
            else:
                print("Advertencia: No se pudo encontrar la disponibilidad del producto.")
                disponibilidad_html = None
            
            precio_span = soup.find('del', class_='oldPrice')
            if precio_span:
                precio = precio_span.text.strip()
                # Reemplazar la coma por un punto y eliminar el símbolo de euro
                precio_sin_euro = re.sub(r'€|\s', '', precio)
                precio_con_punto = precio_sin_euro.replace(',', '.')
            else:
                print("Advertencia: No se pudo encontrar el precio del producto.")
                precio_con_punto = None
            
            return url_producto, disponibilidad_html, precio_con_punto
        else:
            print("Error: No se pudo acceder a la página. Código de estado:", response.status_code)
            return None, None, None
    except Exception as e:
        print("Error al hacer scraping:", e)
        return None, None, None

def enviar_datos_a_API(datos):
    try:
        response = requests.post("https://bookpricetracker.risusapp.com/api/bookPriceUpdate", json=datos)
        if response.status_code == 200:
            print("Datos enviados correctamente a la API.")
        else:
            print("Error al enviar los datos a la API. Código de estado:", response.status_code)
    except Exception as e:
        print("Error al enviar datos a la API:", e)

# Proceso principal

for i in range(1, 101):  # Iterar 100 veces
    print("Iteración:", i)
    ISBN = obtener_ISBN_desde_API()
    if ISBN:
        url_producto, disponibilidad_html, precio = scrape_libro_por_ISBN(ISBN)
        if url_producto and disponibilidad_html and precio:
            datos_a_enviar = {
                'EAN13': ISBN,
                'url': url_producto,
                'ecommerce': 'fnac',  
                'status': 'available' if disponibilidad_html else 'unavailable', 
                'price': precio
            }
            enviar_datos_a_API(datos_a_enviar)
    print()  # Imprimir una línea en blanco entre cada iteración
