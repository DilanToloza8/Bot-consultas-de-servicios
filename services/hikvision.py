import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_estado_camaras():
    """
    Obtiene el estado de los DVRs/Cámaras leyendo la Status Page de Uptime Kuma.
    """
    # URL del JSON de la Status Page de Kuma
    base_url = os.getenv("KUMA_API_URL", "http://100.101.28.41:3001")
    # Usamos la slug 'dvr' que vimos en tu navegador (http://100.101.28.41:3001/status/dvr)
    slug = "dvr" 
    
    url = f"{base_url}/api/status-page/{slug}"

    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Kuma devuelve la estructura de la página de estado
            public_group_list = data.get("publicGroupList", [])
            heartbeat_list = data.get("uptimeGroupList", {}) # O el estado de los heartbeats
            
            lista_camaras = []
            totales = 0
            online_count = 0

            # Recorrer los monitores asignados a esa Status Page
            for group in public_group_list:
                for monitor in group.get("monitorList", []):
                    totales += 1
                    nombre = monitor.get("name", "DVR/Cámara")
                    
                    # Chequear el último estado registrado en la Status Page
                    # En Kuma: 1 = UP (Online), 0 = DOWN (Offline), 2 = PENDING
                    monitor_id = str(monitor.get("id"))
                    
                    # Intentar obtener el estado actual
                    # Si no viene en la lista directa, validamos la propiedad 'active'
                    status_code = monitor.get("status", 1) 
                    
                    if status_code == 1:
                        estado_str = "🟢 Online"
                        online_count += 1
                    else:
                        estado_str = "🔴 Offline"

                    lista_camaras.append({
                        "nombre": nombre,
                        "estado": estado_str
                    })

            if totales == 0:
                # Si no se agruparon por la Status Page, se avisa
                return {
                    "resumen": "⚠️ No se encontraron monitores en la página /status/dvr.",
                    "camaras": []
                }

            resumen_texto = f"{online_count}/{totales} Dispositivos Online"
            if online_count < totales:
                resumen_texto += f" (⚠️ {totales - online_count} caído/s)"

            return {
                "resumen": resumen_texto,
                "camaras": lista_camaras
            }

        else:
            # Fallback si no existe la Status Page 'dvr'
            return {
                "resumen": f"⚠️ Error {response.status_code} consultando la status page '/status/dvr'",
                "camaras": []
            }

    except Exception as e:
        return {
            "resumen": f"❌ Error de conexión con Kuma: {str(e)}",
            "camaras": []
        }