import streamlit as st
import sqlite3
import bcrypt
from email_validator import validate_email, EmailNotValidError

def login():
    st.title("🔐 TeVi 👀 - Login")
    correo = st.text_input("Correo institucional")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        conn = sqlite3.connect("tevi.db")
        c = conn.cursor()
        c.execute("SELECT id, contraseña FROM usuarios WHERE correo=?", (correo,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.checkpw(contraseña.encode(), user[1].encode()):
            st.session_state["usuario_id"] = user[0]
            st.rerun()
        else:
            st.error("Credenciales inválidas ❌")

def registro():
    st.title("📝 Registro")
    correo = st.text_input("Correo institucional")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Registrar"):
        try:
            v = validate_email(correo)
            dominio = correo.split("@")[1]
            if not dominio.endswith(".edu.co"):
                st.error("Solo correos institucionales permitidos ❌")
                return
        except EmailNotValidError:
            st.error("Correo inválido ❌")
            return

        hashed = bcrypt.hashpw(contraseña.encode(), bcrypt.gensalt()).decode()

        conn = sqlite3.connect("tevi.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (correo, contraseña) VALUES (?,?)", (correo, hashed))
            conn.commit()
            st.success("Usuario registrado ✅")
        except:
            st.error("El correo ya existe ❌")
        conn.close()
