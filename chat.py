import streamlit as st
import sqlite3
import os
from datetime import datetime
from chat_whatsapp import chat_whatsapp

def chat(usuario_id):
    
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()
    
    # Obtener matches con el último mensaje y su hora
    query = """
        SELECT m.id, u1.correo, u2.correo, u1.id, u2.id, u1.foto, u2.foto,
        (SELECT mensaje FROM mensajes WHERE match_id = m.id ORDER BY timestamp DESC LIMIT 1) as ultimo_msg,
        (SELECT strftime('%H:%M', timestamp) FROM mensajes WHERE match_id = m.id ORDER BY timestamp DESC LIMIT 1) as hora,
        (SELECT remitente_id FROM mensajes WHERE match_id = m.id ORDER BY timestamp DESC LIMIT 1) as ultimo_remitente
        FROM matches m
        JOIN usuarios u1 ON m.usuario1_id=u1.id
        JOIN usuarios u2 ON m.usuario2_id=u2.id
        WHERE (m.usuario1_id=? OR m.usuario2_id=?)
        AND u1.id NOT IN (SELECT bloqueado_id FROM bloqueos WHERE usuario_id=?)
        AND u2.id NOT IN (SELECT bloqueado_id FROM bloqueos WHERE usuario_id=?)
        AND u1.id NOT IN (SELECT usuario_id FROM bloqueos WHERE bloqueado_id=?)
        AND u2.id NOT IN (SELECT usuario_id FROM bloqueos WHERE bloqueado_id=?)
    """
    c.execute(query, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, usuario_id))
    matches = c.fetchall()

    if not matches:
        st.info("📭 Tu bandeja está vacía. ¡Haz match con alguien!")
        conn.close()
        return

    # Usar session_state para manejar si estamos viendo la lista o un chat específico
    if "chat_activo" not in st.session_state:
        st.session_state.chat_activo = None

    if st.session_state.chat_activo is None:
        st.subheader("Mensajes Recientes")
        for m in matches:
            m_id, u1_c, u2_c, u1_id, u2_id, u1_f, u2_f, last_msg, hora, last_remitente = m
            
            # Determinar datos del otro
            es_u1 = (u1_id == usuario_id)
            nombre_otro = (u2_c if es_u1 else u1_c).split('@')[0].capitalize()
            foto_otro = u2_f if es_u1 else u1_f
            avatar_path = foto_otro if (foto_otro and os.path.exists(foto_otro)) else "https://placehold.co/50x50?text=?"
            
            # Indicador de turno en la lista
            turno_str = "🔴 ¡Te toca!" if last_remitente and last_remitente != usuario_id else ""

            # Diseño de la fila de chat
            with st.container():
                col_img, col_txt, col_btn = st.columns([1, 4, 1])
                with col_img:
                    st.image(avatar_path, width=50)
                with col_txt:
                    st.markdown(f"**{nombre_otro}** <span style='color:gray; font-size:12px;'>{hora or ''}</span>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin:0; font-size:14px; color:#bbb;'>{last_msg or '¡Di hola!'} {turno_str}</p>", unsafe_allow_html=True)
                with col_btn:
                    if st.button("Abrir", key=f"btn_{m_id}"):
                        st.session_state.chat_activo = m_id
                        st.rerun()
                st.markdown("---")
    else:
        # VISTA DEL CHAT ABIERTO
        chat_whatsapp(usuario_id, st.session_state.chat_activo)
        
    conn.close()
