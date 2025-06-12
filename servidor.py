# Sistema de Reservas de Restaurante
# Aplicação Flask para gerenciar reservas de mesas

# IMPORTAÇÕES E CONFIGURAÇÕES

from flask import Flask, request, jsonify, Response, render_template
import sqlite3
from collections import OrderedDict
import datetime
import json
from flask_cors import CORS

# Configuração da aplicação Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # Permite requisições de diferentes origens

# Configuração do banco de dados
DB_PATH = 'reservas.db'

# FUNÇÕES DO BANCO DE DADOS

def conectar():
    """
    Estabelece conexão com o banco de dados SQLite
    Configura row_factory para retornar dicionários
    Cria a tabela se não existir
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    criar_tabela(conn)
    return conn

def criar_tabela(conn):
    
    #Cria a tabela 'reservas' se ela não existir
    
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            mesa INTEGER NOT NULL,
            pessoas INTEGER NOT NULL,
            responsavel TEXT NOT NULL,
            status TEXT DEFAULT 'reservada',
            garcom TEXT
        )
    ''')
    conn.commit()

# FUNÇÕES AUXILIARES

def converter_para_json(obj):
    """
    Converte objetos datetime para formato JSON serializável
    Usado como função 'default' no json.dumps()
    """
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.strftime('%H:%M:%S')
    elif isinstance(obj, datetime.timedelta):
        total_seconds = int(obj.total_seconds())
        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        segundos = total_seconds % 60
        return f"{horas:02}:{minutos:02}:{segundos:02}"
    raise TypeError(f"Tipo não serializável: {type(obj)}")

# ROTAS DAS PÁGINAS WEB

@app.route('/')
def home():
    #Página principal - Seleção de perfis
    return render_template('index.html')

@app.route('/atendente')
def pagina_atendente():
    #Página do Atendente - Interface de reservas
    return render_template('atendente.html')

@app.route('/garcom')
def pagina_garcom():
    #Página do Garçom - Para confirmar reservas
    return render_template('garcom.html')

@app.route('/gerente')
def pagina_gerente():
    #Página do Gerente - Para visualizar relatórios
    return render_template('gerente.html')

# ROTAS DE API - OPERAÇÕES COM RESERVAS

@app.route('/reserva', methods=['POST'])
def criar_reserva():
    
    #Cria uma nova reserva

    dados = request.json
    try:
        # Verificar se a mesa está no range válido (1-20)
        if dados['mesa'] > 20 or dados['mesa'] < 1:
            return jsonify({'mensagem': 'Mesa deve estar entre 1 e 20'}), 400

        # Verificar se não é uma data/hora passada
        data_obj = datetime.datetime.strptime(dados['data'], '%Y-%m-%d')
        hora_obj = datetime.datetime.strptime(dados['hora'], '%H:%M').time()
        data_hora_reserva = datetime.datetime.combine(data_obj.date(), hora_obj)
        
        if data_hora_reserva <= datetime.datetime.now():
            return jsonify({'mensagem': 'Não é possível fazer reservas para datas/horas passadas'}), 400

        # Formatando a data 
        dados['data'] = data_obj.strftime('%Y-%m-%d')

        # Verificar se a mesa já está reservada no mesmo horário
        con = conectar()
        cur = con.cursor()

        cur.execute('''
            SELECT * FROM reservas
            WHERE mesa = ? AND data = ? AND hora = ? AND status = 'reservada'
        ''', (dados['mesa'], dados['data'], dados['hora']))

        if cur.fetchone():
            cur.close()
            con.close()
            return jsonify({'mensagem': 'Mesa ja reservada nesse horario'}), 400

        # INSERIR NOVA RESERVA
        cur.execute('''
            INSERT INTO reservas (data, hora, mesa, pessoas, responsavel, status)
            VALUES (?, ?, ?, ?, ?, 'reservada')
        ''', (dados['data'], dados['hora'], dados['mesa'], dados['pessoas'], dados['responsavel']))
        
        reserva_id = cur.lastrowid  # Obter ID da reserva criada

        con.commit()
        cur.close()
        con.close()

        # Retornar resposta 
        resposta = OrderedDict([
            ('mensagem', 'Reserva criada com sucesso'),
            ('id', reserva_id)
        ])
        return Response(json.dumps(resposta), mimetype='application/json')
        
    except Exception as e:
        print(f"Erro ao criar reserva: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reserva/<int:id>', methods=['DELETE'])
def cancelar_reserva(id):
    
    #Cancela uma reserva existente
    try:
        con = conectar()
        cur = con.cursor()

        # Verificar se a reserva existe e verificar status
        cur.execute('SELECT status FROM reservas WHERE id = ?', (id,))
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            con.close()
            return jsonify({'mensagem': 'Reserva nao encontrada'}), 404

        # Verificar se a reserva já foi confirmada
        # Reservas confirmadas não podem ser canceladas
        if reserva['status'] == 'confirmada':
            cur.close()
            con.close()
            return jsonify({'mensagem': 'Nao e possivel cancelar reserva ja confirmada pelo garcom'}), 400

        # Deletar a reserva
        cur.execute('DELETE FROM reservas WHERE id = ?', (id,))
        con.commit()
        cur.close()
        con.close()
        
        return jsonify({'mensagem': 'Reserva cancelada com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/confirmar/<int:id>', methods=['POST'])
def confirmar_reserva(id):
    
    #Confirmação da reserva
    garcom = request.json.get('garcom')
    
    # Verificar se o nome do garçom foi fornecido
    if not garcom:
        return jsonify({'mensagem': 'Campo "garcom" e obrigatorio'}), 400
        
    try:
        con = conectar()
        cur = con.cursor()

        # Verifica se a reserva está disponível para confirmação
        cur.execute('SELECT * FROM reservas WHERE id = ? AND status = "reservada"', (id,))
        if not cur.fetchone():
            cur.close()
            con.close()
            return jsonify({'mensagem': 'Reserva nao encontrada ou ja confirmada'}), 404

        # Atualiza o status para 'confirmada' e registrar o nome do garçom
        cur.execute('''
            UPDATE reservas SET status = 'confirmada', garcom = ? WHERE id = ?
        ''', (garcom, id))
        
        con.commit()
        cur.close()
        con.close()
        
        return jsonify({'mensagem': 'Reserva confirmada'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ROTAS DE RELATÓRIOS

@app.route('/relatorio/periodo', methods=['GET'])
def relatorio_periodo():
    #Gera relatório de reservas por período
    
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Validação de parâmetros obrigatórios
    if not inicio or not fim:
        return jsonify({'error': 'Parametros "inicio" e "fim" sao obrigatorios.'}), 400

    try:
        con = conectar()
        cur = con.cursor()
        
        # Busca reservas no período especificado
        cur.execute('''
            SELECT * FROM reservas
            WHERE data BETWEEN ? AND ?
        ''', (inicio, fim))
        
        rows = cur.fetchall()
        reservas = [dict(row) for row in rows] 
        
        cur.close()
        con.close()
        
        return Response(json.dumps(reservas, default=converter_para_json), mimetype='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/relatorio/mesa/<int:mesa>', methods=['GET'])
def relatorio_mesa(mesa):
    #Gera relatório de todas as reservas de uma mesa específica
    
    try:
        con = conectar()
        cur = con.cursor()
        
        # Buscar todas as reservas da mesa especificada
        cur.execute('SELECT * FROM reservas WHERE mesa = ?', (mesa,))
        rows = cur.fetchall()
        resultado = [dict(row) for row in rows]
        
        cur.close()
        con.close()
        
        return Response(json.dumps(resultado, default=converter_para_json), mimetype='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/relatorio/garcom/<string:nome>', methods=['GET'])
def relatorio_garcom(nome):
    #Gera relatório de reservas confirmadas por um garçom específico
    
    try:
        con = conectar()
        cur = con.cursor()
        
        # Busca reservas confirmadas pelo garçom especificado
        cur.execute('SELECT * FROM reservas WHERE garcom = ?', (nome,))
        rows = cur.fetchall()
        resultado = [dict(row) for row in rows]
        
        cur.close()
        con.close()
        
        return Response(json.dumps(resultado, default=converter_para_json), mimetype='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ROTAS DE CONSULTA

@app.route('/reservas-disponiveis', methods=['GET'])
def listar_reservas_disponiveis():
    #Lista todas as reservas que ainda não foram confirmadas pelo garçom
    
    try:
        con = conectar()
        cur = con.cursor()
        
        # Busca reservas ordenadas por data/hora
        cur.execute("""
            SELECT id, data, hora, mesa, pessoas, responsavel 
            FROM reservas 
            WHERE status = 'reservada' 
            ORDER BY data, hora
        """)
        
        rows = cur.fetchall()
        reservas = [dict(row) for row in rows]
        
        cur.close()
        con.close()
        
        return Response(json.dumps(reservas, default=converter_para_json), mimetype='application/json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
# INICIALIZAÇÃO DA APLICAÇÃO
if __name__ == '__main__':
    app.run(debug=True)