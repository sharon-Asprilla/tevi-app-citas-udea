import sqlite3

def init_db():
    conn = sqlite3.connect("tevi.db")
    c = conn.cursor()

    # Tabla de usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correo TEXT UNIQUE,
        contraseña TEXT,
        facultad TEXT,
        carrera TEXT,
        edad INTEGER,
        intereses TEXT,
        foto TEXT,
        ubicacion TEXT,
        premium INTEGER DEFAULT 0,
        sexo TEXT,
        preferencia TEXT
    )
    """)

    # Tabla de likes
    c.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        liked_id INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(liked_id) REFERENCES usuarios(id)
    )
    """)

    # Tabla de matches
    c.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario1_id INTEGER,
        usuario2_id INTEGER,
        FOREIGN KEY(usuario1_id) REFERENCES usuarios(id),
        FOREIGN KEY(usuario2_id) REFERENCES usuarios(id)
    )
    """)

    # Tabla de mensajes
    c.execute("""
    CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        remitente_id INTEGER,
        mensaje TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(match_id) REFERENCES matches(id),
        FOREIGN KEY(remitente_id) REFERENCES usuarios(id)
    )
    """)

    # Tabla de pagos
    c.execute("""
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        monto INTEGER,
        fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()
