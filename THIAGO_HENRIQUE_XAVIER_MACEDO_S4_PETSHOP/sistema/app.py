import sqlite3
import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-super-secreta-para-o-prazo-1130'
DATABASE = 'petshop.db'
EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')

# --- Gerenciamento do Banco de Dados ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_path = os.path.join(app.root_path, DATABASE)
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

# --- Wrapper para rota protegida ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para ver esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Algoritmo de Ordenação (Exigência da Reflexão) ---
# (Resposta para a Pergunta 2a do questionário)
def insertion_sort(lista_produtos):
    """Ordena uma lista de dicionários de produtos pelo 'nome' em ordem alfabética."""
    for i in range(1, len(lista_produtos)):
        chave = lista_produtos[i]
        nome_chave = chave['nome'].lower()
        j = i - 1
        
        while j >= 0 and lista_produtos[j]['nome'].lower() > nome_chave:
            lista_produtos[j + 1] = lista_produtos[j]
            j -= 1
        lista_produtos[j + 1] = chave
    return lista_produtos

# --- Rotas de Autenticação ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nome_usuario = request.form['username']; senha = request.form['password']
        db = get_db()
        usuario = db.execute('SELECT * FROM Usuarios WHERE nome_usuario = ? AND senha = ?', (nome_usuario, senha)).fetchone()
        if usuario:
            session['user_id'] = usuario['id_usuario']; session['user_name'] = usuario['nome_completo']
            flash('Login realizado com sucesso!', 'success'); return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None); session.pop('user_name', None)
    flash('Você saiu do sistema.', 'info'); return redirect(url_for('login'))

# --- Rotas Principais (Dashboard) ---
@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- ROTAS DE PRODUTOS ---
@app.route('/produtos')
@login_required
def produtos():
    db = get_db(); busca = request.args.get('busca', '')
    if busca:
        db_rows = db.execute("SELECT * FROM Produtos WHERE nome LIKE ? ORDER BY nome", ('%' + busca + '%',)).fetchall()
    else:
        db_rows = db.execute("SELECT * FROM Produtos ORDER BY nome").fetchall()
    produtos = [dict(row) for row in db_rows]
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/add', methods=['POST'])
@login_required
def add_produto():
    nome = request.form['nome']; categoria = request.form['categoria']
    if not nome: flash('O nome do produto é obrigatório.', 'danger'); return redirect(url_for('produtos'))
    try:
        preco = float(request.form['preco'])
        if preco <= 0: flash('O preço deve ser maior que zero.', 'danger'); return redirect(url_for('produtos'))
    except ValueError: flash('Formato de preço inválido.', 'danger'); return redirect(url_for('produtos'))
    try:
        quantidade = int(request.form['quantidade'])
        if quantidade < 0: flash('A quantidade não pode ser negativa.', 'danger'); return redirect(url_for('produtos'))
    except ValueError: flash('Formato de quantidade inválido.', 'danger'); return redirect(url_for('produtos'))
    db = get_db()
    db.execute('INSERT INTO Produtos (nome, categoria, preco, quantidade) VALUES (?, ?, ?, ?)', (nome, categoria, preco, quantidade))
    db.commit()
    flash('Produto cadastrado com sucesso!', 'success'); return redirect(url_for('produtos'))

@app.route('/produtos/update/<int:id>', methods=['POST'])
@login_required
def update_produto(id):
    nome = request.form['nome']; categoria = request.form['categoria']
    if not nome: flash('O nome do produto é obrigatório.', 'danger'); return redirect(url_for('produtos'))
    try:
        preco = float(request.form['preco'])
        if preco <= 0: flash('O preço deve ser maior que zero.', 'danger'); return redirect(url_for('produtos'))
    except ValueError: flash('Formato de preço inválido.', 'danger'); return redirect(url_for('produtos'))
    try:
        quantidade = int(request.form['quantidade'])
        if quantidade < 0: flash('A quantidade não pode ser negativa.', 'danger'); return redirect(url_for('produtos'))
    except ValueError: flash('Formato de quantidade inválido.', 'danger'); return redirect(url_for('produtos'))
    db = get_db()
    db.execute('UPDATE Produtos SET nome = ?, categoria = ?, preco = ?, quantidade = ? WHERE id_produto = ?', (nome, categoria, preco, quantidade, id))
    db.commit()
    flash('Produto atualizado com sucesso!', 'info'); return redirect(url_for('produtos'))

