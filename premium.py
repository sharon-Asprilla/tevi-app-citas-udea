import streamlit as st
import sqlite3

def premium(usuario_id):
    st.title("💰 Premium")
    monto = st.number_input("Valor a pagar (COP)", min_value=0)
    if st.button("Pagar"):
        if monto >= 10000:
            conn = sqlite3.connect("tevi.db")
            c = conn.cursor()
            c.execute("UPDATE usuarios SET premium=1 WHERE id=?", (usuario_id,))
            c.execute("INSERT INTO pagos (usuario_id, monto) VALUES (?,?)", (usuario_id, monto))
            conn.commit()
            conn.close()
            st.success("Ahora eres Premium ")
        else:
            st.error("El mínimo es 10.000 COP ")
