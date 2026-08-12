from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, Response
import mysql.connectorfrom
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

app.secret_key = "senha_secreta_chave13"

db_config = {
    'host':     os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}

def conectar():
    return mysql.connector.connect(**db_config)
 

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
    status   = 409 if codigo in (1062, 1451, 1452) else 500
    return jsonify({"erro": mensagem}), status


class estabelecimentos: 
    def __init__(self, id, nome, cnpj, email, telefone, dono_id):
        self.id = id
        self.nome = nome
        self.cnpj = cnpj
        self.email = email
        self.telefone = telefone
        self.dono_id = dono_id

class funcionarios:
    def __init__ (self, id, usuario_id, estabelecimento_id):
        self.id = id
        self.usuario_id = usuario_id
        self.estabelecimento_id = estabelecimento_id

class usuarios:
    def __init__(self, id, nome, email, senha, telefone, perfil):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.perfil = perfil

class sessoes:
    def __init__(self, id, sessao, usuario_id):
        self.id = id
        self.sessao = sessao
        self.usuario = usuario_id

@app.route('/api/estabelecimento', methods=['POST'])
def cadastrar_estabelecimentos():
    try:
        dados = request.get_json()
        estab = estabelecimentos(
            dados['nome'], dados['cnpj'], dados['email'], dados['telefone'], dados['dono_id'],
        )

        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO estabelecimentos
                (nome, cnpj, email, telefone, dono_id)
            VALUES (%s,%s,%s,%s,%s)
        """
        cursor.execute(sql,(
            estab.nome, estab.cnpj, estab.email, estab.telefone, estab.dono_id
        ))

        conn.commit()

        novo_id = cursor.lastrowid

        cursor.close()

        conn.close()

        return jsonify({"mensagem": "Estabelecimento cadastrado.", "id": 
        novo_id}), 201

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400

    
@app.route('/api/estabelecimento', methods=['GET'])
def consultar_estabelecimentos():
    try:
        conn  = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM estabelecimentos")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)


@app.route('/api/estabelecimento', methods=['PUT'])
def atualizar_estabelecimento():
    try:
        dados = request.get_json()
        estab = estabelecimentos(
            dados['nome'], dados['cnpj'], dados['email'], dados['telefone'],
            dados['dono_id'],
        )

        conn   = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE estabelecimentos
            SET nome = %s, cnpj = %s, email = %s, telefone = %s,
                dono_id = %s
            WHERE id_funcionarios = %s
        """
        cursor.execute(sql, (
            estab.nome, estab.cnpj, estab.email, estab.telefone, estab.dono_id,
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Estabelecimento atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400

@app.route('/api/estabelecimentos', methods=['DELETE'])
def deletar_estabelecimentos():

    try:
        dados  = request.get_json()
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM estabelecimentos WHERE id = %s",
            (dados['id'],),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Estabelecimento deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400


# ── ROTAS – Funcionarios ─────────────────────────────────────────────────────────────
@app.route('/api/funcionarios', methods=['POST'])
def cadastrar_funcionarios():
    try:
        dados = request.get_json()
        func  = funcionarios(
            dados['usuario_id'], dados['estabelecimento_id'],  
        )
        conn   = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO funcionarios
                (usuario_id, estabelecimento_id)
            VALUES (%s,%s)
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
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM funcionarios")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)

@app.route('/api/funcionarios', methods=['PUT'])
def atualizar_funcionarios():
    try:
        dados = request.get_json()
        func  = funcionarios(
            dados['id'], dados['usuario_id'], dados['estabelecimento_id'],
        )
        conn   = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE funcionarios
            SET usuario_id = %s, estabelecimento_id = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            func.usuario_id, func.estabelecimento_id,
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Funcionário atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400

@app.route('/api/funcionarios', methods=['DELETE'])
def deletar_funcionarios():
    try:
        dados  = request.get_json()
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM funcionarios WHERE id = %s",
            (dados['id'],),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Funcionário deletado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400

#     USUARIOS----------------------------

@app.route('/api/usuarios', methods=['POST'])
def cadastrar_usuarios():
    try:
        dados = request.get_json()
        usuar  = usuarios(
            dados['nome'], dados['email'], dados['senha'], dados['telefone'], dados['perfil'] 
        )
        conn   = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO usuarios
                (nome, email, senha, telefone, perfil)
            VALUES (%s,%s, %s,%s, %s)
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
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(resultado), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)

@app.route('/api/usuarios', methods=['PUT'])
def atualizar_usuarios():
    try:
        dados = request.get_json()
        usuar  = usuarios(
            dados['id'], dados['nome'], dados['email'], dados['senha'], dados['telefone'], dados['perfil']
        )
        conn   = get_db_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE usuarios
            SET nome = %s, email = %s, senha = %s, telefone = %s, perfil = %s,
            WHERE id = %s
        """
        cursor.execute(sql, (
            usuar.id, ,
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"mensagem": "Funcionário atualizado."}), 200

    except mysql.connector.Error as e:
        return tratar_erro_mysql(e)
    except KeyError as e:
        return jsonify({"erro": f"Campo obrigatório ausente: {e}"}), 400
