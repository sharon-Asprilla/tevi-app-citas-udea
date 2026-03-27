import streamlit as st
import sqlite3
import bcrypt
from email_validator import validate_email, EmailNotValidError

def login():
    # Columnas para centrado: [Espacio, Contenido, Espacio]
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.markdown("<h1 style='text-align: center;'> Iniciar Sesión</h1>", unsafe_allow_html=True)
        correo = st.text_input("Correo institucional", placeholder="usuario@udea.edu.co")
        contraseña = st.text_input("Contraseña", type="password", placeholder="••••••••")

        if st.button("Entrar ahora", key="login_btn_main"):
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            c.execute("SELECT id, contraseña FROM usuarios WHERE correo=?", (correo,))
            user = c.fetchone()
            conn.close()

            if user and bcrypt.checkpw(contraseña.encode(), user[1].encode()):
                st.session_state["usuario_id"] = user[0]
                st.rerun()
            else:
                st.error("Credenciales inválidas ")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Botones de navegación abajo
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Crear cuenta", key="goto_reg"):
                st.session_state.auth_mode = "Registro"
                st.rerun()
        with c2:
            if st.button("¿Olvidaste tu contraseña?", key="goto_forgot"):
                st.session_state.auth_mode = "Forgot_Password"
                st.rerun()

def registro():
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        st.markdown("<h1 style='text-align: center;'>te vi</h1>"
        "<br> recuerda registrarte con tu correo institucional y si tienes cuenta iniciar sesión</h4><br><br>", unsafe_allow_html=True)
        correo = st.text_input("Correo institucional", placeholder="tucorreo@udea.edu.co")
        contraseña = st.text_input("Crea una contraseña", type="password")

        if st.button("Registrarme", key="registro_btn_main"):
            try:
                validate_email(correo)
                dominio = correo.split("@")[1]
                if not dominio.endswith("udea.edu.co"):
                    st.error("Solo correos udea.edu.co ")
                    return
            except EmailNotValidError:
                st.error("Correo inválido ")
                return

            hashed = bcrypt.hashpw(contraseña.encode(), bcrypt.gensalt()).decode()
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO usuarios (correo, contraseña) VALUES (?,?)", (correo, hashed))
                conn.commit()
                st.success("¡Registro exitoso!")
                st.session_state.auth_mode = "Login"
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Este correo ya está registrado.")
            conn.close()

        st.markdown("---")
        if st.button("¿Ya tienes cuenta? Inicia Sesión"):
            st.session_state.auth_mode = "Login"
            st.rerun()

def forgot_password():
    _, center_col, _ = st.columns([1, 2, 1])

    with center_col:
        st.markdown("<h1 style='text-align: center;'> Recuperar contraseña</h1>", unsafe_allow_html=True)
        correo = st.text_input("Correo institucional")
        nueva_contraseña = st.text_input("Nueva Contraseña", type="password")
        confirmar = st.text_input("Confirmar Contraseña", type="password")

        if st.button("Cambiar contraseña"):
            if nueva_contraseña != confirmar:
                st.error("Las contraseñas no coinciden")
                return
            
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            c.execute("SELECT id FROM usuarios WHERE correo=?", (correo,))
            if c.fetchone():
                hashed = bcrypt.hashpw(nueva_contraseña.encode(), bcrypt.gensalt()).decode()
                c.execute("UPDATE usuarios SET contraseña=? WHERE correo=?", (hashed, correo))
                conn.commit()
                st.success("¡Listo! Ya puedes entrar.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Correo no encontrado")
            conn.close()

        st.markdown("---")
        if st.button("Volver al inicio"):
            st.session_state.auth_mode = "Login"
            st.rerun()