@app.route('/produtos/delete/<int:id>', methods=['POST'])
@login_required
def delete_produto(id):
    db = get_db()
    venda = db.execute('SELECT 1 FROM Vendas WHERE id_produto_fk = ?', (id,)).fetchone()
    if venda:
        flash('Não é possível excluir um produto que já foi vendido.', 'danger')
    else:
        db.execute('DELETE FROM Produtos WHERE id_produto = ?', (id,))
        db.commit()
        flash('Produto excluído com sucesso.', 'success')
    return redirect(url_for('produtos'))

# --- ROTAS DE CLIENTES ---
@app.route('/clientes')
@login_required
def clientes():
    db = get_db(); busca = request.args.get('busca', '')
    if busca:
        db_rows = db.execute("SELECT * FROM Clientes WHERE nome_completo LIKE ? ORDER BY nome_completo", ('%' + busca + '%',)).fetchall()
    else:
        db_rows = db.execute("SELECT * FROM Clientes ORDER BY nome_completo").fetchall()
    clientes = [dict(row) for row in db_rows]
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/add', methods=['POST'])
@login_required
def add_cliente():
    nome = request.form['nome_completo']; email = request.form['email']; telefone = request.form['telefone']
    if not nome: flash('O nome do cliente é obrigatório.', 'danger'); return redirect(url_for('clientes'))
    if email and not EMAIL_REGEX.match(email):
        flash('Formato de e-mail inválido. Certifique-se de incluir "@" e ".".', 'danger'); return redirect(url_for('clientes'))
    db = get_db()
    if email:
        existente = db.execute('SELECT 1 FROM Clientes WHERE email = ?', (email,)).fetchone()
        if existente: flash('Este e-mail já está cadastrado.', 'danger'); return redirect(url_for('clientes'))
    db.execute('INSERT INTO Clientes (nome_completo, email, telefone) VALUES (?, ?, ?)', (nome, email, telefone))
    db.commit()
    flash('Cliente cadastrado com sucesso!', 'success'); return redirect(url_for('clientes'))

@app.route('/clientes/update/<int:id>', methods=['POST'])
@login_required
def update_cliente(id):
    nome = request.form['nome_completo']; email = request.form['email']; telefone = request.form['telefone']
    if not nome: flash('O nome do cliente é obrigatório.', 'danger'); return redirect(url_for('clientes'))
    if email and not EMAIL_REGEX.match(email):
        flash('Formato de e-mail inválido. Certifique-se de incluir "@" e ".".', 'danger'); return redirect(url_for('clientes'))
    db = get_db()
    if email:
        existente = db.execute('SELECT 1 FROM Clientes WHERE email = ? AND id_cliente != ?', (email, id)).fetchone()
        if existente: flash('Este e-mail já está sendo usado por outro cliente.', 'danger'); return redirect(url_for('clientes'))
    db.execute('UPDATE Clientes SET nome_completo = ?, email = ?, telefone = ? WHERE id_cliente = ?', (nome, email, telefone, id))
    db.commit()
    flash('Cliente atualizado com sucesso!', 'info'); return redirect(url_for('clientes'))

@app.route('/clientes/delete/<int:id>', methods=['POST'])
@login_required
def delete_cliente(id):
    db = get_db()
    venda = db.execute('SELECT 1 FROM Vendas WHERE id_cliente_fk = ?', (id,)).fetchone()
    if venda:
        flash('Não é possível excluir um cliente que já realizou compras.', 'danger')
    else:
        db.execute('DELETE FROM Clientes WHERE id_cliente = ?', (id,))
        db.commit()
        flash('Cliente excluído com sucesso.', 'success')
    return redirect(url_for('clientes'))

# --- ROTAS DE VENDAS (NOVO) ---

