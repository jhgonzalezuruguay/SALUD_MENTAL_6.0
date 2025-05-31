import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv
import base64

# ================== CONFIGURACIÓN DE ADMIN ==================
ADMIN_PASSWORD = "16990037"  # CAMBIA esto por tu clave secreta

# ================== FUNCIONES ===============================

DIARIO_CSV = "diario_emocional.csv"

def guardar_diario_csv(entry):
    file_exists = os.path.isfile(DIARIO_CSV)
    entry_to_save = entry.copy()
    entry_to_save["emociones"] = ";".join(entry["emociones"]) if entry["emociones"] else ""
    entry_to_save["intensidades"] = ";".join([f"{k}:{v}" for k, v in entry["intensidades"].items()]) if entry["intensidades"] else ""
    entry_to_save["acciones"] = ";".join(entry["acciones"]) if entry["acciones"] else ""
    with open(DIARIO_CSV, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=entry_to_save.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry_to_save)

def cargar_diario_csv():
    if os.path.isfile(DIARIO_CSV):
        try:
            df = pd.read_csv(DIARIO_CSV, dtype={'codigo_usuario':str})
        except Exception:
            df = pd.read_csv(DIARIO_CSV, dtype=str)
        return df
    else:
        return pd.DataFrame(columns=["codigo_usuario","fecha", "emociones", "intensidades", "contexto", "acciones"])

def get_table_download_link(df, filename="diario_emocional.csv"):
    csv_str = df.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar historial como CSV</a>'
    return href

# ================== SESIONES STREAMLIT ======================
if "diary_data" not in st.session_state:
    st.session_state.diary_data = []
if "codigo_usuario" not in st.session_state:
    st.session_state.codigo_usuario = None
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

# ================== TÍTULOS ================================
st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")
st.title("📔 Diario Emocional: Check-in")

# =========== INGRESO DE USUARIO (CÓDIGO IDENTIFICADOR) ===========
if st.session_state.codigo_usuario is None:
    st.subheader("🔒 Ingreso de Usuario")
    codigo_input = st.text_input("Por favor, ingresa tu código identificador de 8 dígitos (Documento de Identidad, sin puntos ni guiones):", max_chars=8)
    if st.button("Ingresar"):
        if codigo_input.isdigit() and len(codigo_input) == 8:
            st.session_state.codigo_usuario = codigo_input
            st.success("¡Código aceptado! Ahora puedes completar tu diario emocional.")
        else:
            st.error("El código debe ser numérico y tener exactamente 8 dígitos.")
    st.stop()

# =========== ENTRADA DIARIO EMOCIONAL ======================
emotions = [
    {"label": "Alegría", "emoji": "😊"},
    {"label": "Ansiedad", "emoji": "😟"},
    {"label": "Tristeza", "emoji": "😢"},
    {"label": "Ira", "emoji": "😠"},
    {"label": "Confusión", "emoji": "😐"},
    {"label": "Gratitud", "emoji": "🙏"},
    {"label": "Miedo", "emoji": "😨"}
]

st.subheader("¿Cómo te sientes hoy?")

selected_emotions = st.multiselect(
    "Selecciona hasta 3 emociones:",
    options=[f"{e['emoji']} {e['label']}" for e in emotions],
    max_selections=3
)

emotion_intensities = {}
for emotion in selected_emotions:
    level = st.slider(f"Intensidad de {emotion} (1-10):", 1, 10, 5)
    emotion_intensities[emotion] = level

context = st.text_area("¿Qué hizo que te sintieras así?", placeholder="Describe brevemente lo que pasó...")

st.markdown("¿Qué hiciste para cuidarte?")
coping_actions = st.multiselect(
    "Selecciona las acciones que tomaste:",
    ["Hablé con alguien", "Medité", "Salí a caminar", "Escuché música", "Escribí", "Nada en particular"]
)

if st.button("💾 Guardar entrada de hoy"):
    entry = {
        "codigo_usuario": st.session_state.codigo_usuario,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "emociones": selected_emotions,
        "intensidades": emotion_intensities,
        "contexto": context,
        "acciones": coping_actions
    }
    st.session_state.diary_data.append(entry)
    guardar_diario_csv(entry)
    st.success("✔️ Entrada guardada exitosamente.")

