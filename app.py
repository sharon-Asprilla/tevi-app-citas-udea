import streamlit as st
import sqlite3
import bcrypt
import os
from email_validator import validate_email, EmailNotValidError

#logo en el navegador 

st.set_page_config(
    page_title="TeVi 👀",
    page_icon="img/logo_sinfondo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<link rel="manifest" href="/static/manifest.json">
<script>
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js")
    .then(() => console.log("Service Worker registrado"))
    .catch(err => console.error("Error:", err));
}
</script>
""", unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar estilos
local_css("style.css")






# ------------------ BASE DE DATOS ------------------
def init_db():
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correo TEXT UNIQUE,
        contraseña TEXT,
        facultad TEXT,
        carrera TEXT,
        edad INTEGER,
        intereses TEXT,
        foto TEXT,
        ubicacion TEXT,
        premium INTEGER DEFAULT 0,
        sexo TEXT,
        preferencia TEXT
    )""")

    # Migración segura: Verificar si columnas nuevas existen para evitar errores
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN foto TEXT")
    except sqlite3.OperationalError:
        pass 

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN sexo TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN preferencia TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        liked_id INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS dislikes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        disliked_id INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario1_id INTEGER,
        usuario2_id INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        remitente_id INTEGER,
        mensaje TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        monto INTEGER,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    conn.commit()
    conn.close()

# Asegurar que la carpeta de subidas existe al inicio
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Import authentication functions from auth.py
from auth import login, registro, forgot_password

# ------------------ PERFIL ------------------
def perfil(usuario_id):
    st.info("dele en las >> para poder ver el menu, esta  al lado izquierdo")
    st.title("Mi Perfil")
    st.text("     crea tu perfil para empezar a ver gente en la u  ")
    
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    c.execute("SELECT facultad, carrera, edad, intereses, ubicacion, foto, sexo, preferencia FROM usuarios WHERE id=?", (usuario_id,))
    datos = c.fetchone()
    conn.close()

    # Valores actuales o vacíos
    fac_val = datos[0] if datos and datos[0] else ""
    car_val = datos[1] if datos and datos[1] else ""
    edad_val = datos[2] if datos and datos[2] else 18
    int_val = datos[3] if datos and datos[3] else ""
    ubi_val = datos[4] if datos and datos[4] else ""
    foto_actual = datos[5] if datos and datos[5] else None
    sexo_val = datos[6] if datos and datos[6] else "Femenino"
    pref_val = datos[7] if datos and datos[7] else "Hombres"

    # Variable para controlar la ubicación en el formulario
    if "temp_ubicacion" not in st.session_state:
        st.session_state.temp_ubicacion = ubi_val

    with st.form("perfil_form"):
        st.info("Completa tu perfil  y dale en guardar")
        
        col1, col2 = st.columns(2)
        with col1:
            facultad = st.text_input("Facultad", value=fac_val)
            edad = st.number_input("Edad", 16, 99, value=edad_val)
            sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"], 
                                index=["Femenino", "Masculino", "Otro"].index(sexo_val) if sexo_val in ["Femenino", "Masculino", "Otro"] else 0)
            preferencia = st.selectbox("Preferencia sexual", ["Hombres", "Mujeres"], 
                                        index=["Hombres", "Mujeres"].index(pref_val) if pref_val in ["Hombres", "Mujeres"] else 0)
            
            # Sección de Ubicación Automática
            st.markdown("---")
            st.markdown("**Ubicación Real**")
            # Simulamos la obtención de coordenadas del celular
            st.write("Presiona para obtener la ubicación de tu celular:")
            if st.form_submit_button("Detectar mi ubicación actual"):
                st.session_state.temp_ubicacion = "Ubicación Detectada (GPS)"
                st.success("Ubicación obtenida exitosamente")
            
            # Campo de solo lectura para confirmar
            ubicacion = st.text_input("Estado Ubicación", value=st.session_state.temp_ubicacion, disabled=True)
            
        with col2:
            carrera = st.text_input("Carrera", value=car_val)
            intereses = st.text_area("Intereses y Descripción", value=int_val, height=150)
        
        st.markdown("---")
        col_foto1, col_foto2 = st.columns([1, 2])
        with col_foto1:
            if foto_actual:
                # Validación segura de ruta de imagen
                img_show = "https://placehold.co/100x100?text=Foto"
                if foto_actual and isinstance(foto_actual, str) and os.path.exists(foto_actual):
                    img_show = foto_actual
                st.image(img_show, width=100, caption="Actual", clamp=True)
            else:
                st.warning("Sin foto de perfil")
        with col_foto2:
            foto = st.file_uploader("Actualizar foto", type=["jpg","png"])
        
        # Botón principal de guardado
        submitted = st.form_submit_button("Guardar Perfil")

    if submitted:
        # Validación: Ubicación obligatoria, Foto opcional
        if not ubicacion:
            st.error("Debes detectar tu ubicación para continuar.")
        else:
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            
            # Definir nombre de la foto (la nueva o mantener la vieja)
            nombre_foto = foto_actual
            if foto:
                # Guardar el archivo físicamente
                file_path = os.path.join("uploads", f"{usuario_id}_{foto.name}")
                with open(file_path, "wb") as f:
                    f.write(foto.getbuffer())
                nombre_foto = file_path

            c.execute("""UPDATE usuarios SET facultad=?, carrera=?, edad=?, intereses=?, ubicacion=?, foto=?, sexo=?, preferencia=? WHERE id=?""",
                    (facultad, carrera, edad, intereses, ubicacion, nombre_foto, sexo, preferencia, usuario_id))
            conn.commit()
            conn.close()
            st.session_state["menu_actual"] = "Perfiles"
            st.rerun()

