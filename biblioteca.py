import os
import sys
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

# Usa /tmp no Vercel (read-only filesystem), senao usa o diretorio local
if os.environ.get('VERCEL'):
    app.config['DATABASE'] = '/tmp/biblioteca.db'
else:
    app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'biblioteca.db')


def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descricao TEXT
        );

        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            isbn TEXT,
            categoria_id INTEGER,
            imagem TEXT,
            status TEXT DEFAULT 'disponivel',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_devolucao TIMESTAMP,
            status TEXT DEFAULT 'ativo',
            FOREIGN KEY (livro_id) REFERENCES livros(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    ''')

    existing = cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    if existing > 0:
        db.commit()
        db.close()
        return

    cursor.executemany("INSERT INTO usuarios (nome, matricula, senha) VALUES (?, ?, ?)", [
        ('Administrador', 'admin', 'admin123'),
        ('Larissa', 'larissa', '1235'),
        ('João Silva', '2024001', 'senha123'),
        ('Maria Oliveira', '2024002', 'senha123'),
        ('Pedro Santos', '2024003', 'senha123'),
    ])

    cursor.executemany("INSERT INTO categorias (nome, descricao) VALUES (?, ?)", [
        ('Romance', 'Historias emocionantes e envolventes'),
        ('Ciencias', 'Natureza, fisica e descobertas'),
        ('Psicologia', 'Comportamento e mente humana'),
        ('Ficcao Cientifica', 'Futuro, tecnologia e universos'),
        ('Classicos', 'Obras que marcaram a historia'),
        ('Misterio', 'Enigmas e investigacoes'),
    ])

    cursor.executemany("INSERT INTO livros (titulo, autor, categoria_id, imagem, status) VALUES (?, ?, ?, ?, ?)", [
        ('Dom Casmurro', 'Machado de Assis', 5, 'DOM.webp', 'disponivel'),
        ('O Cortico', 'Aluisio Azevedo', 5, 'CAPA_3000px_O-CORTICO_.webp', 'emprestado'),
        ('Capitaes da Areia', 'Jorge Amado', 1, 'livros.svg', 'reservado'),
        ('Vidas Secas', 'Graciliano Ramos', 5, 'livros.svg', 'emprestado'),
        ('Memorias Postumas de Bras Cubas', 'Machado de Assis', 5, 'livros.svg', 'disponivel'),
        ('A Hora da Estrela', 'Clarice Lispector', 1, 'livros.svg', 'disponivel'),
        ('Grande Sertao: Veredas', 'Guimaraes Rosa', 5, 'livros.svg', 'disponivel'),
        ('1984', 'George Orwell', 4, 'livros.svg', 'disponivel'),
        ('O Pequeno Principe', 'Antoine de Saint-Exupery', 1, 'livros.svg', 'disponivel'),
        ('A Metamorfose', 'Franz Kafka', 5, 'livros.svg', 'disponivel'),
        ('Memorias de um Sargento de Milicias', 'Manuel Antonio de Almeida', 5, 'livros.svg', 'disponivel'),
        ('A Moreninha', 'Joaquim Manuel de Macedo', 1, 'livros.svg', 'disponivel'),
        ('Iracema', 'Jose de Alencar', 1, 'livros.svg', 'disponivel'),
        ('Senhora', 'Jose de Alencar', 1, 'livros.svg', 'disponivel'),
        ('Quincas Borba', 'Machado de Assis', 5, 'livros.svg', 'disponivel'),
    ])

    cursor.execute("""
        INSERT INTO emprestimos (livro_id, usuario_id, data_emprestimo, status)
        VALUES (2, 1, datetime('now', '-5 days'), 'ativo')
    """)
    cursor.execute("""
        INSERT INTO emprestimos (livro_id, usuario_id, data_emprestimo, status)
        VALUES (4, 2, datetime('now', '-3 days'), 'ativo')
    """)

    db.commit()
    db.close()


init_db()


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    matricula = data.get('matricula', '')
    senha = data.get('senha', '')

    db = get_db()
    user = db.execute(
        "SELECT * FROM usuarios WHERE matricula = ? AND senha = ?",
        (matricula, senha)
    ).fetchone()
    db.close()

    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'nome': user['nome'],
                'matricula': user['matricula']
            }
        })
    return jsonify({'success': False, 'message': 'Matricula ou senha invalidos'}), 401


@app.route('/api/livros', methods=['GET'])
def api_livros():
    db = get_db()
    livros = db.execute("""
        SELECT l.*, c.nome as categoria_nome
        FROM livros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        ORDER BY l.titulo
    """).fetchall()
    db.close()

    return jsonify([{
        'id': l['id'],
        'titulo': l['titulo'],
        'autor': l['autor'],
        'isbn': l['isbn'],
        'categoria_id': l['categoria_id'],
        'categoria': l['categoria_nome'],
        'imagem': l['imagem'],
        'status': l['status']
    } for l in livros])


@app.route('/api/livros/buscar', methods=['GET'])
def api_buscar_livros():
    query = request.args.get('q', '')
    db = get_db()
    livros = db.execute("""
        SELECT l.*, c.nome as categoria_nome
        FROM livros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        WHERE l.titulo LIKE ? OR l.autor LIKE ?
        ORDER BY l.titulo
    """, (f'%{query}%', f'%{query}%')).fetchall()
    db.close()

    return jsonify([{
        'id': l['id'],
        'titulo': l['titulo'],
        'autor': l['autor'],
        'isbn': l['isbn'],
        'categoria_id': l['categoria_id'],
        'categoria': l['categoria_nome'],
        'imagem': l['imagem'],
        'status': l['status']
    } for l in livros])


@app.route('/api/livros/<int:livro_id>', methods=['GET'])
def api_livro(livro_id):
    db = get_db()
    livro = db.execute("""
        SELECT l.*, c.nome as categoria_nome
        FROM livros l
        LEFT JOIN categorias c ON l.categoria_id = c.id
        WHERE l.id = ?
    """, (livro_id,)).fetchone()

    if not livro:
        db.close()
        return jsonify({'error': 'Livro nao encontrado'}), 404

    emprestimo = db.execute("""
        SELECT e.*, u.nome as usuario_nome
        FROM emprestimos e
        JOIN usuarios u ON e.usuario_id = u.id
        WHERE e.livro_id = ? AND e.status = 'ativo'
    """, (livro_id,)).fetchone()
    db.close()

    result = {
        'id': livro['id'],
        'titulo': livro['titulo'],
        'autor': livro['autor'],
        'isbn': livro['isbn'],
        'categoria_id': livro['categoria_id'],
        'categoria': livro['categoria_nome'],
        'imagem': livro['imagem'],
        'status': livro['status']
    }
    if emprestimo:
        result['emprestimo'] = {
            'usuario': emprestimo['usuario_nome'],
            'data_emprestimo': emprestimo['data_emprestimo']
        }

    return jsonify(result)


@app.route('/api/emprestar', methods=['POST'])
def api_emprestar():
    data = request.get_json()
    livro_id = data.get('livro_id')
    usuario_id = data.get('usuario_id')

    if not livro_id or not usuario_id:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400

    db = get_db()
    livro = db.execute("SELECT * FROM livros WHERE id = ?", (livro_id,)).fetchone()

    if not livro:
        db.close()
        return jsonify({'success': False, 'message': 'Livro nao encontrado'}), 404

    if livro['status'] != 'disponivel':
        db.close()
        return jsonify({'success': False, 'message': 'Livro nao esta disponivel'}), 400

    db.execute("UPDATE livros SET status = 'emprestado' WHERE id = ?", (livro_id,))
    db.execute("""
        INSERT INTO emprestimos (livro_id, usuario_id, data_emprestimo, status)
        VALUES (?, ?, datetime('now', '-3 hours'), 'ativo')
    """, (livro_id, usuario_id))
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': 'Livro emprestado com sucesso!'})


@app.route('/api/devolver', methods=['POST'])
def api_devolver():
    data = request.get_json()
    livro_id = data.get('livro_id')

    if not livro_id:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400

    db = get_db()
    emprestimo = db.execute("""
        SELECT * FROM emprestimos
        WHERE livro_id = ? AND status = 'ativo'
    """, (livro_id,)).fetchone()

    if not emprestimo:
        db.close()
        return jsonify({'success': False, 'message': 'Nenhum emprestimo ativo encontrado'}), 404

    db.execute("UPDATE livros SET status = 'disponivel' WHERE id = ?", (livro_id,))
    db.execute("""
        UPDATE emprestimos
        SET status = 'devolvido', data_devolucao = datetime('now', '-3 hours')
        WHERE id = ?
    """, (emprestimo['id'],))
    db.commit()
    db.close()

    return jsonify({'success': True, 'message': 'Livro devolvido com sucesso!'})


@app.route('/api/reservar', methods=['POST'])
def api_reservar():
    data = request.get_json()
    livro_id = data.get('livro_id')
    usuario_id = data.get('usuario_id')
    if not livro_id or not usuario_id:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    db = get_db()
    livro = db.execute("SELECT * FROM livros WHERE id = ?", (livro_id,)).fetchone()
    if not livro:
        db.close()
        return jsonify({'success': False, 'message': 'Livro nao encontrado'}), 404
    if livro['status'] != 'disponivel':
        db.close()
        return jsonify({'success': False, 'message': 'Livro nao esta disponivel para reserva'}), 400
    db.execute("UPDATE livros SET status = 'reservado' WHERE id = ?", (livro_id,))
    db.execute("""
        INSERT INTO emprestimos (livro_id, usuario_id, data_emprestimo, status)
        VALUES (?, ?, datetime('now', '-3 hours'), 'reservado')
    """, (livro_id, usuario_id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Livro reservado com sucesso!'})


@app.route('/api/cancelar-reserva', methods=['POST'])
def api_cancelar_reserva():
    data = request.get_json()
    livro_id = data.get('livro_id')
    if not livro_id:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    db = get_db()
    reserva = db.execute(
        "SELECT * FROM emprestimos WHERE livro_id = ? AND status = 'reservado'",
        (livro_id,)
    ).fetchone()
    if not reserva:
        db.close()
        return jsonify({'success': False, 'message': 'Reserva nao encontrada'}), 404
    db.execute("UPDATE livros SET status = 'disponivel' WHERE id = ?", (livro_id,))
    db.execute("UPDATE emprestimos SET status = 'cancelado' WHERE id = ?", (reserva['id'],))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Reserva cancelada com sucesso!'})


@app.route('/api/reservas', methods=['GET'])
def api_reservas():
    db = get_db()
    reservas = db.execute("""
        SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
               u.nome as usuario_nome, u.matricula
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN usuarios u ON e.usuario_id = u.id
        WHERE e.status = 'reservado'
        ORDER BY e.data_emprestimo DESC
    """).fetchall()
    db.close()
    return jsonify([{
        'id': e['id'],
        'livro_id': e['livro_id'],
        'usuario_id': e['usuario_id'],
        'livro': e['livro_titulo'],
        'autor': e['livro_autor'],
        'usuario': e['usuario_nome'],
        'matricula': e['matricula'],
        'data_reserva': e['data_emprestimo']
    } for e in reservas])


@app.route('/api/usuarios/<int:usuario_id>/senha', methods=['PUT'])
def api_alterar_senha(usuario_id):
    data = request.get_json()
    senha_atual = data.get('senha_atual')
    nova_senha = data.get('nova_senha')
    if not senha_atual or not nova_senha:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    db = get_db()
    user = db.execute("SELECT * FROM usuarios WHERE id = ? AND senha = ?", (usuario_id, senha_atual)).fetchone()
    if not user:
        db.close()
        return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 400
    db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha, usuario_id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})


@app.route('/api/emprestimos', methods=['GET'])
def api_emprestimos():
    db = get_db()
    emprestimos = db.execute("""
        SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
               u.nome as usuario_nome, u.matricula
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN usuarios u ON e.usuario_id = u.id
        ORDER BY e.data_emprestimo DESC
    """).fetchall()
    db.close()

    return jsonify([{
        'id': e['id'],
        'livro': e['livro_titulo'],
        'autor': e['livro_autor'],
        'usuario': e['usuario_nome'],
        'matricula': e['matricula'],
        'data_emprestimo': e['data_emprestimo'],
        'data_devolucao': e['data_devolucao'],
        'status': e['status']
    } for e in emprestimos])


@app.route('/api/emprestimos/ativos', methods=['GET'])
def api_emprestimos_ativos():
    db = get_db()
    emprestimos = db.execute("""
        SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
               u.nome as usuario_nome, u.matricula,
               CAST(julianday('now') - julianday(e.data_emprestimo) AS INTEGER) as dias_emprestado
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN usuarios u ON e.usuario_id = u.id
        WHERE e.status = 'ativo'
        ORDER BY e.data_emprestimo
    """).fetchall()
    db.close()

    return jsonify([{
        'id': e['id'],
        'livro': e['livro_titulo'],
        'autor': e['livro_autor'],
        'usuario': e['usuario_nome'],
        'matricula': e['matricula'],
        'data_emprestimo': e['data_emprestimo'],
        'dias_emprestado': e['dias_emprestado'] or 0,
        'atrasado': (e['dias_emprestado'] or 0) > 14
    } for e in emprestimos])


@app.route('/api/usuarios/<int:usuario_id>/emprestimos', methods=['GET'])
def api_emprestimos_usuario(usuario_id):
    db = get_db()
    rows = db.execute("""
        SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
               CAST(julianday('now') - julianday(e.data_emprestimo) AS INTEGER) as dias
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        WHERE e.usuario_id = ? AND e.status IN ('ativo', 'reservado')
        ORDER BY e.data_emprestimo DESC
    """, (usuario_id,)).fetchall()
    db.close()
    return jsonify([{
        'id': r['id'],
        'livro': r['livro_titulo'],
        'autor': r['livro_autor'],
        'tipo': r['status'],
        'data': r['data_emprestimo'],
        'dias': r['dias'] or 0
    } for r in rows])


@app.route('/api/usuarios', methods=['GET'])
def api_usuarios():
    db = get_db()
    usuarios = db.execute("""
        SELECT u.*,
               (SELECT COUNT(*) FROM emprestimos e WHERE e.usuario_id = u.id AND e.status = 'ativo') as livros_emprestados
        FROM usuarios u
        ORDER BY u.nome
    """).fetchall()
    db.close()

    return jsonify([{
        'id': u['id'],
        'nome': u['nome'],
        'matricula': u['matricula'],
        'email': u['email'],
        'livros_emprestados': u['livros_emprestados'],
        'created_at': u['created_at']
    } for u in usuarios])


@app.route('/api/categorias', methods=['GET'])
def api_categorias():
    db = get_db()
    categorias = db.execute("""
        SELECT c.*, (SELECT COUNT(*) FROM livros l WHERE l.categoria_id = c.id) as total_livros
        FROM categorias c
        ORDER BY c.nome
    """).fetchall()
    db.close()

    return jsonify([{
        'id': c['id'],
        'nome': c['nome'],
        'descricao': c['descricao'],
        'total_livros': c['total_livros']
    } for c in categorias])


@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    db = get_db()
    stats = db.execute("""
        SELECT
            (SELECT COUNT(*) FROM livros) as total_livros,
            (SELECT COUNT(*) FROM livros WHERE status = 'disponivel') as disponiveis,
            (SELECT COUNT(*) FROM livros WHERE status = 'emprestado') as emprestados,
            (SELECT COUNT(*) FROM livros WHERE status = 'reservado') as reservados,
            (SELECT COUNT(*) FROM usuarios) as total_usuarios,
            (SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo') as emprestimos_ativos,
            (SELECT COUNT(*) FROM categorias) as total_categorias
    """).fetchone()
    db.close()

    return jsonify({
        'total_livros': stats['total_livros'],
        'disponiveis': stats['disponiveis'],
        'emprestados': stats['emprestados'],
        'reservados': stats['reservados'],
        'total_usuarios': stats['total_usuarios'],
        'emprestimos_ativos': stats['emprestimos_ativos'],
        'total_categorias': stats['total_categorias']
    })


@app.route('/api/livros', methods=['POST'])
def api_criar_livro():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO livros (titulo, autor, isbn, categoria_id, imagem, status)
        VALUES (?, ?, ?, ?, ?, 'disponivel')
    """, (data.get('titulo'), data.get('autor'), data.get('isbn'),
          data.get('categoria_id'), data.get('imagem', 'livros.svg')))
    db.commit()
    livro_id = cursor.lastrowid
    db.close()
    return jsonify({'success': True, 'id': livro_id, 'message': 'Livro cadastrado com sucesso!'}), 201


@app.route('/api/livros/<int:livro_id>', methods=['PUT'])
def api_atualizar_livro(livro_id):
    data = request.get_json()
    db = get_db()
    db.execute("""
        UPDATE livros SET titulo=?, autor=?, isbn=?, categoria_id=?, imagem=?
        WHERE id=?
    """, (data.get('titulo'), data.get('autor'), data.get('isbn'),
          data.get('categoria_id'), data.get('imagem'), livro_id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Livro atualizado com sucesso!'})


@app.route('/api/livros/<int:livro_id>', methods=['DELETE'])
def api_deletar_livro(livro_id):
    db = get_db()
    ativo = db.execute(
        "SELECT id FROM emprestimos WHERE livro_id=? AND status='ativo'",
        (livro_id,)
    ).fetchone()
    if ativo:
        db.close()
        return jsonify({'success': False, 'message': 'Livro com emprestimo ativo nao pode ser excluido'}), 400
    db.execute("DELETE FROM livros WHERE id=?", (livro_id,))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Livro excluido com sucesso!'})


@app.route('/api/usuarios', methods=['POST'])
def api_criar_usuario():
    data = request.get_json()
    db = get_db()
    try:
        db.execute("INSERT INTO usuarios (nome, matricula, senha, email) VALUES (?, ?, ?, ?)",
                   (data.get('nome'), data.get('matricula'), data.get('senha'), data.get('email')))
        db.commit()
        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.close()
        return jsonify({'success': True, 'id': user_id, 'message': 'Usuario cadastrado com sucesso!'}), 201
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'success': False, 'message': 'Matricula ja existe'}), 400


@app.route('/api/usuarios/<int:usuario_id>', methods=['PUT'])
def api_atualizar_usuario(usuario_id):
    data = request.get_json()
    db = get_db()
    senha = data.get('senha')
    if senha:
        db.execute("UPDATE usuarios SET nome=?, matricula=?, senha=?, email=? WHERE id=?",
                   (data.get('nome'), data.get('matricula'), senha, data.get('email'), usuario_id))
    else:
        db.execute("UPDATE usuarios SET nome=?, matricula=?, email=? WHERE id=?",
                   (data.get('nome'), data.get('matricula'), data.get('email'), usuario_id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Usuario atualizado com sucesso!'})


@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
def api_deletar_usuario(usuario_id):
    db = get_db()
    ativo = db.execute(
        "SELECT id FROM emprestimos WHERE usuario_id=? AND status='ativo'",
        (usuario_id,)
    ).fetchone()
    if ativo:
        db.close()
        return jsonify({'success': False, 'message': 'Usuario com emprestimo ativo nao pode ser excluido'}), 400
    db.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Usuario excluido com sucesso!'})


@app.route('/api/categorias', methods=['POST'])
def api_criar_categoria():
    data = request.get_json()
    db = get_db()
    try:
        db.execute("INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
                   (data.get('nome'), data.get('descricao')))
        db.commit()
        cat_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.close()
        return jsonify({'success': True, 'id': cat_id, 'message': 'Categoria cadastrada com sucesso!'}), 201
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'success': False, 'message': 'Categoria ja existe'}), 400


@app.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
def api_atualizar_categoria(categoria_id):
    data = request.get_json()
    db = get_db()
    db.execute("UPDATE categorias SET nome=?, descricao=? WHERE id=?",
               (data.get('nome'), data.get('descricao'), categoria_id))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Categoria atualizada com sucesso!'})


@app.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
def api_deletar_categoria(categoria_id):
    db = get_db()
    livros = db.execute("SELECT id FROM livros WHERE categoria_id=?", (categoria_id,)).fetchall()
    if livros:
        db.close()
        return jsonify({'success': False, 'message': f'Categoria possui {len(livros)} livro(s) vinculado(s)'}), 400
    db.execute("DELETE FROM categorias WHERE id=?", (categoria_id,))
    db.commit()
    db.close()
    return jsonify({'success': True, 'message': 'Categoria excluida com sucesso!'})


@app.route('/api/atrasados', methods=['GET'])
def api_atrasados():
    db = get_db()
    atrasados = db.execute("""
        SELECT e.*, l.titulo as livro_titulo, l.autor as livro_autor,
               u.nome as usuario_nome, u.matricula,
               CAST(julianday('now') - julianday(e.data_emprestimo) - 14 AS INTEGER) as dias_atraso
        FROM emprestimos e
        JOIN livros l ON e.livro_id = l.id
        JOIN usuarios u ON e.usuario_id = u.id
        WHERE e.status = 'ativo' AND julianday('now') - julianday(e.data_emprestimo) > 14
        ORDER BY dias_atraso DESC
    """).fetchall()
    db.close()

    return jsonify([{
        'id': e['id'],
        'livro': e['livro_titulo'],
        'autor': e['livro_autor'],
        'usuario': e['usuario_nome'],
        'matricula': e['matricula'],
        'data_emprestimo': e['data_emprestimo'],
        'dias_atraso': e['dias_atraso']
    } for e in atrasados])


@app.route('/api/resetar', methods=['POST'])
def api_resetar():
    db = get_db()
    cursor = db.cursor()
    cursor.executescript("""
        DROP TABLE IF EXISTS emprestimos;
        DROP TABLE IF EXISTS livros;
        DROP TABLE IF EXISTS categorias;
        DROP TABLE IF EXISTS usuarios;
    """)
    db.commit()
    db.close()
    import os as _os
    _os.remove(app.config['DATABASE'])
    init_db()
    return jsonify({'success': True, 'message': 'Banco resetado com sucesso!'})


@app.route('/')
def serve_index():
    return send_from_directory('.', 'bibliotecaa.html')


@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('.', path)):
        return send_from_directory('.', path)
    return send_from_directory('.', 'bibliotecaa.html'), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
