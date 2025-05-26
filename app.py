import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime
import os

#import streamlit as st

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

#import streamlit as st
import streamlit.components.v1 as components

# Inyectar el manifest y el registro del service worker
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
#st.title("Diagnóstico Preliminar de Salud Mental")

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
    st.success("✔️ Entrada guardada exitosamente.")

# Mostrar historial
if st.checkbox("📖 Mostrar historial de entradas"):
    if st.session_state.diary_data:
        df = pd.DataFrame(st.session_state.diary_data)
        st.dataframe(df)
    else:
        st.info("Aún no has registrado entradas.")


### Archivo CSV para almacenar los datos del estado de ánimo
CSV_FILE = "historial_estado_animo.csv"

# Inicializar archivo CSV si no existe
def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w") as file:
            file.write("Fecha,Estado de Ánimo\n")

# Guardar estado de ánimo en el archivo CSV
def guardar_estado_animo(fecha, estado):
    with open(CSV_FILE, "a") as file:
        file.write(f"{fecha},{estado}\n")

# Cargar los datos del CSV
def cargar_datos_estado_animo():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Fecha", "Estado de Ánimo"])

# Inicializar el archivo CSV
inicializar_csv()

# Cargar datos desde el archivo CSV enriquecido con verificación
@st.cache_data
def cargar_datos_enriquecidos():
    try:
        return pd.read_csv("datos_enriquecidos.csv", encoding="latin-1")
    except FileNotFoundError:
        st.error("Error: El archivo CSV no se encuentra en el directorio. Asegúrate de que el archivo exista.")
        return pd.DataFrame()  # Retorna un DataFrame vacío si el archivo no se encuentra

data = cargar_datos_enriquecidos()

##"""# Función para normalizar nombres de enfermedades
##def normalizar_enfermedad(enfermedad):
   ## enfermedad = enfermedad.lower()
    ##if "pánico" in enfermedad:
        ##return "Trastorno de Pánico"
    ##elif "bipolar" in enfermedad:
       ## return "Trastorno Bipolar"
    ##elif "estado de ánimo" in enfermedad:
        ##return "Trastorno del Estado de Ánimo"
    ##elif "obsesivo" in enfermedad or "compulsivo" in enfermedad:
        ##return "Trastorno Obsesivo-Compulsivo"
    ##elif "fobia" in enfermedad:
        ##return "Fobias"
    ##elif "postparto" in enfermedad:
       ## return "Depresión Postparto"
    ##return enfermedad

### Función para obtener diagnóstico basado en los síntomas
##def obtener_diagnostico(sintomas):
   ## resultados = {}
    ##if not data.empty:
        ##sintomas_lista = [sintoma.lower().strip() for sintoma in sintomas.split(',')]
        ##for index, row in data.iterrows():
            ##if any(sintoma in row['Síntomas'].lower() for sintoma in sintomas_lista):
                ##enfermedad = normalizar_enfermedad(row['Enfermedad'])
                ##descripcion = row['Descripción']
                ##url = row['URL']
                
                ##if enfermedad not in resultados:
                    ##resultados[enfermedad] = {'descripcion': descripcion, 'urls': [url]}
                ##else:
                    ##if descripcion not in resultados[enfermedad]['descripcion']:
                        ##resultados[enfermedad]['descripcion'] += f"\n\n{descripcion}"
                    ##if url not in resultados[enfermedad]['urls']:
                       ## resultados[enfermedad]['urls'].append(url)
    ##return resultados"""

# Título de la aplicación
#st.title("🌈 VITAL")
#st.title("Asistente de Salud Mental con I.A.")
##st.title("Diagnóstico Preliminar de Salud Mental")
##st.markdown(
    ##"Bienvenido a **VITAL**, una aplicación que utiliza Inteligencia Artificial "
    ##"para analizar síntomas y proporcionar un diagnóstico estimado de salud mental. "
    ##"⚠️ **Recuerda**: Este diagnóstico es solo una guía. Para una evaluación completa, "
    ##"puedes consultar con un profesional de la salud mental registrándote a nuestro servicio."
##)

# Robot de chat
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