# ------------------ PERFILES / MATCH ------------------
def ver_perfiles(usuario_id):
    st.title("👀 Quién me miró")
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    # Obtener preferencia del usuario actual para filtrar
    c.execute("SELECT preferencia FROM usuarios WHERE id=?", (usuario_id,))
    pref_res = c.fetchone()
    preferencia_usuario = pref_res[0] if pref_res else "Hombres"
    
    # Mapeo de preferencia a sexo en la base de datos
    sexo_buscado = "Masculino" if preferencia_usuario == "Hombres" else "Femenino"

    c.execute("""SELECT id, facultad, carrera, intereses, edad, foto, correo FROM usuarios 
                 WHERE id!=? 
                 AND sexo=?
                 AND id NOT IN (SELECT liked_id FROM likes WHERE usuario_id=?)
                 AND id NOT IN (SELECT disliked_id FROM dislikes WHERE usuario_id=?)""", 
                 (usuario_id, sexo_buscado, usuario_id, usuario_id))
    perfiles = c.fetchall()
    conn.close()

    if not perfiles:
        st.info("No hay perfiles nuevos por ahora. ¡Vuelve pronto!")
        return

    # Mostrar perfiles en columnas (tarjetas)
    col1, col2, col3 = st.columns(3)
    
    for i, p in enumerate(perfiles):
        pid, p_facultad, p_carrera, p_intereses, p_edad, p_foto, p_correo = p
        
        # Distribuir en columnas
        with (col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3):
            with st.container(border=True):
                # Mostrar foto del usuario
                if p_foto and os.path.exists(p_foto):
                    st.image(p_foto, use_container_width=True)
                else:
                    st.image("https://placehold.co/300x200?text=Sin+Foto", use_container_width=True)

                nombre = p_correo.split('@')[0].capitalize()
                st.markdown(f"### {nombre}, {p_edad or 18}")
                st.markdown(f"🎓 **{p_carrera or 'Estudiante'}**\n📍 {p_facultad}")
                st.write(f"_{p_intereses or 'Sin descripción'}_")
                
                col_no, col_si = st.columns(2)
                with col_no:
                    if st.button(" No interesa", key=f"dislike_{pid}"):
                        conn = sqlite3.connect("tevi.db")
                        c = conn.cursor()
                        c.execute("INSERT INTO dislikes (usuario_id, disliked_id) VALUES (?,?)", (usuario_id, pid))
                        conn.commit()
                        conn.close()
                        st.rerun()
                
                with col_si:
                    if st.button("👀 Me miró", key=f"like_{pid}", type="primary"):
                        conn = sqlite3.connect("tevi.db")
                        c = conn.cursor()
                        
                        # Registrar Like
                        c.execute("INSERT INTO likes (usuario_id, liked_id) VALUES (?,?)", (usuario_id, pid))
                        
                        # Verificar Match
                        c.execute("SELECT * FROM likes WHERE usuario_id=? AND liked_id=?", (pid, usuario_id))
                        match_data = c.fetchone()
                        
                        if match_data:
                            c.execute("INSERT INTO matches (usuario1_id, usuario2_id) VALUES (?,?)", (min(usuario_id, pid), max(usuario_id, pid)))
                            st.balloons()
                            st.toast("¡ES UN MATCH! ", icon="😍")
                            st.success(f"¡Hiciste Match! Ahora puedes chatear.")
                        else:
                            st.toast("Le avisamos que lo miraste ", icon="✅")
                        
                        conn.commit()
                        conn.close()
                        st.rerun()