@app.route('/vendas')
@login_required
def vendas():
    db = get_db()
    
    # 1. Buscar Clientes
    db_clientes = db.execute('SELECT * FROM Clientes ORDER BY nome_completo').fetchall()
    
    # 2. Buscar Produtos (incluindo estoque)
    db_produtos = db.execute('SELECT id_produto, nome, preco, quantidade FROM Produtos').fetchall()
    # Converte para dict para podermos ordenar
    produtos_lista = [dict(row) for row in db_produtos]
    
    # 3. Ordenar Produtos (RF08)
    produtos_ordenados = insertion_sort(produtos_lista)
    
    # 4. Buscar Histórico de Vendas
    db_vendas = db.execute('''
        SELECT v.id_venda, c.nome_completo as nome_cliente, p.nome as nome_produto,
               v.quantidade_vendida, v.valor_total, v.data_venda
        FROM Vendas v
        JOIN Clientes c ON v.id_cliente_fk = c.id_cliente
        JOIN Produtos p ON v.id_produto_fk = p.id_produto
        ORDER BY v.data_venda DESC, v.id_venda DESC
    ''').fetchall()
    
    vendas_lista = []
    for row in db_vendas:
        venda_dict = dict(row)
        venda_dict['data_obj'] = datetime.strptime(venda_dict['data_venda'], '%Y-%m-%d')
        vendas_lista.append(venda_dict)
    
    return render_template('vendas.html',
                           clientes=db_clientes,
                           produtos=produtos_ordenados,
                           vendas=vendas_lista)

# (Resposta para a Pergunta 1a do questionário)
@app.route('/vendas/registrar', methods=['POST'])
@login_required
def registrar_venda():
    db = get_db()
    
    # 1. Coletar dados do formulário
    id_cliente = int(request.form['id_cliente'])
    id_produto = int(request.form['id_produto'])
    data_venda = request.form['data_venda']
    try:
        quantidade_vendida = int(request.form['quantidade'])
        if quantidade_vendida <= 0:
            flash('A quantidade deve ser pelo menos 1.', 'danger')
            return redirect(url_for('vendas'))
    except ValueError:
        flash('Quantidade inválida.', 'danger')
        return redirect(url_for('vendas'))
        
    # 2. Lógica de Negócio: Buscar produto e verificar estoque (RF09)
    # (Resposta para a Pergunta 1c do questionário - Passo 1: Leitura)
    produto = db.execute('SELECT * FROM Produtos WHERE id_produto = ?', (id_produto,)).fetchone()
    
    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('vendas'))
        
    estoque_atual = produto['quantidade']
    nome_produto = produto['nome']
    
    # 3. Validar Estoque (RF09 - Bloquear)
    # (Resposta para a Pergunta 1c do questionário - Passo 2: Verificação)
    if estoque_atual < quantidade_vendida:
        # (Resposta para a Pergunta 1b do questionário - Mensagem de erro)
        flash(f'Estoque insuficiente. Restam apenas {estoque_atual} unidades do produto {nome_produto}.', 'danger')
        return redirect(url_for('vendas'))
        
    # 4. Se tudo OK, efetivar a Venda (RF09 - Efetivar)
    # (Resposta para a Pergunta 1c do questionário - Passo 3: Escrita)
    try:
        # Calcular total
        valor_total = produto['preco'] * quantidade_vendida
        
        # Inserir na tabela de Vendas
        db.execute('''
            INSERT INTO Vendas (id_cliente_fk, id_produto_fk, quantidade_vendida, valor_total, data_venda)
            VALUES (?, ?, ?, ?, ?)
        ''', (id_cliente, id_produto, quantidade_vendida, valor_total, data_venda))
        
        # Atualizar (abater) o estoque na tabela Produtos
        novo_estoque = estoque_atual - quantidade_vendida
        db.execute('UPDATE Produtos SET quantidade = ? WHERE id_produto = ?', (novo_estoque, id_produto))
        
        # Confirmar as duas operações (INSERT e UPDATE)
        db.commit()
        
        # (RF10) Resumo da Venda
        flash(f'Venda registrada! {quantidade_vendida}x {nome_produto} por R$ {valor_total:.2f}. Novo estoque: {novo_estoque} unid.', 'success')
        
    except sqlite3.Error as e:
        db.rollback() # Desfaz qualquer mudança se algo der errado
        flash(f'Erro ao registrar a venda: {e}', 'danger')

    return redirect(url_for('vendas'))

@app.route('/vendas/delete/<int:id>', methods=['POST'])
@login_required
def delete_venda(id):
    # Nota: Esta função NÃO repõe o estoque, apenas remove o registro.
    db = get_db()
    db.execute('DELETE FROM Vendas WHERE id_venda = ?', (id,))
    db.commit()
    flash('Registro de venda excluído. O estoque não foi alterado.', 'info')
    return redirect(url_for('vendas'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)