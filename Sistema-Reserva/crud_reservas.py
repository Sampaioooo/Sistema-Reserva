import mysql.connector  
import bcrypt
from datetime import timedelta
import os
import time

conexao = mysql.connector.connect(
    host="localhost",
    user="usuario_lab",
    password="senha123",
    database="reserva_laboratorio"
)
cursor = conexao.cursor(dictionary=True)
usuario_logado = None

def backup_banco_dados():
    print("\n💾 Iniciando backup do banco de dados...")
    nome_arquivo = f"backup_{time.strftime('%Y%m%d_%H%M%S')}.sql"
    comando = f"mysqldump -u usuario_lab -psenha123 reserva_laboratorio > {nome_arquivo}"
    resultado = os.system(comando)
    if resultado == 0:
        print(f"✅ Backup realizado com sucesso: {nome_arquivo}")
    else:
        print("❌ Erro ao realizar backup.")

def cadastrar_usuario():
    print("\n--- Cadastro de novo usuário ---")
    nome = input("Nome: ").strip()
    if nome == '0': return
    email = input("Email: ").strip()
    if email == '0': return
    senha = input("Senha: ").strip()
    if senha == '0': return
    tipo = input("Tipo de usuário (admin/professor/aluno): ").strip().lower()
    if tipo == '0': return

    if tipo not in ['admin', 'professor', 'aluno']:
        print("❌ Tipo inválido. Digite 'admin', 'professor' ou 'aluno'.")
        return

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    if cursor.fetchone():
        print("❗ E-mail já cadastrado.")
        return

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (%s, %s, %s, %s)
        """, (nome, email, senha_hash, tipo))
        conexao.commit()
        print(f"✅ Usuário {nome} cadastrado com sucesso como {tipo}!")
    except mysql.connector.Error as err:
        print(f"❌ Erro ao cadastrar: {err}")

def login():
    global usuario_logado
    print("\n🔐 Login de Usuário")
    email = input("Email: ").strip()
    if email == '0': return
    senha = input("Senha: ").strip()
    if senha == '0': return

    cursor.execute("SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = %s", (email,))
    resultado = cursor.fetchone()

    if resultado:
        senha_hash = resultado['senha']
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            print(f"✅ Login bem-sucedido. Bem-vindo, {resultado['nome']}!")
            usuario_logado = {
                'id': resultado['id'],
                'nome': resultado['nome'],
                'email': resultado['email'],
                'tipo': resultado['tipo']
            }
            menu()
        else:
            print("❌ Email ou senha inválidos.")
    else:
        print("❌ Email ou senha inválidos.")

def formatar_tempo(t):
    if isinstance(t, timedelta):
        segundos = int(t.total_seconds())
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"
    return str(t)

def menu_inicial():
    while True:
        print("\n--- SISTEMA DE RESERVAS ---")
        print("1. Login")
        print("2. Cadastrar novo usuário")
        print("3. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            login()
        elif opcao == '2':
            cadastrar_usuario()
        elif opcao == '3':
            confirm = input("Tem certeza que deseja sair? (s/n): ").strip().lower()
            if confirm == 's':
                print("👋 Saindo do sistema.")
                break
        else:
            print("❗ Opção inválida.")

def listar_reservas():
    print("\n📋 Reservas cadastradas (0 para voltar)")
    cursor.execute("""
        SELECT reservas.id, reservas.id_usuario, usuarios.nome AS nome_usuario, salas.nome_sala, data_reserva, hora_inicio, hora_fim, status
        FROM reservas
        JOIN usuarios ON reservas.id_usuario = usuarios.id
        JOIN salas ON reservas.id_sala = salas.id
    """)
    resultados = cursor.fetchall()
    if not resultados:
        print("Nenhuma reserva cadastrada.")
    else:
        for r in resultados:
            print(f"ID: {r['id']} | Usuário: {r['nome_usuario']} | Sala: {r['nome_sala']} | Data: {r['data_reserva']} | Início: {formatar_tempo(r['hora_inicio'])} | Fim: {formatar_tempo(r['hora_fim'])} | Status: {r['status']}")
    input("Pressione ENTER para voltar.")

def listar_suas_reservas():
    print("\n📋 Suas Reservas (0 para voltar)")
    cursor.execute("""
        SELECT reservas.id, salas.nome_sala, data_reserva, hora_inicio, hora_fim, status
        FROM reservas
        JOIN salas ON reservas.id_sala = salas.id
        WHERE reservas.id_usuario = %s
    """, (usuario_logado['id'],))
    resultados = cursor.fetchall()
    if not resultados:
        print("Você não possui reservas.")
    else:
        for r in resultados:
            print(f"ID: {r['id']} | Sala: {r['nome_sala']} | Data: {r['data_reserva']} | Início: {formatar_tempo(r['hora_inicio'])} | Fim: {formatar_tempo(r['hora_fim'])} | Status: {r['status']}")
    input("Pressione ENTER para voltar.")

def adicionar_reserva():
    print("\n➕ Nova Reserva (0 para voltar)")
    cursor.execute("SELECT id, nome_sala FROM salas")
    salas = cursor.fetchall()
    if not salas:
        print("Nenhuma sala cadastrada. Peça para um administrador adicionar salas primeiro.")
        return
    for s in salas:
        print(f"{s['id']} - {s['nome_sala']}")

    id_sala = input("ID da Sala: ").strip()
    if id_sala == '0': return
    data = input("Data (YYYY-MM-DD): ").strip()
    if data == '0': return
    hora_inicio = input("Hora Início (HH:MM:SS): ").strip()
    if hora_inicio == '0': return
    hora_fim = input("Hora Fim (HH:MM:SS): ").strip()
    if hora_fim == '0': return

    cursor.execute("""
        SELECT * FROM reservas
        WHERE id_sala = %s AND data_reserva = %s
        AND (
            hora_inicio < %s AND hora_fim > %s
        )
    """, (id_sala, data, hora_fim, hora_inicio))

    conflito = cursor.fetchone()
    if conflito:
        print("❌ ERRO: Já existe uma reserva para essa sala nesse horário!")
        return

    try:
        cursor.execute("""
            INSERT INTO reservas (id_usuario, id_sala, data_reserva, hora_inicio, hora_fim)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_logado['id'], id_sala, data, hora_inicio, hora_fim))
        conexao.commit()
        print("✅ Reserva adicionada com sucesso!")
    except mysql.connector.Error as err:
        print(f"❌ Erro ao adicionar reserva: {err}")


