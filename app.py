import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Importar servicios de infraestructura local
from services.kuma import obtener_estado_kuma
from services.hikvision import obtener_estado_camaras

# Cargar variables de entorno (.env)
load_dotenv()

# Configuración de la interfaz Streamlit
st.set_page_config(
    page_title="Asistente Servidor Dell",
    page_icon="🤖",
    layout="wide"
)

# Inicializar cliente de Groq (Llama 3.3)
groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy el asistente de tu Servidor Dell. ¿En qué te puedo ayudar hoy?"}
    ]

# =========================================================
# BARRA LATERAL (SIDEBAR) - DIAGNÓSTICO
# =========================================================
with st.sidebar:
    st.title("🖥️ Estado del Servidor")
    
    if st.button("🔄 Actualizar Estado"):
        st.rerun()

    # Sección: Uptime Kuma
    st.subheader("📡 Diagnóstico de Red")
    estado_kuma = obtener_estado_kuma()
    if "🟢" in estado_kuma:
        st.success(estado_kuma)
    elif "⚠️" in estado_kuma or "🟡" in estado_kuma:
        st.warning(estado_kuma)
    else:
        st.error(estado_kuma)

    # Sección: HikCentral / CCTV (vía Uptime Kuma)
    st.subheader("📹 Estado de CCTV")
    info_cctv = obtener_estado_camaras()
    st.info(info_cctv["resumen"])
    
    if info_cctv["camaras"]:
        with st.expander("Ver detalle de cámaras"):
            for cam in info_cctv["camaras"]:
                st.write(f"- {cam['nombre']}: {cam['estado']}")

    st.markdown("---")
    
    # Sección: LoRaWAN (ChirpStack)
    st.markdown("### 🛰️ LoRaWAN (ChirpStack)")
    st.info("Próximamente: Integración de sensores")

# =========================================================
# PANEL PRINCIPAL - CHAT CON IA
# =========================================================
st.title("🤖 Asistente de Infraestructura - Servidor Dell")
st.caption("Consulta el estado general de las cámaras, sensores y monitoreo de red mediante Inteligencia Artificial.")

# Mostrar historial de la conversación
for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# Capturar consulta del usuario
if prompt := st.chat_input("Escribe tu consulta aquí (ej: ¿Cómo está el dvr de sewell c98?)..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    if not groq_client:
        st.error("❌ Falta la variable GROQ_API_KEY en el archivo .env.")
    else:
        # Construir el texto con el detalle de cada cámara/DVR
        detalle_camaras_texto = ""
        if info_cctv.get("camaras"):
            for cam in info_cctv["camaras"]:
                detalle_camaras_texto += f"- {cam['nombre']}: {cam['estado']}\n"
        else:
            detalle_camaras_texto = "No hay detalle individual disponible."

        # Contexto dinámico enviado a Groq en tiempo real
        prompt_sistema = f"""
Eres un asistente de infraestructura de TI especializado en el Servidor Dell del usuario.
Responde de forma clara, directa, técnica y concisa.

--- ESTADO EN TIEMPO REAL DEL SISTEMA ---
- Monitoreo Uptime Kuma: {estado_kuma}
- Resumen CCTV: {info_cctv['resumen']}

- Detalle individual de DVRs/Cámaras CCTV:
{detalle_camaras_texto}
----------------------------------------

Pregunta del usuario: {prompt}
"""

        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt_sistema}],
                temperature=0.3
            )
            
            respuesta_texto = response.choices[0].message.content
            st.chat_message("assistant", avatar="🤖").markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})

        except Exception as e:
            st.error(f"❌ Error al consultar Groq: {str(e)}")