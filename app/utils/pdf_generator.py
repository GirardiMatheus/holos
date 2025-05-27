from fpdf import FPDF
from datetime import datetime, timedelta
import tempfile
from flask import send_file

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

def gerar_pdf_orcamento(cliente, cpf, exames_selecionados):
    """
    Gera um PDF de orçamento e retorna o objeto PDF pronto para ser outputado
    Args:
        cliente (str): Nome do cliente
        cpf (str): CPF do cliente
        exames_selecionados (list): Lista de dicionários com {'nome': str, 'valor': str}
    Returns:
        FPDF: Objeto PDF gerado
    """
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

    # Tabela de exames
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(149, 6, 6)
    pdf.cell(140, 6, "Exames", border=1, align='C')
    pdf.cell(40, 6, "Valor", border=1, align='C', ln=True)
    pdf.set_font("Arial", size=8)
    pdf.set_text_color(63, 23, 23)

    total = 0.0
    for exame in exames_selecionados:
        nome = exame.get('nome', '')
        valor_str = exame.get('valor', '0').replace(',', '.')
        try:
            valor_float = float(valor_str)
        except ValueError:
            valor_float = 0.0
        total += valor_float
        pdf.cell(140, 6, nome, border=1)
        pdf.cell(40, 6, f"R$ {valor_float:.2f}".replace('.', ','), border=1, ln=True)

    # Total
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(140, 6, "Total", border=1)
    pdf.cell(40, 6, f"R$ {total:.2f}".replace('.', ','), border=1, ln=True)

    return pdf

def gerar_e_enviar_pdf(cliente, cpf, exames_selecionados):
    """
    Gera o PDF e prepara para envio como resposta HTTP
    Args:
        cliente (str): Nome do cliente
        cpf (str): CPF do cliente
        exames_selecionados (list): Lista de exames
    Returns:
        Response: Resposta Flask com o PDF anexado
    """
    pdf = gerar_pdf_orcamento(cliente, cpf, exames_selecionados)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return send_file(
            tmp.name,
            as_attachment=True,
            download_name=f"orcamento_{cliente}.pdf",
            mimetype='application/pdf'
        )