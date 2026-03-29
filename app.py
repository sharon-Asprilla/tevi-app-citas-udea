import streamlit as st
import sqlite3
import bcrypt
import os
from email_validator import validate_email, EmailNotValidError
import os



#logo en el navegador 

st.set_page_config(
    page_title="TeVi 👀",
    page_icon="img/logo_sinfondo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
<link rel="manifest" href="/static/manifest.json">
<script>
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js")
    .then(() => console.log("Service Worker registrado"))
    .catch(err => console.error("Error:", err));
}
</script>
</style>
""", unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargar estilos
local_css("style.css")


# CSS para ocultar elementos por defecto
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}     /* Oculta el menú de hamburguesa */
    footer {visibility: hidden;}        /* Oculta el pie de página */
    header {visibility: hidden;}        /* Oculta el encabezado por defecto */
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)




# Cuadro de información estilo Streamlit
if st.button("creadora"):
    st.info("""
    **Desarrolladora:** Sharon Asprilla  
    **GitHub:** [sharon-Asprilla](https://github.com/sharon-Asprilla)  
    Aquí puedes ver más proyectos que ha creado, dar click para mas información.
    """, icon="ℹ️")
    



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

    try:
        c.execute("ALTER TABLE mensajes ADD COLUMN tipo TEXT DEFAULT 'text'")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN orientacion TEXT")
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
        tipo TEXT DEFAULT 'text',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS bloqueos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        bloqueado_id INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(bloqueado_id) REFERENCES usuarios(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS reportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        reportado_id INTEGER,
        motivo TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(reportado_id) REFERENCES usuarios(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        monto INTEGER,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS resenas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        comentario TEXT,
        calificacion INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
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
    # Usar columnas para centrar el contenido del perfil
    _, col_central, _ = st.columns([1, 4, 1])
    
    with col_central:
        st.markdown("<h1 style='text-align: center;'> Mi Perfil</h1>", unsafe_allow_html=True)
        
        conn = sqlite3.connect("tevi.db")
        c = conn.cursor()
        c.execute("SELECT facultad, carrera, edad, intereses, ubicacion, foto, sexo, preferencia, orientacion FROM usuarios WHERE id=?", (usuario_id,))
        datos = c.fetchone()
        conn.close()

        if not datos:
            st.error("Error al cargar datos.")
            return

        fac_val, car_val, edad_val, int_val, ubi_val, foto_actual, sexo_val, pref_val, orient_val = datos

        if "temp_ubicacion" not in st.session_state:
            st.session_state.temp_ubicacion = ubi_val or "No detectada"

        facultad = st.text_input("Facultad", value=fac_val or "")
        carrera = st.text_input("Carrera", value=car_val or "")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            edad = st.number_input("Edad", 16, 99, value=edad_val or 18)
            sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"], 
                                index=["Femenino", "Masculino", "Otro"].index(sexo_val) if sexo_val in ["Femenino", "Masculino", "Otro"] else 0)
        with c2:
            orientaciones = ["Heterosexual", "Homosexual", "Bisexual", "Pansexual", "Demisexual", "Asexual"]
            orientacion = st.selectbox("Orientación Sexual", orientaciones, 
                                      index=orientaciones.index(orient_val) if orient_val in orientaciones else 0)
        
        with c3:
            st.write(f"📍 **{st.session_state.temp_ubicacion}**")
            if st.button("🔄 Actualizar GPS"):
                st.session_state.temp_ubicacion = "Sede Principal UdeA"
                st.rerun()

        intereses = st.text_area("Sobre ti y tus Intereses", value=int_val or "", height=100)

        foto = st.file_uploader("Actualizar foto de perfil", type=["jpg","png"])
        if foto_actual and os.path.exists(foto_actual):
            st.image(foto_actual, width=150, caption="Foto actual")

        if st.button("Guardar perfil", type="primary", use_container_width=True):
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            nombre_foto = foto_actual
            if foto:
                file_path = os.path.join("uploads", f"{usuario_id}_{foto.name}")
                with open(file_path, "wb") as f: f.write(foto.getbuffer())
                nombre_foto = file_path
            c.execute("UPDATE usuarios SET facultad=?, carrera=?, edad=?, intereses=?, ubicacion=?, foto=?, sexo=?, orientacion=? WHERE id=?",
                      (facultad, carrera, edad, intereses, st.session_state.temp_ubicacion, nombre_foto, sexo, orientacion, usuario_id))
            conn.commit()
            conn.close()
            st.success("¡Perfil actualizado con éxito!")
            st.balloons()
            st.session_state["menu_actual"] = "Perfiles"
            st.rerun()

# ------------------ PERFILES / MATCH ------------------
def mostrar_celebracion(usuario_id, pid_match):
    """Pantalla especial de celebración cuando ocurre un Match"""
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    # Datos del usuario actual
    c.execute("SELECT foto, correo FROM usuarios WHERE id=?", (usuario_id,))
    yo = c.fetchone()
    # Datos del match
    c.execute("SELECT foto, correo, edad, carrera, facultad, intereses FROM usuarios WHERE id=?", (pid_match,))
    otro = c.fetchone()
    conn.close()

    st.balloons()
    
    with st.container(border=True):
        st.markdown("<h1 style='text-align: center; color: #FF4B4B; font-size: 3rem;'>❤️ ¡ES UN MATCH! ❤️</h1>", unsafe_allow_html=True)
        
        col1, col_fire, col2 = st.columns([2, 1, 2])
        
        with col1:
            foto_yo = yo[0] if (yo[0] and os.path.exists(yo[0])) else "https://placehold.co/300x300?text=Tú"
            st.image(foto_yo, use_container_width=True, caption="Tú")
        
        with col_fire:
            st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔥</h1>", unsafe_allow_html=True)
        
        with col2:
            foto_otro = otro[0] if (otro[0] and os.path.exists(otro[0])) else "https://placehold.co/300x300?text=Match"
            st.image(foto_otro, use_container_width=True, caption=otro[1].split('@')[0].capitalize())

        nombre_match = otro[1].split('@')[0].capitalize()
        st.markdown(f"""
            <div style='text-align: center; background-color: #1a1a1a; padding: 20px; border-radius: 15px; border: 1px solid #FF4B4B;'>
                <h2 style='color: white;'>¡A {nombre_match} también le gustas!</h2>
                <p style='font-size: 1.2rem;'>🎓 <b>{otro[3]}</b> en <b>{otro[4]}</b></p>
                <p style='font-size: 1.1rem; font-style: italic; color: #ccc;'>"{otro[5] or '¡Sin descripción aún!'}"</p>
                <hr style='border-color: #444;'>
                <h3 style='color: #FF4B4B;'>¡Ya pueden dar el paso de hablar por chat y conocerse!</h3>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button(" Ir al Chat ahora", type="primary", use_container_width=True):
            st.session_state.menu_actual = "Chat"
            st.session_state.match_celebration = None
            st.rerun()
        
        if st.button(" Seguir descubriendo personas", use_container_width=True):
            st.session_state.match_celebration = None
            st.rerun()

def ver_perfiles(usuario_id):
    # Si hay un match pendiente de celebrar, mostramos la pantalla de celebración
    if st.session_state.get("match_celebration"):
        mostrar_celebracion(usuario_id, st.session_state["match_celebration"])
        return

    st.title(" Quién me miró")
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    # 1. Obtener datos del usuario actual para filtrar
    c.execute("SELECT sexo, orientacion FROM usuarios WHERE id=?", (usuario_id,))
    user_data = c.fetchone()
    if not user_data: return
    mi_sexo, mi_orient = user_data

    # 2. Definir lógica de búsqueda compleja
    # Construimos la query base para excluir ya interactuados/bloqueados
    query_base = """
        SELECT id, facultad, carrera, intereses, edad, foto, correo, orientacion FROM usuarios 
        WHERE id != ? 
        AND id NOT IN (SELECT liked_id FROM likes WHERE usuario_id=?)
        AND id NOT IN (SELECT disliked_id FROM dislikes WHERE usuario_id=?)
        AND id NOT IN (SELECT bloqueado_id FROM bloqueos WHERE usuario_id=?)
        AND id NOT IN (SELECT usuario_id FROM bloqueos WHERE bloqueado_id=?)
    """
    params = [usuario_id, usuario_id, usuario_id, usuario_id, usuario_id]

    # 3. Aplicar filtros de orientación y género
    if mi_orient == "Heterosexual":
        query_base += " AND sexo != ? AND (orientacion = 'Heterosexual' OR orientacion IN ('Bisexual', 'Pansexual', 'Demisexual'))"
        params.append(mi_sexo)
    elif mi_orient == "Homosexual":
        query_base += " AND sexo = ? AND (orientacion = 'Homosexual' OR orientacion IN ('Bisexual', 'Pansexual', 'Demisexual'))"
        params.append(mi_sexo)
    elif mi_orient == "Asexual":
        query_base += " AND orientacion = 'Asexual'"
    else: # Bi, Pan, Demi: ven a todos los que sean compatibles con su género
        query_base += """ AND (
            (sexo != ? AND orientacion IN ('Heterosexual', 'Bisexual', 'Pansexual', 'Demisexual')) OR
            (sexo = ? AND orientacion IN ('Homosexual', 'Bisexual', 'Pansexual', 'Demisexual'))
        )"""
        params.extend([mi_sexo, mi_sexo])

    c.execute(query_base, params)
    perfiles = c.fetchall()
    conn.close()

    if not perfiles:
        st.info("No hay perfiles nuevos por ahora. ¡Vuelve pronto!")
        return

    # Mostrar perfiles en columnas (tarjetas)
    col1, col2, col3 = st.columns(3)
    
    for i, p in enumerate(perfiles):
        pid, p_facultad, p_carrera, p_intereses, p_edad, p_foto, p_correo, p_orient = p
        
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
                st.markdown(f"<span style='color: #FF4B4B;'>🌈 {p_orient}</span>", unsafe_allow_html=True)
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
                            conn.commit()
                            st.session_state["match_celebration"] = pid # Activamos la celebración
                        else:
                            conn.commit()
                            st.toast("Le avisamos que lo miraste ", icon="✅")
                        conn.close()
                        st.rerun()

# ------------------ CHAT ------------------
from chat import chat # Import the chat function directly
from reviews import resenas_page

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
    # --- LÓGICA DE DATOS PARA EL NAVBAR ---
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM likes WHERE liked_id=?", (st.session_state["usuario_id"],))
    num_likes = c.fetchone()[0]
    conn.close()
    
    # --- NAVEGACIÓN EN LA BARRA LATERAL (SIDEBAR) ---
    if "menu_actual" not in st.session_state:
        # Verificar si el perfil está completo para decidir la página de aterrizaje
        conn = sqlite3.connect("tevi.db")
        c = conn.cursor()
        c.execute("SELECT facultad FROM usuarios WHERE id=?", (st.session_state["usuario_id"],))
        res_perfil = c.fetchone()
        conn.close()

        # Si la facultad está vacía, es su primera vez o no ha terminado su perfil
        if res_perfil and not res_perfil[0]:
            st.session_state["menu_actual"] = "Perfil"
        else:
            st.session_state["menu_actual"] = "Perfiles" # "Perfiles" es la vista de Descubrir

    with st.sidebar:
        ruta = os.path.join("img", "logo_sinfondo.png")
        st.image(ruta)
        st.markdown(f"### ❤️ Likes: {num_likes}")
        st.markdown("---")

    
        
        if st.button(" Inicio", use_container_width=True):
            st.session_state.menu_actual = "Inicio"
        if st.button(" Mi Perfil", use_container_width=True):
            st.session_state.menu_actual = "Perfil"
        if st.button(" Descubrir", use_container_width=True):
            st.session_state.menu_actual = "Perfiles"
        if st.button(" Chat", use_container_width=True):
            st.session_state.menu_actual = "Chat"
        if st.button(" Premium", use_container_width=True):
            st.session_state.menu_actual = "Premium"
        if st.button(" ⭐ Reseñas", use_container_width=True):
            st.session_state.menu_actual = "Reseñas"
        
        st.markdown("---")
        if st.button(" Cerrar Sesión", use_container_width=True):
            st.session_state.confirmar_logout = True
        if st.button(" Eliminar Cuenta", use_container_width=True):
            st.session_state.confirmar_borrado = True

    # --- LÓGICA DE MODALES DE CONFIRMACIÓN ---
    
    if "confirmar_logout" not in st.session_state:
        st.session_state["confirmar_logout"] = False
    if "confirmar_borrado" not in st.session_state:
        st.session_state["confirmar_borrado"] = False

    if st.session_state["confirmar_logout"]:
        st.warning("¿Estás seguro de salir?")
        col_si, col_no = st.columns(2)
        if col_si.button("Sí"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if col_no.button("No"):
            st.session_state["confirmar_logout"] = False
            st.rerun()

    if st.session_state["confirmar_borrado"]:
        st.error("⚠️ ¿ELIMINAR CUENTA? Esto borrará tus matches y mensajes permanentemente.")
        col_si_b, col_no_b = st.columns(2)
        if col_si_b.button("Sí, borrar todo", key="del_acc_yes"):
            uid = st.session_state["usuario_id"]
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            # Limpieza profunda de datos
            c.execute("DELETE FROM mensajes WHERE match_id IN (SELECT id FROM matches WHERE usuario1_id=? OR usuario2_id=?)", (uid, uid))
            c.execute("DELETE FROM matches WHERE usuario1_id=? OR usuario2_id=?", (uid, uid))
            c.execute("DELETE FROM likes WHERE usuario_id=? OR liked_id=?", (uid, uid))
            c.execute("DELETE FROM dislikes WHERE usuario_id=? OR disliked_id=?", (uid, uid))
            c.execute("DELETE FROM pagos WHERE usuario_id=?", (uid,))
            c.execute("DELETE FROM usuarios WHERE id=?", (uid,))
            conn.commit()
            conn.close()
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
    elif st.session_state["menu_actual"] == "Reseñas":
        resenas_page(st.session_state["usuario_id"])
    else:
        st.title(" ¡Bienvenido a TeVi!")
        st.markdown("""
        ### ¿Has visto a alguien en la U y no sabes cómo hablarle?
        Todos hemos tenido ese **crush** que vemos a diario en la biblioteca, en la cafetería o cruzando el campus, pero a veces los nervios nos ganan y no sabemos cómo acercarnos. **TeVi** nace para que esos encuentros de pasillo se conviertan en algo más.
                    además tiene incorporado ladiversidad de genero y orientacion sexual asi identificas si le gustas a alguien y si tiene la orientacion sexual que  quieres

                    TeVi se creo con autenticidad y creatividad donde todos podemos ser felices y disfrutar de esta comunidad  sinlimites

                    recuerda que puedes bloquear y reportar si hay simbolo de acoso "es muy importante que pongas tus limites"

                    cualquier persona que intente usar esta app web conotras intenciones maliciosas se le sera bloqueado el acceso ala pagina
                    y no podria volver a registrar nunca mas el correo, sean respetuosos y concientes 

                

        Esta es la app de citas diseñada exclusivamente para nuestra comunidad universitaria. Aquí puedes encontrar a esa persona que te llama la atención, descubrir si tienen gustos en común y romper el hielo de forma segura y divertida.

        **¡El amor de tu vida podría estar sentado en el salón de al lado!** No dejes pasar la oportunidad de conectar con alguien especial de tu propia universidad.
        """)
        st.image("https://images.unsplash.com/photo-1543269865-cbf427effbad?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", caption="Tu historia de amor comienza en el campus")