# =========== HISTORIAL INDIVIDUAL (SIN DESCARGA) =================
if st.checkbox("📖 Mostrar historial de entradas"):
    df = cargar_diario_csv()
    if not df.empty:
        df_usuario = df[df["codigo_usuario"] == st.session_state.codigo_usuario]
        if not df_usuario.empty:
            st.dataframe(df_usuario)
            st.info("Solo el administrador puede descargar el historial en CSV.")
        else:
            st.info("Aún no has registrado entradas.")
    else:
        st.info("Aún no has registrado entradas.")

# =========== ACCESO ADMINISTRATIVO ================================
st.markdown("---")
st.subheader("🔑 Acceso administrativo (descarga de datos)")

if not st.session_state.admin_ok:
    admin_code = st.text_input("Código de administrador:", type="password")
    if st.button("Ingresar como administrador"):
        if admin_code == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.success("Acceso concedido. Puedes descargar los historiales.")
        else:
            st.error("Código incorrecto.")
else:
    st.success("🟢 Acceso de administrador activo.")

    # Listado de códigos únicos de usuario
    st.markdown("#### Códigos de usuario registrados")
    df = cargar_diario_csv()
    codigos_unicos = sorted(df["codigo_usuario"].unique())
    st.write("Códigos únicos registrados:")
    st.code('\n'.join(codigos_unicos), language="text")

    # Descarga historial individual de cualquier usuario
    st.markdown("#### Descargar historial individual de usuario")
    buscar_codigo = st.text_input("Código identificador de usuario para descargar historial:", max_chars=8, key="descarga_individual")
    if buscar_codigo:
        df_usuario = df[df["codigo_usuario"] == buscar_codigo]
        if not df_usuario.empty:
            st.dataframe(df_usuario)
            st.markdown(get_table_download_link(df_usuario, filename=f"diario_usuario_{buscar_codigo}.csv"), unsafe_allow_html=True)
        else:
            st.info("No hay datos para ese código de usuario.")

    # Descarga historial grupal de todos los usuarios
    st.markdown("#### Descargar historial grupal/completo")
    if not df.empty:
        st.dataframe(df)
        st.markdown(get_table_download_link(df, filename="diario_emocional_completo.csv"), unsafe_allow_html=True)
    else:
        st.info("No hay ingresos registrados aún.")

# =========== ENLACES Y PIE DE PÁGINA =========================
st.markdown("---")
st.subheader("📅 Agendar una consulta con un profesional")
booking_url = "https://forms.gle/MQwofoD14ELSp4Ye7"
st.markdown(f'<a href="{booking_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">AGENDAR CITA</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("📋 Registro de Usuario")
registro_url = "https://forms.gle/ZsM2xrWyUUU9ak6z7"
st.markdown(f'<a href="{registro_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">REGISTRARSE</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("💬 Enviar Mensaje por WhatsApp")
st.write("Si deseas enviar un mensaje por WhatsApp, haz clic en el siguiente botón:")
whatsapp_url = "https://wa.me/59897304859?text=Hola,%20necesito%20ayuda%20con%20mi%20salud%20mental."
st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">Enviar Mensaje</button></a>', unsafe_allow_html=True)

st.markdown("---")
st.write("VITAL LE AGRADECE POR CONFIAR Y USAR NUESTRO SERVICIO ❤️")
st.subheader("⚠️  Por consultas, y/o para participar y brindar tu servicio como profesional de la salud en nuestra app, comunicarse con:")
st.write("Mag. José González Gómez")
st.write("Correo: josehumbertogonzalezgomez@gmail.com")

st.markdown("---")
st.subheader("PROFESIONALES DE LA SALUD REFERENTES:")
st.write("Psic. Natalia Brandl")
st.write("Correo: brandlnatalia@gmail.com")
st.write("Atención presencial en: Germán Barbato 1358. Apto 501, y virtual")
st.write('Tesis: "Adicción a videojuegos como riesgo invisible de suicidio"')
st.write("Ps. Bryan Mora Durán")
st.write("Correo: bryanmoraduran@gmail.com")

st.markdown("---")
st.subheader("SECCIÓN DE TALLERES:")
st.write("Analista en Ciberseguridad Matías Alves")
st.write("Taller de concientización del uso de Redes Sociales (virtual)")
st.write("Correo: matiasalvessarmiento@gmail.com")
st.write("Lic. Guillermo Rodríguez")
st.write("Taller de Informática (virtual)")
st.write("Taller de inglés (virtual)")
st.write("Correo: williamforever2014@gmail.com")

st.markdown("---")
st.write("**Nota:** Esta herramienta proporciona diagnósticos preliminares basados en los síntomas ingresados. No reemplaza una consulta profesional.")
