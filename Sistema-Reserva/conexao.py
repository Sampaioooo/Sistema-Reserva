import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="usuario_lab",      
        password="senha123",     
        database="reserva_laboratorio"
    )
