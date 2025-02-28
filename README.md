# Laboratório Holos - Sistema de Gerenciamento de Exames e Orçamentos

Este projeto é um sistema web desenvolvido para o Laboratório Holos, que permite o gerenciamento de exames, cadastro de novos exames, edição, exclusão, geração de orçamentos em PDF e importação/exportação de dados em CSV.

## Tecnologias Utilizadas
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Banco de Dados**: CSV (para armazenamento de exames)
- **Bibliotecas**:
  - `FPDF` para geração de PDFs.
  - `bcrypt` para autenticação de usuários.

## Funcionalidades
1. **Autenticação de Usuários**:
   - Login e logout com senha criptografada.
   - Acesso restrito a usuários autenticados.

2. **Gerenciamento de Exames**:
   - Cadastro de novos exames.
   - Edição e exclusão de exames existentes.
   - Listagem de exames com filtro de pesquisa.

3. **Geração de Orçamentos**:
   - Seleção de exames para gerar um orçamento.
   - Geração de PDF com detalhes do orçamento.

4. **Importação e Exportação de Dados**:
   - Exportar a lista de exames para um arquivo CSV.
   - Importar exames a partir de um arquivo CSV.

5. **Interface Responsiva**:
   - Design adaptável para diferentes tamanhos de tela.



