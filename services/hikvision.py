import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_estado_camaras():
    """
    Obtiene el estado real de los DVRs/Cámaras consultando la estructura 
    y los latidos en tiempo real de Uptime Kuma.
    """
    base_url = os.getenv("KUMA_API_URL", "http://100.101.28.41:3001")
    slug = "dvr" 
    
    url_info = f"{base_url}/api/status-page/{slug}"
    url_heartbeats = f"{base_url}/api/status-page/heartbeat/{slug}"

    try:
        # 1. Obtener la lista de monitores (nombres e IDs)
        resp_info = requests.get(url_info, timeout=5)
        # 2. Obtener los latidos/estados en tiempo real
        resp_hb = requests.get(url_heartbeats, timeout=5)

        if resp_info.status_code == 200:
            data_info = resp_info.json()
            data_hb = resp_hb.json() if resp_hb.status_code == 200 else {}

            public_group_list = data_info.get("publicGroupList", [])
            heartbeat_list = data_hb.get("heartbeatList", {})
            uptime_group_list = data_hb.get("uptimeGroupList", {})

            lista_camaras = []
            totales = 0
            online_count = 0

            # Recorrer cada monitor configurado
            for group in public_group_list:
                for monitor in group.get("monitorList", []):
                    totales += 1
                    nombre = monitor.get("name", "DVR/Cámara")
                    monitor_id_str = str(monitor.get("id"))

                    # Determinar si está Online (1) u Offline (0)
                    is_online = False

                    # Método A: Buscar en el último latido (heartbeatList)
                    if monitor_id_str in heartbeat_list:
                        hbs = heartbeat_list[monitor_id_str]
                        if isinstance(hbs, list) and len(hbs) > 0:
                            # El último heartbeat de la lista es el más reciente
                            ultimo_status = hbs[-1].get("status")
                            is_online = (ultimo_status == 1)
                        elif isinstance(hbs, dict):
                            is_online = (hbs.get("status") == 1)

                    # Método B: Fallback con uptimeGroupList si existe
                    elif uptime_group_list and monitor_id_str in uptime_group_list:
                        is_online = (uptime_group_list[monitor_id_str] == 1)

                    # Formatear estado
                    if is_online:
                        estado_str = "🟢 Online"
                        online_count += 1
                    else:
                        estado_str = "🔴 Offline"

                    lista_camaras.append({
                        "nombre": nombre,
                        "estado": estado_str
                    })

            if totales == 0:
                return {
                    "resumen": "⚠️ No se encontraron monitores en la página /status/dvr.",
                    "camaras": []
                }

            resumen_texto = f"CCTV: {online_count}/{totales} Dispositivos Online"
            if online_count < totales:
                resumen_texto += f" (⚠️ {totales - online_count} caído/s)"

            return {
                "resumen": resumen_texto,
                "camaras": lista_camaras
            }

        else:
            return {
                "resumen": f"⚠️ Error {resp_info.status_code} consultando /status/dvr",
                "camaras": []
            }

    except Exception as e:
        return {
            "resumen": f"❌ Error de conexión con Kuma: {str(e)}",
            "camaras": []
        }