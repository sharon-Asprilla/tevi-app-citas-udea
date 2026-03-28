import streamlit as st
import sqlite3
import os
from datetime import datetime

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
        WHERE m.usuario1_id=? OR m.usuario2_id=?
    """
    c.execute(query, (usuario_id, usuario_id))
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
        m_id = st.session_state.chat_activo
        # Obtener datos del match seleccionado
        match_sel = next(m for m in matches if m[0] == m_id)
        m_id, u1_c, u2_c, u1_id, u2_id, u1_f, u2_f, _, _, last_remitente = match_sel
        
        es_u1 = (u1_id == usuario_id)
        nombre_otro = (u2_c if es_u1 else u1_c).split('@')[0].capitalize()
        foto_otro = u2_f if es_u1 else u1_f
        foto_mia = u1_f if es_u1 else u2_f
        
        avatar_otro = foto_otro if (foto_otro and os.path.exists(foto_otro)) else None
        avatar_mio = foto_mia if (foto_mia and os.path.exists(foto_mia)) else None

        # Cabecera con botón volver
        h_col1, h_col2 = st.columns([1, 6])
        with h_col1:
            if st.button("⬅️", key="back_top"):
                st.session_state.chat_activo = None
                st.rerun()
        with h_col2:
            st.markdown(f"### Chat con {nombre_otro}")

        # Indicador de turno
        if last_remitente and last_remitente != usuario_id:
            st.warning("🔔 **¡Te toca responder!** No dejes en visto a " + nombre_otro)

        # Área de mensajes
        # Fetch full timestamp for date separation
        c.execute("SELECT remitente_id, mensaje, timestamp FROM mensajes WHERE match_id=? ORDER BY timestamp ASC", (m_id,))
        messages_data = c.fetchall()

        last_displayed_date = None
        month_names_es = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        for r_id, texto, full_timestamp in messages_data:
            message_datetime = datetime.strptime(full_timestamp, "%Y-%m-%d %H:%M:%S")
            message_date = message_datetime.date()
            message_time = message_datetime.strftime("%H:%M")

            if message_date != last_displayed_date:
                formatted_date = f"<div style='text-align: center; color: gray; margin: 15px 0; font-size: 0.9em;'>--- {message_date.day} de {month_names_es[message_date.month]} de {message_date.year} ---</div>"
                st.markdown(formatted_date, unsafe_allow_html=True)
                last_displayed_date = message_date

            soy_yo = (r_id == usuario_id)
            with st.chat_message("user" if soy_yo else "assistant", avatar=avatar_mio if soy_yo else avatar_otro):
                st.write(texto)
                st.caption(message_time) # Display only time here
        
        # Barra de utilidades inferior (Botón volver y Emoji)
        # Se coloca antes del input para que aparezca justo encima de la caja de texto
        st.write("---")
        col_back, col_emo, _ = st.columns([1, 1, 8])
        with col_back:
            if st.button("⬅️", key="back_bottom", help="Volver a la lista de chats"):
                st.session_state.chat_activo = None
                st.rerun()
        with col_emo:
            if st.button("😊"):
                st.toast("Usa el teclado de tu celular para emojis 📱")

        # Input estilo Messenger (Streamlit chat_input ya tiene el avión de papel ✈️)
        nuevo_msg = st.chat_input(f"Escribe un mensaje a {nombre_otro}...")

        if nuevo_msg:
            c.execute("INSERT INTO mensajes (match_id, remitente_id, mensaje) VALUES (?,?,?)", (m_id, usuario_id, nuevo_msg))
            conn.commit()
            st.rerun()

    conn.close()
