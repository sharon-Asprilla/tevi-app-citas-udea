import streamlit as st
import sqlite3

def chat(usuario_id):
    st.title("💬 Chat")
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    c.execute("""SELECT m.id, u1.correo, u2.correo FROM matches m
                 JOIN usuarios u1 ON m.usuario1_id=u1.id
                 JOIN usuarios u2 ON m.usuario2_id=u2.id
                 WHERE usuario1_id=? OR usuario2_id=?""", (usuario_id, usuario_id))
    matches = c.fetchall()

    for m in matches:
        st.subheader(f"Chat con {m[1] if m[1]!=usuario_id else m[2]}")
        mensaje = st.text_input("Escribe un mensaje", key=m[0])
        if st.button("Enviar", key=f"send{m[0]}"):
            c.execute("INSERT INTO mensajes (match_id, remitente_id, mensaje) VALUES (?,?,?)", (m[0], usuario_id, mensaje))
            conn.commit()
        c.execute("SELECT remitente_id, mensaje FROM mensajes WHERE match_id=?", (m[0],))
        msgs = c.fetchall()
        for msg in msgs:
            st.write(f"{msg[0]}: {msg[1]}")
    conn.close()