def pode_editar_reserva(reserva):
    """
    Retorna True se o usuário_logado pode editar a reserva dada, segundo a hierarquia:
    admin > professor > aluno.
    - Admin pode editar qualquer reserva.
    - Professor pode editar reservas próprias e de alunos (níveis abaixo).
    - Aluno só pode editar reservas próprias.
    """
    if usuario_logado['tipo'] == 'admin':
        return True
    if usuario_logado['tipo'] == 'professor':
        if reserva['id_usuario'] == usuario_logado['id']:
            return True
       
        cursor.execute("SELECT tipo FROM usuarios WHERE id = %s", (reserva['id_usuario'],))
        res_tipo = cursor.fetchone()
        if res_tipo and res_tipo['tipo'] == 'aluno':
            return True
        return False
    if usuario_logado['tipo'] == 'aluno':
        return reserva['id_usuario'] == usuario_logado['id']
    return False

def editar_reserva():
    print("\n✏️ Editar Reserva (0 para voltar)")
    id_reserva = input("ID da reserva que deseja editar: ").strip()
    if id_reserva == '0': return

    cursor.execute("""
        SELECT reservas.*, usuarios.tipo AS tipo_usuario_reserva
        FROM reservas
        JOIN usuarios ON reservas.id_usuario = usuarios.id
        WHERE reservas.id = %s
    """, (id_reserva,))
    reserva = cursor.fetchone()

    if not reserva:
        print("❗ Reserva não encontrada.")
        return

    if not pode_editar_reserva(reserva):
        print("❌ Permissão negada para editar esta reserva.")
        return

    nova_data = input("Nova data (YYYY-MM-DD): ").strip()
    if nova_data == '0': return
    nova_hora_inicio = input("Nova hora início (HH:MM:SS): ").strip()
    if nova_hora_inicio == '0': return
    nova_hora_fim = input("Nova hora fim (HH:MM:SS): ").strip()
    if nova_hora_fim == '0': return

    try:
        cursor.execute("""
            UPDATE reservas SET data_reserva=%s, hora_inicio=%s, hora_fim=%s
            WHERE id=%s
        """, (nova_data, nova_hora_inicio, nova_hora_fim, id_reserva))
        conexao.commit()
        print("✏️ Reserva editada com sucesso!")
    except mysql.connector.Error as err:
        print(f"❌ Erro ao editar reserva: {err}")

