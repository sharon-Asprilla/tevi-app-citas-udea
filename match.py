import streamlit as st
import sqlite3

def ver_perfiles(usuario_id):
    st.title("👀 Quién me miró")
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    # Obtener preferencia del usuario actual
    c.execute("SELECT preferencia FROM usuarios WHERE id=?", (usuario_id,))
    res = c.fetchone()
    pref = res[0] if res else "Hombres"
    
    # Mapear preferencia al sexo buscado en la DB
    sexo_buscado = "Masculino" if pref == "Hombres" else "Femenino"

    # Filtrar perfiles por sexo y excluir a los que ya se les dio like/dislike
    c.execute("""SELECT id, facultad FROM usuarios 
                 WHERE id != ? 
                 AND sexo = ?
                 AND id NOT IN (SELECT liked_id FROM likes WHERE usuario_id = ?)
                 AND id NOT IN (SELECT disliked_id FROM dislikes WHERE usuario_id = ?)""", 
              (usuario_id, sexo_buscado, usuario_id, usuario_id))
    
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
