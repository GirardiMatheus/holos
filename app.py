from flask import Flask, request, jsonify, redirect, url_for, render_template, session, send_file
import bcrypt
from fpdf import FPDF
import csv
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  

usuarios = {
    "velorin": {
        "senha_hash": b'$2b$12$ZdDv3hl4F.XPV6xw6073J.PAjVAIuOhwAM/pLqF8fhERAXWlxVB3C', 
    },
    "r.souza": {
        "senha_hash": b'$2b$12$GQDP2JRI8c/.Kx4IaOvl2e2f/j5ISGtOhz7EIL1IPJWAeXjkJa2/W',  
    }
}

def login_required(route):
    @wraps(route)  
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return route(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  
        senha = request.form.get('senha')

        if username in usuarios:
            senha_hash = usuarios[username]['senha_hash']

            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
                session['username'] = username  
                return jsonify({"status": "success", "message": "Login realizado com sucesso!"})
            else:
                return jsonify({"status": "error", "message": "Senha incorreta"}), 401
        else:
            return jsonify({"status": "error", "message": "Usuário não encontrado"}), 404

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

CSV_FILE = 'exames.csv'

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Nome", "Valor"])

@app.route('/exames', methods=['GET'])
@login_required
def listar_exames():
    exames = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        next(reader)  
        for row in reader:
            exames.append({"nome": row[0], "valor": row[1]})
    return jsonify(exames)

@app.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar_exame():
    nome = request.json.get('nome')
    valor = request.json.get('valor')
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nome, valor])
    return jsonify({"status": "success"})

@app.route('/editar_exame', methods=['POST'])
@login_required
def editar_exame():
    nome_antigo = request.json.get('nomeAntigo')
    nome_novo = request.json.get('nomeNovo')
    valor = request.json.get('valor')

    exames = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        exames = list(reader)

    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in exames:
            if row[0] == nome_antigo:
                writer.writerow([nome_novo, valor])
            else:
                writer.writerow(row)

    return jsonify({"status": "success"})

@app.route('/excluir_exame', methods=['POST'])
@login_required
def excluir_exame():
    nome = request.json.get('nome')

    exames = []
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        exames = list(reader)

    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in exames:
            if row[0] != nome:
                writer.writerow(row)

    return jsonify({"status": "success"})

@app.route('/gerar_orcamento', methods=['POST'])
@login_required
def gerar_orcamento():
    from datetime import datetime, timedelta
    cliente = request.json.get('cliente')
    cpf = request.json.get('cpf')
    exames_selecionados = request.json.get('exames')

    data_atual = datetime.now()
    data_formatada = data_atual.strftime("%d/%m/%Y")
    data_validade = data_atual + timedelta(days=30)
    data_validade_formatada = data_validade.strftime("%d/%m/%Y")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(149, 6, 6) 
    pdf.cell(200, 10, txt="LABORATÓRIO HOLOS", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(63, 23, 23)  
    pdf.cell(200, 10, txt="Saúde Ocupacional", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(149, 6, 6) 
    pdf.cell(200, 10, txt="ORÇAMENTO", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.set_text_color(63, 23, 23)  
    pdf.cell(200, 10, txt=f"COLABORADOR: {cliente}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"CPF: {cpf}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"ORÇAMENTO REALIZADO NO DIA: {data_formatada}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"VÁLIDO ATÉ O DIA: {data_validade_formatada}", ln=True, align='L')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(149, 6, 6)  
    pdf.cell(95, 10, txt="Exames", border=1, align='C')
    pdf.cell(95, 10, txt="Total da linha", border=1, align='C', ln=True)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(63, 23, 23)  

    total = 0
    for exame in exames_selecionados:
        pdf.cell(95, 10, txt=exame['nome'], border=1, align='L')
        pdf.cell(95, 10, txt=f"R$ {exame['valor']}", border=1, align='C', ln=True)
        total += float(exame['valor'])

    pdf.cell(95, 10, txt="Total", border=1, align='L')
    pdf.cell(95, 10, txt=f"R$ {total:.2f}", border=1, align='C', ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.set_text_color(149, 6, 6)  
    pdf.cell(200, 10, txt="Obrigado pela preferência!", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(63, 23, 23)  
    pdf.cell(200, 10, txt="Laboratório Holos", ln=True, align='C')
    pdf.cell(200, 10, txt="Avenida Doutor Galdino do Valle Filho, N 133, Centro, 28625-010, Nova Friburgo - RJ", ln=True, align='C')
    pdf.cell(200, 10, txt="(22)9 8837-0724 | @holoservicosmedicos", ln=True, align='C')

    pdf_output = f"orcamento_{cliente}.pdf"
    pdf.output(pdf_output)

    return send_file(pdf_output, as_attachment=True)

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT))