def pode_deletar_reserva(reserva):
    """
    Retorna True se o usuário_logado pode deletar a reserva dada, segundo a hierarquia:
    admin > professor > aluno.
    - Admin pode deletar qualquer reserva.
    - Professor pode deletar somente reservas próprias.
    - Aluno pode deletar somente reservas próprias.
    """
    if usuario_logado['tipo'] == 'admin':
        return True
    if usuario_logado['tipo'] == 'professor':
        return reserva['id_usuario'] == usuario_logado['id']
    if usuario_logado['tipo'] == 'aluno':
        return reserva['id_usuario'] == usuario_logado['id']
    return False

def deletar_reserva():
    print("\n❌ Deletar Reserva (0 para voltar)")
    id_reserva = input("ID da reserva a excluir: ").strip()
    if id_reserva == '0': return

    cursor.execute("SELECT * FROM reservas WHERE id = %s", (id_reserva,))
    reserva = cursor.fetchone()

    if not reserva:
        print("❗ Reserva não encontrada.")
        return

    if not pode_deletar_reserva(reserva):
        print("❌ Permissão negada para deletar esta reserva.")
        return

    confirm = input("Tem certeza que deseja deletar essa reserva? (s/n): ").strip().lower()
    if confirm != 's':
        print("Operação cancelada.")
        return

    try:
        cursor.execute("DELETE FROM reservas WHERE id = %s", (id_reserva,))
        conexao.commit()
        print("❌ Reserva excluída com sucesso!")
    except mysql.connector.Error as err:
        print(f"❌ Erro ao deletar reserva: {err}")

def adicionar_sala():
    if usuario_logado['tipo'] != 'admin':
        print("❌ Permissão negada. Apenas admins podem adicionar salas.")
        return

    print("\n🔬 Adicionar Nova Sala (0 para voltar)")
    nome_sala = input("Nome da nova sala: ").strip()
    if nome_sala == '0': return
    try:
        cursor.execute("INSERT INTO salas (nome_sala) VALUES (%s)", (nome_sala,))
        conexao.commit()
        print("🔬 Sala adicionada com sucesso!")
    except mysql.connector.Error as err:
        print(f"❌ Erro ao adicionar sala: {err}")

def deletar_usuario():
    if usuario_logado['tipo'] != 'admin':
        print("❌ Permissão negada. Apenas admins podem deletar usuários.")
        return

    print("\n🗑️ Deletar Usuário (0 para voltar)")
    email = input("Email do usuário a ser deletado: ").strip()
    if email == '0': return

    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
    resultado = cursor.fetchone()

    if resultado:
        confirm = input(f"Tem certeza que deseja deletar o usuário '{email}'? (s/n): ").strip().lower()
        if confirm == 's':
            try:
                cursor.execute("DELETE FROM usuarios WHERE email = %s", (email,))
                conexao.commit()
                print("✅ Usuário deletado com sucesso!")
            except mysql.connector.Error as err:
                print(f"❌ Erro ao deletar usuário: {err}")
    else:
        print("❗ Usuário não encontrado.")

def menu():
    while True:
        print("\n--- MENU CRUD RESERVAS ---")
        print("1. Listar Todas as Reservas")
        print("2. Listar Suas Reservas")
        print("3. Adicionar Reserva")
        print("4. Editar Reserva")
        print("5. Deletar Reserva")
        if usuario_logado['tipo'] == 'admin':
            print("6. Adicionar Nova Sala")
            print("7. Deletar Usuário")
            print("8. Fazer Backup do Banco")
            print("9. Logout")
        else:
            print("6. Logout")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == '1':
            listar_reservas()
        elif opcao == '2':
            listar_suas_reservas()
        elif opcao == '3':
            adicionar_reserva()
        elif opcao == '4':
            editar_reserva()
        elif opcao == '5':
            deletar_reserva()
        elif opcao == '6':
            if usuario_logado['tipo'] == 'admin':
                adicionar_sala()
            else:
                confirm = input("Tem certeza que deseja fazer logout? (s/n): ").strip().lower()
                if confirm == 's':
                    print("🔒 Logout realizado.")
                    break
        elif opcao == '7' and usuario_logado['tipo'] == 'admin':
            deletar_usuario()
        elif opcao == '8' and usuario_logado['tipo'] == 'admin':
            backup_banco_dados()
        elif opcao == '9' and usuario_logado['tipo'] == 'admin':
            confirm = input("Tem certeza que deseja fazer logout? (s/n): ").strip().lower()
            if confirm == 's':
                print("🔒 Logout realizado.")
                break
        else:
            print("❗ Opção inválida ou não permitida para seu perfil.")

if __name__ == "__main__":
    try:
        menu_inicial()
    finally:
        cursor.close()
        conexao.close()
