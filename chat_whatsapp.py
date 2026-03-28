import streamlit as st
from audio_recorder_streamlit import audio_recorder
from datetime import datetime
import sqlite3
import os

def chat_whatsapp(usuario_id, match_id):
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    # 0. Obtener información de ambos usuarios para las burbujas
    # Info del Usuario Actual (Tú)
    c.execute("SELECT correo, foto FROM usuarios WHERE id=?", (usuario_id,))
    yo = c.fetchone()
    nombre_yo = "Tú"
    foto_yo = yo[1] if yo and yo[1] and os.path.exists(yo[1]) else "https://placehold.co/100x100?text=Yo"

    # Info del Contacto (Match)
    c.execute("""
        SELECT u.correo, u.foto FROM usuarios u
        JOIN matches m ON (u.id = m.usuario1_id OR u.id = m.usuario2_id)
        WHERE m.id = ? AND u.id != ?
    """, (match_id, usuario_id))
    contacto = c.fetchone()
    nombre_match = contacto[0].split('@')[0].capitalize() if contacto else "Usuario"
    foto_match = contacto[1] if contacto and contacto[1] and os.path.exists(contacto[1]) else "https://placehold.co/100x100?text=Match"

    def guardar_mensaje(contenido, tipo='text'):
        c.execute("INSERT INTO mensajes (match_id, remitente_id, mensaje, tipo) VALUES (?,?,?,?)",
                  (match_id, usuario_id, contenido, tipo))
        conn.commit()

    # 1. Estilos CSS Personalizados usando la paleta de TeVi
    st.markdown("""
    <style>
        /* Encabezado del Chat */
        .chat-header {
            background-color: #111111;
            color: #FF4B4B;
            border-bottom: 2px solid #E63946;
            padding: 10px 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        /* Personalización de Burbujas para que parezcan WhatsApp */
        [data-testid="stChatMessage"] {
            border-radius: 15px !important;
            padding: 5px 15px !important;
            margin-bottom: 10px !important;
        }

        /* Mensajes Recibidos (Gris oscuro del proyecto) */
        [data-testid="stChatMessageAssistant"] {
            background-color: #2D2D2D !important;
            border: 1px solid #444 !important;
            margin-right: 20% !important;
        }

        /* Mensajes Enviados (Rojo TeVi) */
        [data-testid="stChatMessageUser"] {
            background-color: #E63946 !important;
            margin-left: 20% !important;
        }

        /* Etiquetas internas del mensaje */
        .msg-label {
            font-size: 0.7rem;
            font-weight: bold;
            margin-bottom: 2px;
            display: block;
            opacity: 0.9;
        }
        
        .msg-time {
            font-size: 0.6rem;
            text-align: right;
            display: block;
            margin-top: 4px;
            opacity: 0.7;
        }

    </style>
    """, unsafe_allow_html=True)

    # 2. Encabezado Fijo con Botón de Volver
    with st.container():
        col_back, col_info = st.columns([1, 9])
        with col_back:
            if st.button("⬅️", key="back_to_list"):
                st.session_state.chat_activo = None
                st.rerun()
        with col_info:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{foto_match}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">
                    <div>
                        <b style="color: #FF4B4B; font-size: 1rem;">{nombre_match}</b><br>
                        <small style="color: #888;">En línea</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("<div class='header-spacer'></div>", unsafe_allow_html=True)

    # 3. Gestión de historial con session_state para rapidez
    c.execute("SELECT id, remitente_id, mensaje, tipo, strftime('%H:%M', timestamp) FROM mensajes WHERE match_id=? ORDER BY timestamp ASC", (match_id,))
    st.session_state[f"history_{match_id}"] = c.fetchall()

    # 4. Mostrar Mensajes con diseño de burbuja
    for m_id, r_id, contenido, tipo, hora in st.session_state[f"history_{match_id}"]:
        es_mio = (r_id == usuario_id)
        role = "user" if es_mio else "assistant"
        avatar = foto_yo if es_mio else foto_match
        nombre_remitente = nombre_yo if es_mio else nombre_match
        
        with st.chat_message(role, avatar=avatar):
            st.markdown(f"<span class='msg-label'>{nombre_remitente}</span>", unsafe_allow_html=True)
            if tipo == "text":
                st.write(contenido)
            elif tipo == "image":
                st.image(contenido, use_container_width=True)
            elif tipo == "audio":
                st.audio(contenido)
            
            # Botón para borrar (solo para mis propios mensajes)
            if es_mio:
                col_del, _ = st.columns([1, 5])
                if col_del.button("🗑️", key=f"del_{m_id}", help="Eliminar mensaje para todos"):
                    # Si es una foto o audio, borramos el archivo del servidor
                    if tipo in ["image", "audio"] and os.path.exists(contenido):
                        try: os.remove(contenido)
                        except: pass
                    
                    c.execute("DELETE FROM mensajes WHERE id=?", (m_id,))
                    conn.commit()
                    st.rerun()

            st.markdown(f"<span class='msg-time'>{hora} {'✔️✔️' if es_mio else ''}</span>", unsafe_allow_html=True)

    # 5. Acciones de Multimedia y Seguridad (Ahora integradas al final del chat)
    st.markdown("---")
    col_back, col_img, col_audio, col_sec = st.columns([1, 1, 1, 1])
    
    with col_back:
        if st.button("⬅️", key="back_bottom", help="Volver a la lista", use_container_width=True):
            st.session_state.chat_activo = None
            st.rerun()

    with col_img:
        with st.popover("📷 Foto"):
            foto = st.file_uploader("Enviar imagen", type=["png", "jpg", "jpeg"], key="chat_img")
            if foto and st.button("📤 Enviar", use_container_width=True):
                path = os.path.join("uploads", f"chat_{datetime.now().timestamp()}.png")
                with open(path, "wb") as f: f.write(foto.getbuffer())
                guardar_mensaje(path, 'image')
                st.rerun()

    with col_audio:
        with st.popover("🎤 Audio"):
            audio_bytes = audio_recorder(
                text="Toca para grabar",
                recording_color="#E63946",
                neutral_color="#FF4B4B",
                icon_size="2x"
            )
            if audio_bytes:
                if st.button("🚀 Enviar Audio", use_container_width=True):
                    path = os.path.join("uploads", f"chat_{datetime.now().timestamp()}.wav")
                    with open(path, "wb") as f: f.write(audio_bytes)
                    guardar_mensaje(path, 'audio')
                    st.rerun()

    with col_sec:
        with st.popover("Seguridad"):
            motivo = st.selectbox("Reportar por:", ["Spam", "Acoso", "Perfil Falso", "Otro"])
            if st.button("🚩 Reportar", use_container_width=True):
                c.execute("SELECT u.id FROM usuarios u JOIN matches m ON (u.id = m.usuario1_id OR u.id = m.usuario2_id) WHERE m.id = ? AND u.id != ?", (match_id, usuario_id))
                otro_id = c.fetchone()[0]
                c.execute("INSERT INTO reportes (usuario_id, reportado_id, motivo) VALUES (?,?,?)", (usuario_id, otro_id, motivo))
                conn.commit()
                st.toast("Reporte enviado")
            if st.button("🚫 Bloquear", use_container_width=True):
                c.execute("SELECT u.id FROM usuarios u JOIN matches m ON (u.id = m.usuario1_id OR u.id = m.usuario2_id) WHERE m.id = ? AND u.id != ?", (match_id, usuario_id))
                otro_id = c.fetchone()[0]
                c.execute("INSERT INTO bloqueos (usuario_id, bloqueado_id) VALUES (?,?)", (usuario_id, otro_id))
                conn.commit()
                st.session_state.chat_activo = None
                st.rerun()

    # 6. Entrada de texto principal
    prompt = st.chat_input(f"Escribe un mensaje para {nombre_match}...")
    if prompt:
        guardar_mensaje(prompt, 'text')
        st.rerun()

    conn.close()