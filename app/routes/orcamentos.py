from flask import Blueprint, request, jsonify, send_file
from ..utils.decorators import login_required
from ..utils.pdf_generator import gerar_pdf_orcamento
import tempfile
import os

orcamentos_bp = Blueprint('orcamentos', __name__)

@orcamentos_bp.route('/gerar_orcamento', methods=['POST'])
@login_required
def gerar_orcamento():
    # Validação dos dados de entrada
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Nenhum dado fornecido"}), 400

    cliente = data.get('cliente', '').strip()
    cpf = data.get('cpf', '').strip()
    exames_selecionados = data.get('exames', [])

    if not cliente:
        return jsonify({"status": "error", "message": "Nome do cliente não fornecido"}), 400
    if not cpf:
        return jsonify({"status": "error", "message": "CPF não fornecido"}), 400
    if not exames_selecionados or len(exames_selecionados) == 0:
        return jsonify({"status": "error", "message": "Nenhum exame selecionado"}), 400

    try:
        # Gera o PDF usando a função do módulo utils
        pdf = gerar_pdf_orcamento(cliente, cpf, exames_selecionados)
        
        # Cria um arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            tmp_path = tmp.name
        
        # Envia o arquivo como resposta
        response = send_file(
            tmp_path,
            as_attachment=True,
            download_name=f"orcamento_{cliente}.pdf",
            mimetype='application/pdf'
        )
        
        # Remove o arquivo temporário após enviar
        response.call_on_close(lambda: os.unlink(tmp_path))
        
        return response

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao gerar o orçamento: {str(e)}"
        }), 500