from conexao import conectar

def criar_reserva(id_usuario, id_sala, data, inicio, fim):
    conexao = conectar()
    cursor = conexao.cursor()
    sql = """
    INSERT INTO reservas (id_usuario, id_sala, data_reserva, hora_inicio, hora_fim)
    VALUES (%s, %s, %s, %s, %s)
    """
    valores = (id_usuario, id_sala, data, inicio, fim)
    cursor.execute(sql, valores)
    conexao.commit()
    cursor.close()
    conexao.close()
    print("✅ Reserva cadastrada com sucesso!")


criar_reserva(1, 1, "2025-06-17", "10:00:00", "12:00:00")
