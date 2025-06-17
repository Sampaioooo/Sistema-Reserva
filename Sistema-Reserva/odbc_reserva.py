import pyodbc

def conectar_odbc():
    return pyodbc.connect(
        "DSN=ReservaLabODBC;"
    )

def criar_reserva_odbc(id_usuario, id_sala, data, inicio, fim):
    conn = conectar_odbc()
    cursor = conn.cursor()
    sql = """
        INSERT INTO reservas (id_usuario, id_sala, data_reserva, hora_inicio, hora_fim)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (id_usuario, id_sala, data, inicio, fim))
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Reserva via ODBC cadastrada com sucesso!")

criar_reserva_odbc(2, 2, "2025-06-18", "14:00:00", "16:00:00")
