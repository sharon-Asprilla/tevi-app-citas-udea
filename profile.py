import streamlit as st
import sqlite3

def perfil(usuario_id):
    st.title("👤 Mi Perfil")
    facultad = st.text_input("Facultad")
    carrera = st.text_input("Carrera")
    edad = st.number_input("Edad", 16, 99)
    intereses = st.text_area("Intereses")
    ubicacion = st.text_input("Ubicación (simulada)")
    foto = st.file_uploader("Subir foto", type=["jpg","png"])

    if st.button("Guardar perfil"):
        conn = sqlite3.connect("tevi.db")
        c = conn.cursor()
        c.execute("""UPDATE usuarios SET facultad=?, carrera=?, edad=?, intereses=?, ubicacion=?, foto=? WHERE id=?""",
                  (facultad, carrera, edad, intereses, ubicacion, foto.name if foto else None, usuario_id))
        conn.commit()
        conn.close()
        st.session_state["menu_actual"] = "Perfiles"
        st.rerun()
