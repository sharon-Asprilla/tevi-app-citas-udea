import streamlit as st
import sqlite3
from datetime import datetime

def resenas_page(usuario_id):
    """
    Página de Reseñas y Calificaciones para TeVi.
    Permite a los usuarios dejar feedback y ver el de otros.
    """
    st.markdown("<h1 style='text-align: center;'>⭐ Reseñas y Calificaciones</h1>", unsafe_allow_html=True)
    
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    # 1. Formulario para nueva reseña
    with st.container(border=True):
        st.subheader("¡Cuéntanos tu experiencia!")
        with st.form("nueva_resena", clear_on_submit=True):
            col_stars, col_empty = st.columns([2, 1])
            with col_stars:
                calificacion = st.select_slider(
                    "Califica la app (1: Mala - 5: ¡Excelente!)", 
                    options=[1, 2, 3, 4, 5], 
                    value=5
                )
            
            comentario = st.text_area("Escribe tu opinión...", placeholder="¿Qué es lo que más te gusta de TeVi o qué deberíamos mejorar?")
            
            submit = st.form_submit_button("Publicar reseña", use_container_width=True)
            
            if submit:
                if comentario.strip() == "":
                    st.error("Por favor, escribe un comentario antes de enviar.")
                else:
                    c.execute("INSERT INTO resenas (usuario_id, comentario, calificacion) VALUES (?, ?, ?)",
                              (usuario_id, comentario, calificacion))
                    conn.commit()
                    st.success("¡Gracias por tu reseña! Tu opinión nos ayuda a crecer. ❤️")
                    st.rerun()

    st.markdown("---")

    # 2. Listado de reseñas con opciones de ordenamiento
    col_title, col_sort = st.columns([2, 1])
    with col_title:
        st.subheader("Opiniones de la comunidad")
    with col_sort:
        orden = st.selectbox("Ordenar por:", ["Más recientes", "Mejor puntuación", "Menor puntuación"])

    # Mapeo de lógica de ordenamiento
    order_map = {
        "Más recientes": "r.timestamp DESC",
        "Mejor puntuación": "r.calificacion DESC, r.timestamp DESC",
        "Menor puntuación": "r.calificacion ASC, r.timestamp DESC"
    }

    c.execute(f"""
        SELECT u.correo, r.comentario, r.calificacion, r.timestamp 
        FROM resenas r 
        JOIN usuarios u ON r.usuario_id = u.id 
        ORDER BY {order_map[orden]}
    """)
    resenas = c.fetchall()

    if not resenas:
        st.info("Aún no hay reseñas. ¡Sé el primero en calificar la app!")
    else:
        for correo, texto, nota, fecha in resenas:
            nombre = correo.split('@')[0].capitalize()
            estrellas = "⭐" * nota
            # Formatear fecha de SQLite a algo legible
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            
            with st.container(border=True):
                st.markdown(f"**{nombre}** <span style='color:gray; font-size: 0.8rem;'>• {fecha_dt}</span>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='margin-top:0; color:#FF4B4B;'>{estrellas}</h3>", unsafe_allow_html=True)
                st.write(texto)

    conn.close()