import streamlit as st
import sqlite3

def ver_perfiles(usuario_id):
    st.title("👀 Quién me miró")
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    c.execute("SELECT id, facultad FROM usuarios WHERE id!=?", (usuario_id,))
    perfiles = c.fetchall()
    conn.close()

    for p in perfiles:
        st.write(f"Alguien de {p[1]}")
        if st.button("Me miró", key=p[0]):
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            c.execute("INSERT INTO likes (usuario_id, liked_id) VALUES (?,?)", (usuario_id, p[0]))
            conn.commit()
            conn.close()
            st.success("Like enviado ✅")
