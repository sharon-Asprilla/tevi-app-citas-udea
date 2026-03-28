import streamlit as st
import sqlite3

def perfil(usuario_id):
    
    st.title(" Mi Perfil")
   
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    c.execute("SELECT facultad, carrera, edad, intereses, sexo, preferencia, ubicacion FROM usuarios WHERE id=?", (usuario_id,))
    datos = c.fetchone()
    conn.close()

    facultad = st.text_input("Facultad", value=datos[0] if datos and datos[0] else "")
    carrera = st.text_input("Carrera", value=datos[1] if datos and datos[1] else "")
    edad = st.number_input("Edad", 16, 99, value=datos[2] if datos and datos[2] else 18)
    intereses = st.text_area("Intereses", value=datos[3] if datos and datos[3] else "")
    
    sexo_val = datos[4] if datos and datos[4] else "Femenino"
    pref_val = datos[5] if datos and datos[5] else "Hombres"
    
    sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"], index=["Femenino", "Masculino", "Otro"].index(sexo_val) if sexo_val in ["Femenino", "Masculino", "Otro"] else 0)
    preferencia = st.selectbox("Preferencia sexual", ["Hombres", "Mujeres"], index=["Hombres", "Mujeres"].index(pref_val) if pref_val in ["Hombres", "Mujeres"] else 0)
    
    ubicacion = st.text_input("Ubicación (simulada)", value=datos[6] if datos and datos[6] else "")
    foto = st.file_uploader("Subir foto", type=["jpg","png"])

    if st.button("Guardar perfil"):
        conn = sqlite3.connect("tevi.db")
        c = conn.cursor()
        c.execute("""UPDATE usuarios SET facultad=?, carrera=?, edad=?, intereses=?, ubicacion=?, foto=?, sexo=?, preferencia=? WHERE id=?""",
                  (facultad, carrera, edad, intereses, ubicacion, foto.name if foto else None, sexo, preferencia, usuario_id))
        conn.commit()
        conn.close()
        st.session_state["menu_actual"] = "Perfiles"
        st.rerun()
