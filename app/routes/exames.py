from flask import Blueprint, request, jsonify, send_file
from .. import db
from ..models.exame import Exame
from ..utils.decorators import login_required
import csv
import tempfile

exames_bp = Blueprint('exames', __name__)

@exames_bp.route('/exames', methods=['GET'])
@login_required
def listar_exames():
    exames = Exame.query.all()
    return jsonify([{"nome": e.nome, "valor": e.valor} for e in exames])

@exames_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrar_exame():
    data = request.get_json()
    if not data or 'nome' not in data or 'valor' not in data:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400

    try:
        exame = Exame(nome=data['nome'], valor=data['valor'])
        db.session.add(exame)
        db.session.commit()
        return jsonify({"status": "success", "message": "Exame cadastrado com sucesso"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Erro ao cadastrar: {str(e)}"}), 500

@exames_bp.route('/editar_exame', methods=['POST'])
@login_required
def editar_exame():
    data = request.get_json()
    if not data or 'nomeAntigo' not in data or 'nomeNovo' not in data or 'valor' not in data:
        return jsonify({"status": "error", "message": "Dados incompletos"}), 400

    try:
        exame = Exame.query.filter_by(nome=data['nomeAntigo']).first()
        if not exame:
            return jsonify({"status": "error", "message": "Exame não encontrado"}), 404
            
        exame.nome = data['nomeNovo']
        exame.valor = data['valor']
        db.session.commit()
        return jsonify({"status": "success", "message": "Exame atualizado com sucesso"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Erro ao editar: {str(e)}"}), 500

@exames_bp.route('/excluir_exame', methods=['POST'])
@login_required
def excluir_exame():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({"status": "error", "message": "Nome não fornecido"}), 400

    try:
        exame = Exame.query.filter_by(nome=data['nome']).first()
        if not exame:
            return jsonify({"status": "error", "message": "Exame não encontrado"}), 404
            
        db.session.delete(exame)
        db.session.commit()
        return jsonify({"status": "success", "message": "Exame excluído com sucesso"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Erro ao excluir: {str(e)}"}), 500

@exames_bp.route('/exportar_csv')
@login_required
def exportar_csv():
    try:
        exames = Exame.query.all()
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".csv", newline='', encoding='utf-8') as tmp:
            writer = csv.writer(tmp)
            writer.writerow(["Nome", "Valor"])
            for e in exames:
                writer.writerow([e.nome, e.valor])
            tmp.flush()
            return send_file(
                tmp.name,
                download_name="exames_exportados.csv",
                as_attachment=True,
                mimetype='text/csv'
            )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao exportar: {str(e)}"}), 500

@exames_bp.route('/importar_csv', methods=['POST'])
@login_required
def importar_csv():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400
        
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({"status": "error", "message": "Formato de arquivo inválido"}), 400

    try:
        file_data = file.read().decode('utf-8').splitlines()
        reader = csv.reader(file_data)
        next(reader)  # Pula cabeçalho
        
        for row in reader:
            if len(row) >= 2:  # Verifica se tem pelo menos nome e valor
                db.session.add(Exame(nome=row[0].strip(), valor=row[1].strip()))
        
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"CSV importado com sucesso! {len(list(reader))} exames adicionados."
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Erro ao importar CSV: {str(e)}"
        }), 500