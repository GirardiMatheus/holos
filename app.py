from flask import Flask, request, jsonify, redirect, url_for, render_template, session, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from fpdf import FPDF
from functools import wraps
from datetime import datetime, timedelta
import bcrypt
import csv
import os
import tempfile

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELS
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.LargeBinary(128), nullable=False)

class Exame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.String(50), nullable=False)

# Decorator para login obrigatório
def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return route(*args, **kwargs)
    return wrapper

# ROTAS

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            # Converta o hash armazenado para bytes se necessário
            stored_hash = usuario.senha_hash
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(senha.encode('utf-8'), stored_hash):
                session['username'] = username
                return jsonify({"status": "success", "message": "Login realizado com sucesso!"})
        
        return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/exames', methods=['GET'])
@login_required
def listar_exames():
    exames = Exame.query.all()
    return jsonify([{"nome": e.nome, "valor": e.valor} for e in exames])

@app.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar_exame():
    data = request.get_json()
    if not data or 'nome' not in data or 'valor' not in data:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400

    exame = Exame(nome=data['nome'], valor=data['valor'])
    db.session.add(exame)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/editar_exame', methods=['POST'])
@login_required
def editar_exame():
    data = request.get_json()
    if not data or 'nomeAntigo' not in data or 'nomeNovo' not in data or 'valor' not in data:
        return jsonify({"status": "error", "message": "Dados incompletos"}), 400

    exame = Exame.query.filter_by(nome=data['nomeAntigo']).first()
    if exame:
        exame.nome = data['nomeNovo']
        exame.valor = data['valor']
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Exame não encontrado"}), 404

@app.route('/excluir_exame', methods=['POST'])
@login_required
def excluir_exame():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({"status": "error", "message": "Nome não fornecido"}), 400

    exame = Exame.query.filter_by(nome=data['nome']).first()
    if exame:
        db.session.delete(exame)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Exame não encontrado"}), 404

@app.route('/gerar_orcamento', methods=['POST'])
@login_required
def gerar_orcamento():
    data = request.get_json()
    cliente = data.get('cliente')
    cpf = data.get('cpf')
    exames_selecionados = data.get('exames')

    if not cliente or not cpf or not exames_selecionados:
        return jsonify({"status": "error", "message": "Dados insuficientes"}), 400

    class PDF(FPDF):
        def __init__(self):
            super().__init__()
            self.footer_height = 25
            
        def footer(self):
            self.set_y(-self.footer_height + 5)
            self.set_font("Arial", size=8)
            self.set_text_color(149, 6, 6)
            self.cell(0, 5, txt="Obrigado pela preferência!", ln=True, align='C')
            self.set_font("Arial", 'I', 7)
            self.set_text_color(63, 23, 23)
            self.cell(0, 4, txt="Laboratório Holos", ln=True, align='C')
            self.cell(0, 4, txt="Avenida Doutor Galdino do Valle Filho, N 133, Centro, 28625-010, Nova Friburgo - RJ", ln=True, align='C')
            self.cell(0, 4, txt="(22)9 8837-0724 | @holoservicosmedicos", ln=True, align='C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=pdf.footer_height)
    pdf.set_margins(left=10, top=10, right=10)

    # Cabeçalho
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(149, 6, 6)
    pdf.cell(0, 6, txt="LABORATÓRIO HOLOS", ln=True, align='C')
    pdf.set_font("Arial", size=8)
    pdf.set_text_color(63, 23, 23)
    pdf.cell(0, 5, txt="Saúde Ocupacional", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, txt="ORÇAMENTO", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", size=8)
    data_atual = datetime.now()
    pdf.cell(0, 5, txt=f"COLABORADOR: {cliente}", ln=True)
    pdf.cell(0, 5, txt=f"CPF: {cpf} | DATA: {data_atual.strftime('%d/%m/%Y')} | VÁLIDO ATÉ: {(data_atual + timedelta(days=30)).strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)

    # Tabela
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(149, 6, 6)
    pdf.cell(140, 6, "Exames", border=1, align='C')
    pdf.cell(40, 6, "Valor", border=1, align='C', ln=True)
    pdf.set_font("Arial", size=8)
    pdf.set_text_color(63, 23, 23)

    total = 0.0
    for exame in exames_selecionados:
        nome = exame.get('nome')
        valor_str = exame.get('valor', '0').replace(',', '.')
        try:
            valor_float = float(valor_str)
        except ValueError:
            valor_float = 0.0
        total += valor_float
        pdf.cell(140, 6, nome, border=1)
        pdf.cell(40, 6, f"R$ {valor_float:.2f}".replace('.', ','), border=1, ln=True)

    pdf.set_font("Arial", 'B', 8)
    pdf.cell(140, 6, "Total", border=1)
    pdf.cell(40, 6, f"R$ {total:.2f}".replace('.', ','), border=1, ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return send_file(tmp.name, download_name=f"orcamento_{cliente}.pdf", as_attachment=True)

@app.route('/exportar_csv')
@login_required
def exportar_csv():
    exames = Exame.query.all()
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".csv", newline='', encoding='utf-8') as tmp:
        writer = csv.writer(tmp)
        writer.writerow(["Nome", "Valor"])
        for e in exames:
            writer.writerow([e.nome, e.valor])
        tmp.flush()
        return send_file(tmp.name, download_name="exames_exportados.csv", as_attachment=True)

@app.route('/importar_csv', methods=['POST'])
@login_required
def importar_csv():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.csv'):
        return jsonify({"status": "error", "message": "Arquivo inválido"}), 400

    try:
        file_data = file.read().decode('utf-8').splitlines()
        reader = csv.reader(file_data)
        next(reader)  
        for row in reader:
            db.session.add(Exame(nome=row[0], valor=row[1]))
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao importar: {str(e)}"}), 500

# Inicialização do banco
with app.app_context():
    db.create_all()
    
    # Limpa usuários existentes para evitar duplicatas
    Usuario.query.delete()
    
    # Adiciona os usuários com os hashes gerados
    usuarios = [
        {
            'username': 'velorin',
            'senha_hash': b'$2b$12$2gYAxX0YXlZeq6FMKgSktOE5ezsxtMrJBtzJ26asBIeq0Drdh.FIy'  
        },
        {
            'username': 'r.souza',
            'senha_hash': b'$2b$12$dqO.B7Zs.EywgyjnH3xjYuMxZHb/Yur4JQYtj9WnOA77pI6mNxNJ2'  
        }
    ]
    
    for usuario in usuarios:
        if not Usuario.query.filter_by(username=usuario['username']).first():
            db.session.add(Usuario(
                username=usuario['username'],
                senha_hash=usuario['senha_hash']
            ))
    
    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