# ------------------ CHAT ------------------
def chat(usuario_id):
    st.title("💬 Chat")

    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    
    # JOIN para obtener el correo/nombre del otro usuario
    # Usamos try-except para evitar errores si las columnas de fotos no están perfectamente sincronizadas
    try:
        c.execute("""SELECT m.id, u1.correo, u2.correo, u1.id, u2.id, u1.foto, u2.foto 
                    FROM matches m
                    JOIN usuarios u1 ON m.usuario1_id=u1.id
                    JOIN usuarios u2 ON m.usuario2_id=u2.id
                    WHERE m.usuario1_id=? OR m.usuario2_id=?""", (usuario_id, usuario_id))
    except sqlite3.OperationalError:
        # Fallback por seguridad
        c.execute("""SELECT m.id, u1.correo, u2.correo, u1.id, u2.id, NULL, NULL
                    FROM matches m
                    JOIN usuarios u1 ON m.usuario1_id=u1.id
                    JOIN usuarios u2 ON m.usuario2_id=u2.id
                    WHERE m.usuario1_id=? OR m.usuario2_id=?""", (usuario_id, usuario_id))
        
    matches = c.fetchall()

    if not matches:
        st.info("No tienes chats activos. Haz match en 'Perfiles' para empezar a hablar.")
        conn.close()
        return

    for m in matches:
        match_id = m[0]
        # Identificar usuarios
        if m[3] == usuario_id: 
            nombre_otro = m[2].split('@')[0]
            foto_otro = m[6]
            foto_mia = m[5]
        else:
            nombre_otro = m[1].split('@')[0]
            foto_otro = m[5]
            foto_mia = m[6]
            
        # Validar ruta de avatar para evitar errores
        avatar_otro_valido = foto_otro if (foto_otro and os.path.exists(foto_otro)) else None
    from chat import chat as chat_v2
    chat_v2(usuario_id)

    conn.close()

# ------------------ PREMIUM ------------------
def premium(usuario_id):
    st.title(" Premium")
    
    st.markdown("### 🚧 Función en Mantenimiento")
    st.image("https://media.giphy.com/media/l0HlOaQcLJ2hHpYcw/giphy.gif", width=300)
    st.warning("⚠️ Los pagos aún no está disponible aun")
    st.info("Estamos trabajando para traerte funciones exclusivas muy pronto. ¡Gracias por tu paciencia!")

# ------------------ APP PRINCIPAL ------------------
init_db()

if "usuario_id" not in st.session_state:
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "Registro" # Default to registration as requested

    if st.session_state.auth_mode == "Login":
        login()
    elif st.session_state.auth_mode == "Registro":
        registro()
    elif st.session_state.auth_mode == "Forgot_Password":
        forgot_password()
