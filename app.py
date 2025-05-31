import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
import os
import csv
import base64
import streamlit.components.v1 as components

# Inyecta el manifest y los íconos en el <head>
st.markdown("""
<link rel="manifest" href="https://jhgonzalezuruguay.github.io/SALUD_MENTAL_3.0/manifest.json">
<link rel="icon" type="image/png" sizes="192x192" href="https://jhgonzalezuruguay.github.io/SALUD_MENTAL_3.0/icon-192.png">
<link rel="icon" type="image/png" sizes="512x512" href="https://jhgonzalezuruguay.github.io/SALUD_MENTAL_3.0/icon-512.png">
""", unsafe_allow_html=True)

# Registra el service worker
st.markdown("""
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('https://jhgonzalezuruguay.github.io/SALUD_MENTAL_3.0/sw.js');
  });
}
</script>
""", unsafe_allow_html=True)

components.html(
    """
    <link rel="manifest" href="/manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js');
            });
        }
    </script>
    """,
    height=0,
)

# Archivo CSV para el diario emocional
DIARIO_CSV = "diario_emocional.csv"

# Función: Guardar entrada en CSV
def guardar_diario_csv(entry):
    file_exists = os.path.isfile(DIARIO_CSV)
    # Convertir listas y diccionarios a string para guardar en CSV
    entry_to_save = entry.copy()
    entry_to_save["emociones"] = ";".join(entry["emociones"]) if entry["emociones"] else ""
    entry_to_save["intensidades"] = ";".join([f"{k}:{v}" for k, v in entry["intensidades"].items()]) if entry["intensidades"] else ""
    entry_to_save["acciones"] = ";".join(entry["acciones"]) if entry["acciones"] else ""
    with open(DIARIO_CSV, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=entry_to_save.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry_to_save)

# Función: Cargar todas las entradas desde el CSV
def cargar_diario_csv():
    if os.path.isfile(DIARIO_CSV):
        df = pd.read_csv(DIARIO_CSV)
        return df
    else:
        return pd.DataFrame(columns=["fecha", "emociones", "intensidades", "contexto", "acciones"])

# Función: Crear enlace de descarga
def get_table_download_link(df):
    csv_str = df.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="diario_emocional.csv">Descargar historial como CSV</a>'
    return href

# Inicializa la base de datos temporal
if "diary_data" not in st.session_state:
    st.session_state.diary_data = []

# Lista de emociones disponibles
emotions = [
    {"label": "Alegría", "emoji": "😊"},
    {"label": "Ansiedad", "emoji": "😟"},
    {"label": "Tristeza", "emoji": "😢"},
    {"label": "Ira", "emoji": "😠"},
    {"label": "Confusión", "emoji": "😐"},
    {"label": "Gratitud", "emoji": "🙏"},
    {"label": "Miedo", "emoji": "😨"}
]
st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")

st.title("📔 Diario Emocional: Check-in")

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

# Guardar entrada
if st.button("💾 Guardar entrada de hoy"):
    entry = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "emociones": selected_emotions,
        "intensidades": emotion_intensities,
        "contexto": context,
        "acciones": coping_actions
    }
    st.session_state.diary_data.append(entry)
    guardar_diario_csv(entry)  # Guarda en CSV permanente
    st.success("✔️ Entrada guardada exitosamente.")

# Mostrar historial
if st.checkbox("📖 Mostrar historial de entradas"):
    df = cargar_diario_csv()
    if not df.empty:
        st.dataframe(df)
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)
    else:
        st.info("Aún no has registrado entradas.")

# Chat de asistencia
st.sidebar.title("🤖 Chat de Asistencia")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hola! Soy tu asistente de salud mental. ¿Cómo te sientes hoy?"}
    ]

for message in st.session_state.messages:
    with st.sidebar:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.sidebar.chat_input("Cuéntame cómo te sientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.sidebar:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = "Gracias por compartir. Si necesitas más ayuda, revisa las secciones de la aplicación."
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# ---- Otras secciones y enlaces ----
st.markdown("---")
st.subheader("📅 Agendar una consulta con un profesional")
st.write("Si deseas hablar con un profesional de salud mental, agenda una cita a continuación.")
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

# Footer y profesionales
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
