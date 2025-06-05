import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import hashlib
import base64

# ================== CONFIGURACIÓN DE USUARIOS Y SESIÓN ==================
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = [
        {"username": "admin", "password": hashlib.sha256("admin123".encode()).hexdigest(), "rol": "admin"}
    ]
if "user" not in st.session_state:
    st.session_state["user"] = None
if "diary_data" not in st.session_state:
    st.session_state["diary_data"] = []
if "reset_form" not in st.session_state:
    st.session_state["reset_form"] = False
if "do_rerun" not in st.session_state:
    st.session_state["do_rerun"] = False

# ========== CONTROL DE RERUN ==========
if st.session_state["do_rerun"]:
    st.session_state["do_rerun"] = False
    st.rerun()

# ================== FUNCIONES AUXILIARES ==================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    return next((u for u in st.session_state["usuarios"] if u["username"] == username), None)

def get_table_download_link(df, filename="diario_emocional.csv"):
    csv_str = df.to_csv(index=False, encoding='utf-8')
    b64 = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Descargar historial como CSV</a>'
    return href

# ================== AUTENTICACIÓN ==================
def mostrar_login():
    st.title('🔒 Registrarse e Ingresar a: "DIARIO EMOCIONAL"')
    tabs = st.tabs(["Iniciar sesión", "Registrarse"])
    with tabs[0]:
        username = st.text_input("Usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Ingresar"):
            user = get_user(username)
            if user and user["password"] == hash_password(password):
                st.session_state["user"] = user
                st.success("¡Bienvenido/a!")
                st.session_state["do_rerun"] = True
            else:
                st.error("Usuario o contraseña incorrectos.")
    with tabs[1]:
        username = st.text_input("Nuevo usuario", key="reg_user")
        password = st.text_input("Nueva contraseña", type="password", key="reg_pass")
        if st.button("Registrarse"):
            if not username or not password:
                st.warning("Completa todos los campos.")
            elif get_user(username):
                st.warning("El nombre de usuario ya existe.")
            else:
                st.session_state["usuarios"].append({
                    "username": username,
                    "password": hash_password(password),
                    "rol": "usuario"
                })
                st.success("Usuario registrado. Ahora puedes iniciar sesión.")
                st.session_state["do_rerun"] = True

# ========== BLOQUE DE AUTENTICACIÓN ==========
if not st.session_state["user"]:
    mostrar_login()
    st.stop()

user = st.session_state["user"]
es_admin = user["rol"] == "admin"

# ================== TÍTULOS ================================
st.title("🌈 VITAL")
st.title("Asistente de Salud Mental con I.A.")
st.title("📔 Diario Emocional: Check-in")

# =========== ENTRADA DIARIO EMOCIONAL ======================
emotions = [
    {"label": "Alegre", "emoji": "😊"},
    {"label": "Triste", "emoji": "😢"},
    {"label": "Ira", "emoji": "😠"},
    {"label": "Confuso", "emoji": "😐"},
    {"label": "Gratitud", "emoji": "🙏"},
    {"label": "Miedo", "emoji": "😨"}
    {"label": "Feliz", "emoji": "😀"},
    {"label": "Ansioso", "emoji": "😰"},
    {"label": "Relajado", "emoji": "😌"},
    {"label": "Enojado", "emoji": "😡"},
    {"label": "Fiesta", "emoji": "🥳"},
    {"label": "Enamorado", "emoji": "😍"},
    {"label": "Cool", "emoji": "😎"},
    {"label": "Corazòn roto", "emoji": "💔"},
    {"label": "Asombrado", "emoji": "🤩"}
]


st.subheader("¿Cómo te sientes hoy?")

if st.session_state.reset_form:
    emociones_default = []
    contexto_default = ""
    acciones_default = []
    st.session_state.reset_form = False
else:
    emociones_default = []
    contexto_default = ""
    acciones_default = []

selected_emotions = st.multiselect(
    "Selecciona hasta 3 emociones:",
    options=[f"{e['emoji']} {e['label']}" for e in emotions],
    max_selections=3,
    default=emociones_default,
    key="emociones"
)