else:
    st.sidebar.title("Navegación")
    st.sidebar.info("ℹ Dele ahí para ver el menú")
   
    
    # Notificación de "Miradas" (Likes recibidos) en la barra lateral
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM likes WHERE liked_id=?", (st.session_state["usuario_id"],))
    num_likes = c.fetchone()[0]
    conn.close()
    if num_likes > 0:
        st.sidebar.info(f"**{num_likes} personas** te han mirado.")
    
    # Control de navegación por estado para permitir redirecciones
    if "menu_actual" not in st.session_state:
        st.session_state["menu_actual"] = "Perfil" # Por defecto ir a perfil primero
    
    # Menú de navegación con botones (sin puntos de selección)
    if st.sidebar.button("Inicio"):
        st.session_state["menu_actual"] = "Inicio"
    if st.sidebar.button("Mi Perfil"):
        st.session_state["menu_actual"] = "Perfil"
    if st.sidebar.button("Perfiles"):
        st.session_state["menu_actual"] = "Perfiles"
    if st.sidebar.button("Chat"):
        st.session_state["menu_actual"] = "Chat"
    if st.sidebar.button("Premium"):
        st.session_state["menu_actual"] = "Premium"
    
    st.sidebar.markdown("---")
    # Lógica de confirmación de Logout
    if "confirmar_logout" not in st.session_state:
        st.session_state["confirmar_logout"] = False
    if "confirmar_borrado" not in st.session_state:
        st.session_state["confirmar_borrado"] = False

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["confirmar_logout"] = True
        st.rerun()

    if st.sidebar.button("Borrar Cuenta"):
        st.session_state["confirmar_borrado"] = True
        st.rerun()

    if st.session_state["confirmar_logout"]:
        st.sidebar.warning("¿Estás seguro de salir?")
        col_si, col_no = st.sidebar.columns(2)
        if col_si.button("Sí"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if col_no.button("No"):
            st.session_state["confirmar_logout"] = False
            st.rerun()

    if st.session_state["confirmar_borrado"]:
        st.sidebar.error("⚠️ ¿ELIMINAR CUENTA? Esto borrará tus matches y mensajes permanentemente.")
        col_si_b, col_no_b = st.sidebar.columns(2)
        if col_si_b.button("Sí, borrar todo", key="del_acc_yes"):
            uid = st.session_state["usuario_id"]
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            # Limpieza profunda de datos relacionados para no dejar rastro
            c.execute("DELETE FROM mensajes WHERE match_id IN (SELECT id FROM matches WHERE usuario1_id=? OR usuario2_id=?)", (uid, uid))
            c.execute("DELETE FROM matches WHERE usuario1_id=? OR usuario2_id=?", (uid, uid))
            c.execute("DELETE FROM likes WHERE usuario_id=? OR liked_id=?", (uid, uid))
            c.execute("DELETE FROM dislikes WHERE usuario_id=? OR disliked_id=?", (uid, uid))
            c.execute("DELETE FROM pagos WHERE usuario_id=?", (uid,))
            c.execute("DELETE FROM usuarios WHERE id=?", (uid,))
            conn.commit()
            conn.close()
            
            # Limpiar sesión y redirigir al registro
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if col_no_b.button("No, cancelar", key="del_acc_no"):
            st.session_state["confirmar_borrado"] = False
            st.rerun()

    if st.session_state["menu_actual"] == "Perfil":
        perfil(st.session_state["usuario_id"])
    elif st.session_state["menu_actual"] == "Perfiles":
        ver_perfiles(st.session_state["usuario_id"])
    elif st.session_state["menu_actual"] == "Chat":
        chat(st.session_state["usuario_id"])
    elif st.session_state["menu_actual"] == "Premium":
        premium(st.session_state["usuario_id"])
    else:
        st.title(" ¡Bienvenido a TeVi!")
        st.markdown("""
        ### ¿Has visto a alguien en la U y no sabes cómo hablarle?
        Todos hemos tenido ese **crush** que vemos a diario en la biblioteca, en la cafetería o cruzando el campus, pero a veces los nervios nos ganan y no sabemos cómo acercarnos. **TeVi** nace para que esos encuentros de pasillo se conviertan en algo más.

        Esta es la app de citas diseñada exclusivamente para nuestra comunidad universitaria. Aquí puedes encontrar a esa persona que te llama la atención, descubrir si tienen gustos en común y romper el hielo de forma segura y divertida.

        **¡El amor de tu vida podría estar sentado en el salón de al lado!** No dejes pasar la oportunidad de conectar con alguien especial de tu propia universidad.
        """)
        st.image("https://images.unsplash.com/photo-1543269865-cbf427effbad?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", caption="Tu historia de amor comienza en el campus")
