from flask import Flask, render_template, request, redirect, session, url_for, flash, make_response, send_file
import bcrypt, mysql.connector
import os, time, io
import subprocess
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

conn = mysql.connector.connect(
    host="localhost",
    user="usuario_lab",
    password="senha123",
    database="reserva_laboratorio"
)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha'].encode('utf-8')
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usr = cursor.fetchone()
        if usr and bcrypt.checkpw(senha, usr['senha'].encode('utf-8')):
            session['usuario_id'] = usr['id']
            session['usuario_nome'] = usr['nome']
            session['tipo'] = usr['tipo']
            return redirect(url_for('dashboard'))
        flash("Email ou senha inválidos.")
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()
        tipo = request.form['tipo']

        if tipo not in ['admin', 'professor', 'aluno']:
            flash("Tipo de usuário inválido.")
            return redirect(url_for('cadastro'))

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("E-mail já cadastrado.")
            return redirect(url_for('cadastro'))

        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)", (nome, email, senha_hash, tipo))
        conn.commit()
        flash("✅ Usuário cadastrado com sucesso!")
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', nome=session.get('usuario_nome'))

@app.route('/listar_reservas')
def listar_reservas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reservas.id, usuarios.nome AS nome_usuario, salas.nome_sala, data_reserva, hora_inicio, hora_fim, status
        FROM reservas
        JOIN usuarios ON reservas.id_usuario = usuarios.id
        JOIN salas ON reservas.id_sala = salas.id
    """)
    reservas = cursor.fetchall()
    return render_template('listar_reservas.html', reservas=reservas)

@app.route('/gerar_pdf/<int:id>', methods=['POST'])
def gerar_pdf(id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reservas.id, usuarios.nome AS nome_usuario, salas.nome_sala, data_reserva, hora_inicio, hora_fim, status
        FROM reservas
        JOIN usuarios ON reservas.id_usuario = usuarios.id
        JOIN salas ON reservas.id_sala = salas.id
        WHERE reservas.id = %s
    """, (id,))
    reserva = cursor.fetchone()

    if not reserva:
        flash("Reserva não encontrada.")
        return redirect(url_for('listar_reservas'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Detalhes da Reserva", ln=True, align='C')
    pdf.ln(10)

    for key, value in reserva.items():
        pdf.cell(200, 10, txt=f"{key.capitalize()}: {value}", ln=True)

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Reserva_{id}.pdf'
    return response

@app.route('/gerar_pdf_lista', methods=['POST'])
def gerar_pdf_lista():
    if 'usuario_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT usuarios.nome AS nome_usuario, salas.nome_sala, data_reserva, hora_inicio, hora_fim, status
        FROM reservas
        JOIN usuarios ON reservas.id_usuario = usuarios.id
        JOIN salas ON reservas.id_sala = salas.id
    """)
    reservas = cursor.fetchall()

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    textobject = c.beginText(40, 750)
    textobject.setFont("Helvetica", 12)
    textobject.textLine("Relatório de Reservas - Sistema de Laboratório")
    textobject.moveCursor(0, 20)

    for r in reservas:
        linha = f"Usuário: {r['nome_usuario']} | Sala: {r['nome_sala']} | Data: {r['data_reserva']} | Início: {r['hora_inicio']} | Fim: {r['hora_fim']} | Status: {r['status']}"
        textobject.textLine(linha)
        textobject.moveCursor(0, 10)

    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="relatorio_reservas.pdf", mimetype='application/pdf')

@app.route('/minhas_reservas')
def minhas_reservas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT reservas.id, salas.nome_sala, data_reserva, hora_inicio, hora_fim, status
        FROM reservas
        JOIN salas ON reservas.id_sala = salas.id
        WHERE reservas.id_usuario = %s
    """, (session['usuario_id'],))
    reservas = cursor.fetchall()
    return render_template('reservas.html', reservas=reservas)

@app.route('/adicionar_reserva', methods=['GET', 'POST'])
def adicionar_reserva():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome_sala FROM salas")
    salas = cursor.fetchall()

    if request.method == 'POST':
        id_sala = request.form['id_sala']
        data = request.form['data']
        hora_inicio = request.form['hora_inicio']
        hora_fim = request.form['hora_fim']

        cursor.execute("""
            INSERT INTO reservas (id_usuario, id_sala, data_reserva, hora_inicio, hora_fim)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['usuario_id'], id_sala, data, hora_inicio, hora_fim))
        conn.commit()
        flash("✅ Reserva adicionada com sucesso!")
        return redirect(url_for('minhas_reservas'))

    return render_template('adicionar_reserva.html', salas=salas)

@app.route('/adicionar_sala', methods=['GET', 'POST'])
def adicionar_sala():
    if 'usuario_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        nome_sala = request.form['nome_sala'].strip()
        if nome_sala:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO salas (nome_sala) VALUES (%s)", (nome_sala,))
            conn.commit()
            flash("🔬 Sala adicionada com sucesso!")
            return redirect(url_for('dashboard'))
        flash("❗ Nome da sala não pode ser vazio.")

    return render_template('adicionar_sala.html')

@app.route('/deletar_sala', methods=['GET', 'POST'])
def deletar_sala():
    if 'usuario_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome_sala FROM salas")
    salas = cursor.fetchall()

    if request.method == 'POST':
        id_sala = request.form['id_sala']
        cursor.execute("DELETE FROM salas WHERE id = %s", (id_sala,))
        conn.commit()
        flash("🧹 Sala deletada com sucesso!")
        return redirect(url_for('deletar_sala'))

    return render_template('deletar_sala.html', salas=salas)

@app.route('/editar_reserva', methods=['GET', 'POST'])
def editar_reserva():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    tipo = session.get('tipo')
    usuario_id = session.get('usuario_id')
    cursor = conn.cursor(dictionary=True)

    if tipo == 'admin':
        cursor.execute("""
            SELECT reservas.id, salas.nome_sala, data_reserva, hora_inicio, hora_fim
            FROM reservas
            JOIN salas ON reservas.id_sala = salas.id
        """)
    elif tipo == 'professor':
        cursor.execute("""
            SELECT reservas.id, salas.nome_sala, data_reserva, hora_inicio, hora_fim
            FROM reservas
            JOIN salas ON reservas.id_sala = salas.id
            JOIN usuarios ON reservas.id_usuario = usuarios.id
            WHERE usuarios.tipo IN ('aluno', 'professor')
        """)
    else: 
        cursor.execute("""
            SELECT reservas.id, salas.nome_sala, data_reserva, hora_inicio, hora_fim
            FROM reservas
            JOIN salas ON reservas.id_sala = salas.id
            WHERE reservas.id_usuario = %s
        """, (usuario_id,))

    reservas = cursor.fetchall()

    if request.method == 'POST':
        id_reserva = request.form['id_reserva']
        nova_data = request.form['data']
        nova_hora_inicio = request.form['hora_inicio']
        nova_hora_fim = request.form['hora_fim']

        if tipo == 'admin':
            pode_editar = True
        elif tipo == 'professor':
            cursor.execute("""
                SELECT usuarios.tipo FROM reservas
                JOIN usuarios ON reservas.id_usuario = usuarios.id
                WHERE reservas.id = %s
            """, (id_reserva,))
            destino = cursor.fetchone()
            pode_editar = destino and destino['tipo'] in ['aluno', 'professor']
        else:  
            cursor.execute("SELECT id_usuario FROM reservas WHERE id = %s", (id_reserva,))
            destino = cursor.fetchone()
            pode_editar = destino and destino['id_usuario'] == usuario_id

        if pode_editar:
            cursor.execute("""
                UPDATE reservas SET data_reserva=%s, hora_inicio=%s, hora_fim=%s
                WHERE id=%s
            """, (nova_data, nova_hora_inicio, nova_hora_fim, id_reserva))
            conn.commit()
            flash("✏️ Reserva atualizada com sucesso!")
            return redirect(url_for('reservas'))
        else:
            flash("❌ Você não tem permissão para editar essa reserva.")

    return render_template('editar_reserva.html', reservas=reservas)

@app.route('/deletar_reserva', methods=['GET', 'POST'])
def deletar_reserva():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    tipo = session.get('tipo')
    usuario_id = session.get('usuario_id')
    cursor = conn.cursor(dictionary=True)

    if tipo == 'admin':
        cursor.execute("""
            SELECT reservas.id, salas.nome_sala, data_reserva
            FROM reservas
            JOIN salas ON reservas.id_sala = salas.id
        """)
    elif tipo == 'professor':
        cursor.execute("""
            SELECT reservas.id, salas.nome_sala, data_reserva
            FROM reservas
            JOIN salas ON reservas.id_sala = salas.id
            JOIN usuarios ON reservas.id_usuario = usuarios.id
            WHERE usuarios.tipo IN ('aluno', 'professor') AND usuarios.id = %s OR usuarios.tipo = 'aluno'
        """, (usuario_id,))
    else:  
        cursor.execute("""
            SELECT reservas.id, salas.nome_sala, data_reserva
            FROM reservas
            JOIN salas ON reservas.id_sala = salas.id
            WHERE reservas.id_usuario = %s
        """, (usuario_id,))

    reservas = cursor.fetchall()

    if request.method == 'POST':
        id_reserva = request.form['id_reserva']

        pode_deletar = False
        if tipo == 'admin':
            pode_deletar = True
        elif tipo == 'professor':
            cursor.execute("""
                SELECT usuarios.tipo, reservas.id_usuario
                FROM reservas
                JOIN usuarios ON reservas.id_usuario = usuarios.id
                WHERE reservas.id = %s
            """, (id_reserva,))
            destino = cursor.fetchone()
            pode_deletar = destino and (destino['tipo'] == 'aluno' or destino['id_usuario'] == usuario_id)
        else:
            cursor.execute("SELECT id_usuario FROM reservas WHERE id = %s", (id_reserva,))
            destino = cursor.fetchone()
            pode_deletar = destino and destino['id_usuario'] == usuario_id

        if pode_deletar:
            cursor.execute("DELETE FROM reservas WHERE id = %s", (id_reserva,))
            conn.commit()
            flash("❌ Reserva deletada com sucesso!")
            return redirect(url_for('minhas_reservas'))
        else:
            flash("🚫 Você não tem permissão para deletar essa reserva.")

    return render_template('deletar_reserva.html', reservas=reservas)


@app.route('/deletar_usuario', methods=['GET', 'POST'])
def deletar_usuario():
    if 'usuario_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, email, tipo FROM usuarios WHERE tipo != 'admin'")
    usuarios = cursor.fetchall()

    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        cursor.execute("DELETE FROM usuarios WHERE id = %s AND tipo != 'admin'", (id_usuario,))
        conn.commit()
        flash("🗑 Usuário deletado com sucesso!")
        return redirect(url_for('deletar_usuario'))

    return render_template('deletar_usuario.html', usuarios=usuarios)

@app.route('/backup', endpoint='backup_banco')
def backup():
    if 'usuario_id' not in session or session.get('tipo') != 'admin':
        flash("Acesso negado.")
        return redirect(url_for('dashboard'))

    nome_arquivo = f"backup_{time.strftime('%Y%m%d_%H%M%S')}.sql"
    caminho_mysqldump = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    comando = [
        caminho_mysqldump,
        "-u", "usuario_lab",
        "-psenha123",
        "--single-transaction",
        "--skip-lock-tables",
        "reserva_laboratorio"
    ]

    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            subprocess.run(comando, stdout=f, stderr=subprocess.PIPE, check=True)
        flash(f"✅ Backup realizado com sucesso: {nome_arquivo}")
    except subprocess.CalledProcessError as e:
        flash(f"❌ Erro ao realizar backup: {e.stderr.decode()}")

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Logout realizado com sucesso!")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
