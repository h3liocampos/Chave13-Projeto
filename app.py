from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'troque-esta-chave-no-.env')

db_config = {
    'host':     os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}


def get_db_connection():

    return mysql.connector.connect(**db_config)


def tratar_erro_mysql(e):
    """Converte erros do MySQL em mensagens amigáveis."""
    codigo = e.errno
    mensagens = {
        1062: "Registro duplicado: já existe um cadastro com esse CPF, e-mail, celular ou CNPJ.",
        1452: "Registro relacionado não encontrado: verifique se o ID informado existe na tabela correspondente.",
        1451: "Não é possível excluir: este registro está sendo usado em outro cadastro (ex: funcionário com ASO vinculado).",
        1048: "Campo obrigatório não preenchido: verifique se todos os campos foram enviados corretamente.",
        1406: "Valor muito longo para um dos campos. Verifique o tamanho dos dados enviados.",
        1366: "Tipo de dado inválido: um dos campos recebeu um valor no formato incorreto.",
        1146: "Tabela não encontrada no banco de dados. Verifique a configuração do sistema.",
        2003: "Não foi possível conectar ao banco de dados. Verifique se o servidor está ativo.",
    }
    mensagem = mensagens.get(codigo, f"Erro interno no banco de dados. (código {codigo})")
    status = 409 if codigo in (1062, 1451, 1452) else 500
    return jsonify({"erro": mensagem}), status


class Estabelecimento:
    def __init__(self, nome, cnpj, email, telefone, dono_id, id=None):
        self.nome = nome
        self.cnpj = cnpj
        self.email = email
        self.telefone = telefone
        self.dono_id = dono_id
        self.id = id


class Funcionario:
    def __init__(self, usuario_id, estabelecimento_id, id=None):
        self.usuario_id = usuario_id
        self.estabelecimento_id = estabelecimento_id
        self.id = id


class Usuario:
    def __init__(self, nome, email, senha, telefone, perfil, id=None):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.perfil = perfil
        self.id = id


class Sessao:
    def __init__(self, sessao, usuario_id, id=None):
        self.sessao = sessao
        self.usuario_id = usuario_id
        self.id = id


class Manutencao:
    def __init__(self, cliente_id, carro_id, estabelecimento_id, funcionario_id,
                 servico, preco_servico, pagamento, id=None):
        self.cliente_id = cliente_id
        self.carro_id = carro_id
        self.estabelecimento_id = estabelecimento_id
        self.funcionario_id = funcionario_id
        self.servico = servico
        self.preco_servico = preco_servico
        self.pagamento = pagamento
        self.id = id


class Carro:
    def __init__(self, usuario_id, placa, modelo, marca, ano, chassi, id=None):
        self.usuario_id = usuario_id
        self.placa = placa
        self.modelo = modelo
        self.marca = marca
        self.ano = ano
        self.chassi = chassi
        self.id = id


class Peca:
    def __init__(self, manutencao_id, nome, descricao, preco_unitario, id=None):
        self.manutencao_id = manutencao_id
        self.nome = nome
        self.descricao = descricao
        self.preco_unitario = preco_unitario
        self.id = id


class Endereco:
    def __init__(self, estabelecimento_id, cep, numero, logradouro, bairro,
                 cidade, estado, pais, complemento, observacao, id=None):
        self.estabelecimento_id = estabelecimento_id
        self.cep = cep
        self.numero = numero
        self.logradouro = logradouro
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.pais = pais
        self.complemento = complemento
        self.observacao = observacao
        self.id = id