emotion_intensities = {}
for emotion in selected_emotions:
    level = st.slider(f"Intensidad de {emotion} (1-10):", 1, 10, 5, key=f"intensidad_{emotion}")
    emotion_intensities[emotion] = level

context = st.text_area("¿Qué hizo que te sintieras así?", placeholder="Describe brevemente lo que pasó...", key="contexto", value=contexto_default)

st.markdown("¿Qué hiciste para cuidarte?")
coping_actions = st.multiselect(
    "Selecciona las acciones que tomaste:",
    ["Hablé con alguien", "Medité", "Salí a caminar", "Escuché música", "Escribí", "Nada en particular"],
    default=acciones_default,
    key="acciones"
)

if st.button("💾 Guardar entrada de hoy"):
    entry = {
        "usuario": user["username"],
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "emociones": ";".join(selected_emotions) if selected_emotions else "",
        "intensidades": ";".join([f"{k}:{v}" for k, v in emotion_intensities.items()]) if emotion_intensities else "",
        "contexto": context,
        "acciones": ";".join(coping_actions) if coping_actions else ""
    }
    st.session_state["diary_data"].append(entry)
    st.success("✔️ Entrada guardada exitosamente.")
    st.session_state.reset_form = True
    st.rerun()

# =========== HISTORIAL INDIVIDUAL (NO DESCARGA SI NO ES ADMIN) ============
st.markdown("---")
if st.checkbox("📖 Mostrar historial de entradas"):
    df = pd.DataFrame(st.session_state["diary_data"])
    if not df.empty:
        if es_admin:
            st.dataframe(df)
            st.markdown(get_table_download_link(df, filename="diario_emocional_completo.csv"), unsafe_allow_html=True)
        else:
            df_usuario = df[df["usuario"] == user["username"]]
            if not df_usuario.empty:
                st.dataframe(df_usuario)
                st.info("Solo el administrador puede descargar el historial en CSV.")
            else:
                st.info("Aún no has registrado entradas.")
    else:
        st.info("Aún no has registrado entradas.")

# =========== ADMIN: DESCARGA DE USUARIOS INDIVIDUALES ===============
if es_admin:
    st.markdown("---")
    st.subheader("🔑 Acceso administrativo (descarga de datos)")
    df = pd.DataFrame(st.session_state["diary_data"])
    if not df.empty:
        st.markdown("#### Usuarios registrados")
        codigos_unicos = sorted(df["usuario"].unique())
        st.write("Usuarios registrados:")
        st.code('\n'.join(codigos_unicos), language="text")

        st.markdown("#### Descargar historial individual de usuario")
        buscar_usuario = st.text_input("Nombre de usuario para descargar historial:", key="descarga_individual")
        if buscar_usuario:
            df_usuario = df[df["usuario"] == buscar_usuario]
            if not df_usuario.empty:
                st.dataframe(df_usuario)
                st.markdown(get_table_download_link(df_usuario, filename=f"diario_usuario_{buscar_usuario}.csv"), unsafe_allow_html=True)
            else:
                st.info("No hay datos para ese usuario.")
    else:
        st.info("No hay ingresos registrados aún.")

# =========== ESTADÍSTICA (BARRAS HORIZONTALES) ===============
st.markdown("---")
st.subheader("📊 Estadísticas de emociones")
df = pd.DataFrame(st.session_state["diary_data"])
if not df.empty:
    # Contar emociones
    from collections import Counter
    todas_las_emociones = []
    for em in df["emociones"]:
        if isinstance(em, str) and em:
            todas_las_emociones.extend(em.split(";"))
    conteo = Counter(todas_las_emociones)
    if conteo:
        conteo_df = pd.DataFrame.from_dict(conteo, orient='index', columns=['Cantidad']).sort_values("Cantidad")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        conteo_df.plot.barh(ax=ax, color="#A5D6A7")
        ax.set_xlabel("Cantidad")
        ax.set_ylabel("Emoción")
        ax.set_title("Emociones registradas")
        st.pyplot(fig)
    else:
        st.info("Aún no hay emociones registradas.")
else:
    st.info("Aún no hay emociones registradas.")

# =========== CIERRE DE SESIÓN ===============
if st.button("Cerrar sesión"):
    st.session_state["user"] = None
    st.session_state["do_rerun"] = True

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
