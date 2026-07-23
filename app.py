import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from services.kuma import obtener_estado_kuma
from services.hikvision import obtener_estado_camaras

load_dotenv()

st.set_page_config(
    page_title="Asistente Servidor Dell",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# BRANDING: LOGO COMBINADO EN EL HEADER NATIVO
# =========================================================
LOGO_COMBINADO = "assets/logo_infraestructura.png" 

st.logo(
    LOGO_COMBINADO,
    icon_image=LOGO_COMBINADO
)

# =========================================================
# CSS CUSTOM: TAMAÑOS Y JERARQUÍA EN TARJETA RESUMEN
# =========================================================
st.markdown("""
    <style>
        /* 0. ANCHO DEL SIDEBAR */
        [data-testid="stSidebar"] {
            min-width: 310px !important;
            max-width: 310px !important;
        }

        /* 1. AMPLIAR CONTENEDOR DEL LOGO NATIVO */
        [data-testid="stSidebarHeader"] {
            padding-top: 1rem !important;
            padding-bottom: 0.5rem !important;
            height: auto !important;
            min-height: 60px !important;
        }

        /* 2. AGRANDAR LA IMAGEN DEL LOGO */
        [data-testid="stLogo"] img,
        [data-testid="stSidebarHeader"] img {
            height: 50px !important;
            max-height: 55px !important;
            width: auto !important;
            object-fit: contain !important;
        }

        /* 3. PEGAR CONTENIDO DEBAJO DEL HEADER */
        [data-testid="stSidebarUserContent"] {
            padding-top: 0.5rem !important;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 0.4rem !important;
        }

        /* 4. REDUCIR TAMAÑO DE MÉTRICAS */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }

        /* 5. RESUMEN DE CCTV - ESTILOS DE TAMAÑO */
        .cctv-status-badge {
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid #3b82f6;
            padding: 10px 12px;
            border-radius: 4px;
            margin-bottom: 8px;
            color: #e5e7eb;
        }

        .cctv-main-text {
            font-size: 0.95rem;      /* Tamaño más grande y visible */
            font-weight: 600;        /* Negrita seminegrita */
            color: #f3f4f6;
            display: block;
            margin-bottom: 2px;
        }

        .cctv-sub-text {
            font-size: 0.82rem;      /* Un toque más sutil pero claro */
            color: #fbbf24;          /* Tono amarillo/alerta tenue para caídos */
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* 6. REMOVER BORDES Y CAJAS NATIVAS DEL EXPANDER */
        [data-testid="stExpander"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }

        [data-testid="stExpander"] details {
            border: none !important;
            background: transparent !important;
        }

        [data-testid="stExpanderDetails"] {
            border: none !important;
            background: transparent !important;
            padding: 8px 0px 0px 0px !important;
        }

        [data-testid="stExpander"] summary {
            border: none !important;
            border-radius: 6px !important;
            padding: 6px 4px !important;
            color: #9ca3af !important;
            font-size: 0.82rem !important;
            background-color: transparent !important;
            transition: background 0.2s ease;
        }

        [data-testid="stExpander"] summary:hover {
            color: #f3f4f6 !important;
            background-color: rgba(255, 255, 255, 0.04) !important;
        }

        /* 7. TARJETAS DE CÁMARAS ESPACIADAS Y ELEGANTES */
        .camera-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px !important;
            font-size: 0.78rem;
            transition: all 0.2s ease;
        }

        .camera-card:hover {
            background-color: rgba(255, 255, 255, 0.07);
            border-color: rgba(255, 255, 255, 0.15);
        }

        .camera-name {
            color: #d1d5db;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 155px;
        }

        .badge-online {
            background-color: rgba(34, 197, 94, 0.12);
            color: #4ade80;
            border: 1px solid rgba(34, 197, 94, 0.25);
            font-size: 0.65rem;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
            flex-shrink: 0;
        }

        .badge-offline {
            background-color: rgba(239, 68, 68, 0.12);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.25);
            font-size: 0.65rem;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
            flex-shrink: 0;
        }
    </style>
""", unsafe_allow_html=True)

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy Dashy, tu asistente virtual. ¿En qué te puedo ayudar hoy?"}
    ]

# =========================================================
# BARRA LATERAL (SIDEBAR)
# =========================================================
with st.sidebar:

    # --- 1. ESTADO DEL HOST ---
    estado_kuma = obtener_estado_kuma()
    if "🟢" in estado_kuma:
        st.metric(
            label="Servidor Dell PowerEdge", 
            value="ENCENDIDO", 
            delta="Online / Ping OK"
        )
    else:
        st.metric(
            label="Servidor Dell PowerEdge", 
            value="APAGADO", 
            delta="- Offline", 
            delta_color="inverse"
        )

    st.markdown("---")

    # --- 2. ESTADO DE CCTV ---
    info_cctv = obtener_estado_camaras()
    st.markdown("**📹 CCTV & Cámaras**")
    
    # Separación limpia del texto para aplicar diferentes tamaños y estilos
    resumen_raw = info_cctv["resumen"]
    if "(" in resumen_raw:
        partes = resumen_raw.split(" (")
        texto_principal = partes[0]
        texto_alerta = "(" + partes[1]
    else:
        texto_principal = resumen_raw
        texto_alerta = ""

    st.markdown(f"""
        <div class="cctv-status-badge">
            <span class="cctv-main-text">{texto_principal}</span>
            <span class="cctv-sub-text">{texto_alerta}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if info_cctv["camaras"]:
        with st.expander("🔍 Detalle de dispositivos", expanded=False):
            for cam in info_cctv["camaras"]:
                is_online = "🟢" in cam['estado'] or "Online" in cam['estado']
                badge_class = "badge-online" if is_online else "badge-offline"
                status_text = "ONLINE" if is_online else "OFFLINE"
                dot = "🟢" if is_online else "🔴"

                st.markdown(f"""
                    <div class="camera-card">
                        <span class="camera-name" title="{cam['nombre']}">{cam['nombre']}</span>
                        <span class="{badge_class}">{dot} {status_text}</span>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 3. LORAWAN ---
    st.markdown("**🛰️ LoRaWAN (ChirpStack)**")
    st.caption("Próximamente: Sensores IoT")

# =========================================================
# PANEL PRINCIPAL - CHAT
# =========================================================
st.title("Asistente de Infraestructura - Dashy")
st.caption("Consulta el estado general de las cámaras, sensores y monitoreo de red mediante IA.")

for msg in st.session_state.messages:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

if prompt := st.chat_input("Escribe tu consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="👤").write(prompt)

    if not groq_client:
        st.error("❌ Falta la variable GROQ_API_KEY en el archivo .env.")
    else:
        detalle_camaras_texto = ""
        if info_cctv.get("camaras"):
            for cam in info_cctv["camaras"]:
                detalle_camaras_texto += f"- {cam['nombre']}: {cam['estado']}\n"
        else:
            detalle_camaras_texto = "No hay detalle individual disponible."

        prompt_sistema = f"""
Eres un asistente de infraestructura de TI especializado en el Servidor Dell del usuario.
Responde de forma clara, directa, técnica y concisa.

--- ESTADO EN TIEMPO REAL DEL SISTEMA ---
- Monitoreo Host Dell: {estado_kuma}
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