import os
import requests

def obtener_estado_kuma():
    kuma_url = os.getenv("KUMA_API_URL", "http://100.101.28.41:3001").rstrip("/")
    slug = "principal"

    try:
        response = requests.get(f"{kuma_url}/api/status-page/heartbeat/{slug}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            heartbeats = data.get("heartbeatList", {})
            monitores_down, monitores_up = [], []

            for monitor_id, lista in heartbeats.items():
                if lista:
                    if lista[-1].get("status") == 0:
                        monitores_down.append(f"ID {monitor_id}")
                    else:
                        monitores_up.append(f"ID {monitor_id}")

            total = len(monitores_up) + len(monitores_down)
            if monitores_down:
                return f"⚠️ Uptime Kuma: {len(monitores_down)} servicio(s) CAÍDO(S)."
            else:
                return f"🟢 Todos los {total} servicios monitoreados en Uptime Kuma están OPERATIVOS."
        else:
            return f"🟡 Error {response.status_code} al consultar la página de estado."
    except Exception as e:
        return f"🔴 No se pudo conectar con Uptime Kuma: {str(e)}"