# Sección 1: Diagnóstico basado en síntomas
##st.subheader("📋 Ingresa tus síntomas")
##st.write("Ingresa tus síntomas separados por comas y recibe información y enlaces a posibles trastornos relacionados.")
##st.write("Cuanta más información ingreses sobre cómo te sientes, ayuda a mejorar el posible diagnóstico")

##sintomas_usuario = st.text_input("Describe tus síntomas (por ejemplo: tristeza, insomnio, fatiga)")

# Botón para procesar
st.markdown(
    """
    <style>
    .stButton button {
        background-color: #ADD8E6;
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

##if st.button("Obtener Diagnóstico"):
   ## if sintomas_usuario:
        ##diagnostico = obtener_diagnostico(sintomas_usuario)
        ##if diagnostico:
           ## st.success("**POSIBLE DIAGNÓSTICO O PATOLOGÍAS ASOCIADAS A TUS SÍNTOMAS:**")
           ## for enfermedad, info in diagnostico.items():
                ##st.subheader(enfermedad)
                ##st.write(info['descripcion'])
                ##for url in info['urls']:
                    ##st.markdown(f"[Más información aquí]({url})", unsafe_allow_html=True)
       ## else:
           ## st.warning("No se identificaron trastornos específicos basados en los síntomas proporcionados. Por favor, consulta con un profesional.")
    ##else:
        ##st.error("Por favor, ingresa al menos un síntoma para obtener el diagnóstico.")

# Sección 2: Seguimiento del Estado de Ánimo
##st.markdown("---")
##st.subheader("📊 Seguimiento del Estado de Ánimo")
##st.write("Registra tu estado de ánimo cada vez que sientas un cambio del mismo o cuando consideres necesario registrarlo, para así llevar un seguimiento de cómo te sientes a lo largo del tiempo.")

##estado_animo = st.selectbox(
    ##"¿Cómo te sientes hoy?",
    ##[
       ## "Feliz 😀", "Triste 😢", "Ansioso 😰", "Relajado 😌", "Enojado 😡",
       ## "Fiesta 🥳", "Enamorado 😍", "Cool 😎", "Asombrado 🤩", "Arcoíris 🌈",
        ##"Neutral 😐", "Pensativo 🤔", "Tristeza leve 😔", "Miedo 😱",
       ## "Agotado 😩", "Meditación 🧘", "Idea 💡", "Energía ⚡", "Confuso 🌪️",
        ##"Corazón roto 💔"
    ##]
##)

##if st.button("Registrar Estado de Ánimo"):
    ##fecha_actual = datetime.now().strftime("%Y-%m-%d")
    ##guardar_estado_animo(fecha_actual, estado_animo)
    ##st.success(f"¡Estado de ánimo '{estado_animo}' registrado para la fecha {fecha_actual}!")

# Sección 3: Historial de Estados de Ánimo
##st.markdown("---")
##datos = cargar_datos_estado_animo()
##st.subheader("📋 Historial de Estados de Ánimo")
##if not datos.empty:
    ##st.write(datos)
##else:
    ##st.write("No hay datos registrados aún.")

# Sección 4: Generación de gráficos
##if not datos.empty:
    ##datos["Fecha"] = pd.to_datetime(datos["Fecha"]).dt.date  # Asegurarse de que solo se use la fecha, sin hora.

    ##st.subheader("📊 Tendencia Temporal de Estados de Ánimo")
    ##resumen = datos["Estado de Ánimo"].value_counts()
    ##fig, ax = plt.subplots()
    ##ax.bar(resumen.index, resumen.values, color="skyblue")
    ##ax.set_title("Frecuencia de Estados de Ánimo")
    ##ax.set_xlabel("Estado de Ánimo")
    ##ax.set_ylabel("Frecuencia")
    ##st.pyplot(fig)

    # Configuración del gráfico de tendencia temporal (191 a 199)
    #fig, ax = plt.subplots()
    #datos.groupby("Fecha").size().plot(ax=ax, kind="line", marker="o", color="green")
    #ax.set_title("Tendencia de Estados de Ánimo a lo Largo del Tiempo")
    #ax.set_xlabel("Fecha")
    #ax.set_ylabel("Cantidad de Registros")
    #ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))  # Mostrar fechas correctamente
    #plt.xticks(rotation=45)
    #st.pyplot(fig)

# Configuración del gráfico de tendencia temporal
#fig, ax = plt.subplots()

# Obtener la fecha actual
#fecha_actual = datetime.now().date()  # Fecha actual dinámica

# Filtrar los datos desde la fecha actual
#datos_filtrados = datos[datos["Fecha"] >= fecha_actual]

# Verificar si hay datos después de filtrar
#if datos_filtrados.empty:
    #st.warning("No hay datos registrados después de la fecha actual.")
#else:
    # Graficar los datos filtrados
    #datos_filtrados.groupby("Fecha").size().plot(ax=ax, kind="line", marker="o", color="green")
    #ax.set_title("Tendencia de Estados de Ánimo a lo Largo del Tiempo")
    #ax.set_xlabel("Fecha")
    #ax.set_ylabel("Cantidad de Registros")
    #ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))  # Mostrar fechas correctamente
    #plt.xticks(rotation=45)
    #st.pyplot(fig)

# Sección 5: Opciones adicionales (Agendar cita, Registro, WhatsApp)
st.markdown("---")
st.subheader("📅 Agendar una consulta con un profesional")
st.write("Si deseas hablar con un profesional de salud mental, agenda una cita a continuación.")
#booking_url = "https://forms.gle/MQwofoD14ELSp4Ye7"
#st.markdown(f'[**Agendar Cita**]({booking_url})', unsafe_allow_html=True)

# Enlace a Google Forms o WhatsApp (elige uno)
booking_url = "https://forms.gle/MQwofoD14ELSp4Ye7"  # Enlace de tu formulario de citas
st.markdown(f'<a href="{booking_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">AGENDAR CITA</button></a>', unsafe_allow_html=True)



st.markdown("---")
st.subheader("📋 Registro de Usuario")
registro_url = "https://forms.gle/ZsM2xrWyUUU9ak6z7"
#st.markdown(f'[**Registrarse**]({registro_url})', unsafe_allow_html=True)
st.markdown(f'<a href="{registro_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">REGISTRARSE</button></a>', unsafe_allow_html=True)


#st.markdown("---")
# WhatsApp messaging section
st.markdown("---")
st.subheader("💬 Enviar Mensaje por WhatsApp")
st.write("Si deseas enviar un mensaje por WhatsApp, haz clic en el siguiente botón:")

# WhatsApp Click to Chat URL
whatsapp_url = "https://wa.me/59897304859?text=Hola,%20necesito%20ayuda%20con%20mi%20salud%20mental."  # Reemplaza con tu número de teléfono

# Button for WhatsApp Click to Chat
st.markdown(f'<a href="{whatsapp_url}" target="_blank"><button style="background-color: #25D366; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">Enviar Mensaje</button></a>', unsafe_allow_html=True)


#st.subheader("💬 Enviar Mensaje por WhatsApp")
#st.write("Si deseas enviar un mensaje por WhatsApp, haz clic en el siguiente botón:")
#whatsapp_url = "https://wa.me/59897304859?text=Hola,%20necesito%20ayuda%20con%20mi%20salud%20mental."
#st.markdown(f'[**Enviar Mensaje por WhatsApp**]({whatsapp_url})', unsafe_allow_html=True)
#st.markdown(f'<a href="{booking_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer;">Enviar Mensaje</button></a>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.write("VITAL LE AGRADECE POR CONFIAR Y USAR NUESTRO SERVICIO ❤️")
st.subheader("⚠️  Por consultas, y/o para participar y brindar tu servicio como profesional de la salud en nuestra app, comunicarse con:")
st.write("Mag. José González Gómez")
st.write("Correo: josehumbertogonzalezgomez@gmail.com")

# Sección 6: Profesionales referentes
st.markdown("---")
st.subheader("PROFESIONALES DE LA SALUD REFERENTES:")
st.write("Psic. Natalia Brandl")
st.write("Correo: brandlnatalia@gmail.com")
st.write("Atención presencial en: Germán Barbato 1358. Apto 501, y virtual")
st.write('Tesis: "Adicción a videojuegos como riesgo invisible de suicidio"')
st.write("Ps. Bryan Mora Durán")
st.write("Correo: bryanmoraduran@gmail.com")

# Sección 7: Talleres
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