@app.route('/api/estabelecimentos', methods=['POST'])
def cadastrar_estabelecimento():
    try:
        dados = request.get_json()
        estab = Estabelecimento(
            dados['nome'], dados['cnpj'], dados['email'], dados['telefone'], dados['dono_id'],
        )

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO estabelecimentos
                (nome, cnpj, email, telefone, dono_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            estab.nome, estab.cnpj, estab.email, estab.telefone, estab.dono_id
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({"mensagem": "Estabelecimento cadastrado.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/estabelecimentos', methods=['GET'])
def consultar_estabelecimentos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estabelecimentos")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/estabelecimentos/<int:id>', methods=['GET'])
def consultar_estabelecimento(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estabelecimentos WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Estabelecimento não encontrado."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/estabelecimentos/<int:id>', methods=['PUT'])
def atualizar_estabelecimento(id):
    try:
        dados = request.get_json()
        estab = Estabelecimento(
            dados['nome'], dados['cnpj'], dados['email'], dados['telefone'],
            dados['dono_id'], id,
        )

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE estabelecimentos
            SET nome = %s, cnpj = %s, email = %s, telefone = %s, dono_id = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            estab.nome, estab.cnpj, estab.email, estab.telefone, estab.dono_id, estab.id
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Estabelecimento não encontrado."}), 404
        return jsonify({"mensagem": "Estabelecimento atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/estabelecimentos/<int:id>', methods=['DELETE'])
def deletar_estabelecimento(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estabelecimentos WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Estabelecimento não encontrado."}), 404
        return jsonify({"mensagem": "Estabelecimento deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Funcionarios ─────────────────────────────────────────────────

@app.route('/api/funcionarios', methods=['POST'])
def cadastrar_funcionario():
    try:
        dados = request.get_json()
        func = Funcionario(
            dados['usuario_id'], dados['estabelecimento_id'],
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO funcionarios
                (usuario_id, estabelecimento_id)
            VALUES (%s, %s)
        """
        cursor.execute(sql, (
            func.usuario_id, func.estabelecimento_id,
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Funcionário cadastrado.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/funcionarios', methods=['GET'])
def consultar_funcionarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM funcionarios")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/funcionarios/<int:id>', methods=['GET'])
def consultar_funcionario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM funcionarios WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Funcionário não encontrado."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/funcionarios/<int:id>', methods=['PUT'])
def atualizar_funcionario(id):
    try:
        dados = request.get_json()
        func = Funcionario(
            dados['usuario_id'], dados['estabelecimento_id'], id,
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE funcionarios
            SET usuario_id = %s, estabelecimento_id = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            func.usuario_id, func.estabelecimento_id, func.id
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Funcionário atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/funcionarios/<int:id>', methods=['DELETE'])
def deletar_funcionario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM funcionarios WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Funcionário não encontrado."}), 404
        return jsonify({"mensagem": "Funcionário deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Usuarios ─────────────────────────────────────────────────────

@app.route('/api/usuarios', methods=['POST'])
def cadastrar_usuario():
    try:
        dados = request.get_json()
        usuar = Usuario(
            dados['nome'], dados['email'], dados['senha'], dados['telefone'], dados['perfil']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios
                (nome, email, senha, telefone, perfil)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            usuar.nome, usuar.email, usuar.senha, usuar.telefone, usuar.perfil
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Usuário cadastrado.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/usuarios', methods=['GET'])
def consultar_usuarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, telefone, perfil FROM usuarios")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/usuarios/<int:id>', methods=['GET'])
def consultar_usuario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email, telefone, perfil FROM usuarios WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    try:
        dados = request.get_json()
        usuar = Usuario(
            dados['nome'], dados['email'], dados['senha'], dados['telefone'], dados['perfil'], id,
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE usuarios
            SET nome = %s, email = %s, senha = %s, telefone = %s, perfil = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            usuar.nome, usuar.email, usuar.senha, usuar.telefone, usuar.perfil, usuar.id,
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify({"mensagem": "Usuário atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Usuário não encontrado."}), 404
        return jsonify({"mensagem": "Usuário deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Sessoes ───────────────────────────────────────────────────────

@app.route('/api/sessoes', methods=['POST'])
def cadastrar_sessao():
    try:
        dados = request.get_json()
        sess = Sessao(
            dados['sessao'], dados['usuario_id']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO sessoes
                (sessao, usuario_id)
            VALUES (%s, %s)
        """
        cursor.execute(sql, (
            sess.sessao, sess.usuario_id
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Sessão cadastrada.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/sessoes', methods=['GET'])
def consultar_sessoes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sessoes")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/sessoes/<int:id>', methods=['GET'])
def consultar_sessao(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sessoes WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Sessão não encontrada."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/sessoes/<int:id>', methods=['PUT'])
def atualizar_sessao(id):
    try:
        dados = request.get_json()
        sess = Sessao(
            dados['sessao'], dados['usuario_id'], id,
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE sessoes
            SET sessao = %s, usuario_id = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            sess.sessao, sess.usuario_id, sess.id,
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Sessão não encontrada."}), 404
        return jsonify({"mensagem": "Sessão atualizada."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/sessoes/<int:id>', methods=['DELETE'])
def deletar_sessao(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessoes WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Sessão não encontrada."}), 404
        return jsonify({"mensagem": "Sessão deletada."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Manutencoes ───────────────────────────────────────────────────

@app.route('/api/manutencoes', methods=['POST'])
def cadastrar_manutencao():
    try:
        dados = request.get_json()
        manut = Manutencao(
            dados['cliente_id'], dados['carro_id'], dados['estabelecimento_id'],
            dados['funcionario_id'], dados['servico'], dados['preco_servico'], dados['pagamento']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO manutencoes
                (cliente_id, carro_id, estabelecimento_id, funcionario_id, servico, preco_servico, pagamento)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            manut.cliente_id, manut.carro_id, manut.estabelecimento_id,
            manut.funcionario_id, manut.servico, manut.preco_servico, manut.pagamento
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Manutenção cadastrada.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/manutencoes', methods=['GET'])
def consultar_manutencoes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM manutencoes")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/manutencoes/<int:id>', methods=['GET'])
def consultar_manutencao(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM manutencoes WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Manutenção não encontrada."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/manutencoes/<int:id>', methods=['PUT'])
def atualizar_manutencao(id):
    try:
        dados = request.get_json()
        manut = Manutencao(
            dados['cliente_id'], dados['carro_id'], dados['estabelecimento_id'],
            dados['funcionario_id'], dados['servico'], dados['preco_servico'],
            dados['pagamento'], id,
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE manutencoes
            SET cliente_id = %s, carro_id = %s, estabelecimento_id = %s,
                funcionario_id = %s, servico = %s, preco_servico = %s, pagamento = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            manut.cliente_id, manut.carro_id, manut.estabelecimento_id,
            manut.funcionario_id, manut.servico, manut.preco_servico,
            manut.pagamento, manut.id,
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Manutenção não encontrada."}), 404
        return jsonify({"mensagem": "Manutenção atualizada."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/manutencoes/<int:id>', methods=['DELETE'])
def deletar_manutencao(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM manutencoes WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Manutenção não encontrada."}), 404
        return jsonify({"mensagem": "Manutenção deletada."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Carros ────────────────────────────────────────────────────────

@app.route('/api/carros', methods=['POST'])
def cadastrar_carro():
    try:
        dados = request.get_json()
        carr = Carro(
            dados['usuario_id'], dados['placa'], dados['modelo'], dados['marca'],
            dados['ano'], dados['chassi']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO carros
                (usuario_id, placa, modelo, marca, ano, chassi)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            carr.usuario_id, carr.placa, carr.modelo, carr.marca, carr.ano, carr.chassi
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Carro cadastrado.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/carros', methods=['GET'])
def consultar_carros():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM carros")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/carros/<int:id>', methods=['GET'])
def consultar_carro(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM carros WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Carro não encontrado."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/carros/<int:id>', methods=['PUT'])
def atualizar_carro(id):
    try:
        dados = request.get_json()
        carr = Carro(
            dados['usuario_id'], dados['placa'], dados['modelo'], dados['marca'],
            dados['ano'], dados['chassi'], id
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE carros
            SET usuario_id = %s, placa = %s, modelo = %s, marca = %s, ano = %s, chassi = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            carr.usuario_id, carr.placa, carr.modelo, carr.marca, carr.ano, carr.chassi, carr.id,
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Carro não encontrado."}), 404
        return jsonify({"mensagem": "Carro atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/carros/<int:id>', methods=['DELETE'])
def deletar_carro(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carros WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Carro não encontrado."}), 404
        return jsonify({"mensagem": "Carro deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Pecas ─────────────────────────────────────────────────────────

@app.route('/api/pecas', methods=['POST'])
def cadastrar_peca():
    try:
        dados = request.get_json()
        pec = Peca(
            dados['manutencao_id'], dados['nome'], dados['descricao'], dados['preco_unitario']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO pecas
                (manutencao_id, nome, descricao, preco_unitario)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (
            pec.manutencao_id, pec.nome, pec.descricao, pec.preco_unitario
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Peça cadastrada.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/pecas', methods=['GET'])
def consultar_pecas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pecas")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/pecas/<int:id>', methods=['GET'])
def consultar_peca(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pecas WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Peça não encontrada."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/pecas/<int:id>', methods=['PUT'])
def atualizar_peca(id):
    try:
        dados = request.get_json()
        pec = Peca(
            dados['manutencao_id'], dados['nome'], dados['descricao'], dados['preco_unitario'], id,
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE pecas
            SET manutencao_id = %s, nome = %s, descricao = %s, preco_unitario = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            pec.manutencao_id, pec.nome, pec.descricao, pec.preco_unitario, pec.id
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Peça não encontrada."}), 404
        return jsonify({"mensagem": "Peça atualizada."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/pecas/<int:id>', methods=['DELETE'])
def deletar_peca(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pecas WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Peça não encontrada."}), 404
        return jsonify({"mensagem": "Peça deletada."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


# ── ROTAS – Enderecos ─────────────────────────────────────────────────────

@app.route('/api/enderecos', methods=['POST'])
def cadastrar_endereco():
    try:
        dados = request.get_json()
        ender = Endereco(
            dados['estabelecimento_id'], dados['cep'], dados['numero'], dados['logradouro'],
            dados['bairro'], dados['cidade'], dados['estado'], dados['pais'], dados['complemento'], dados['observacao']
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO enderecos
                (estabelecimento_id, cep, numero, logradouro, bairro, cidade, estado, pais, complemento, observacao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            ender.estabelecimento_id, ender.cep, ender.numero, ender.logradouro,
            ender.bairro, ender.cidade, ender.estado, ender.pais, ender.complemento, ender.observacao
        ))
        conn.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Endereço cadastrado.", "id": novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/enderecos', methods=['GET'])
def consultar_enderecos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM enderecos")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/enderecos/<int:id>', methods=['GET'])
def consultar_endereco(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM enderecos WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        if resultado is None:
            return jsonify({"erro": "Endereço não encontrado."}), 404
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/enderecos/<int:id>', methods=['PUT'])
def atualizar_endereco(id):
    try:
        dados = request.get_json()
        ender = Endereco(
            dados['estabelecimento_id'], dados['cep'], dados['numero'], dados['logradouro'],
            dados['bairro'], dados['cidade'], dados['estado'], dados['pais'], dados['complemento'], dados['observacao'], id
        )
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE enderecos
            SET estabelecimento_id = %s, cep = %s, numero = %s, logradouro = %s,
                bairro = %s, cidade = %s, estado = %s, pais = %s, complemento = %s, observacao = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            ender.estabelecimento_id, ender.cep, ender.numero, ender.logradouro,
            ender.bairro, ender.cidade, ender.estado, ender.pais, ender.complemento, ender.observacao, ender.id
        ))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Endereço não encontrado."}), 404
        return jsonify({"mensagem": "Endereço atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


@app.route('/api/enderecos/<int:id>', methods=['DELETE'])
def deletar_endereco(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM enderecos WHERE id = %s", (id,))
        conn.commit()
        linhas = cursor.rowcount
        cursor.close()
        conn.close()

        if linhas == 0:
            return jsonify({"erro": "Endereço não encontrado."}), 404
        return jsonify({"mensagem": "Endereço deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


if __name__ == '__main__':
    app.run(debug=True)
