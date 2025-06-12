# API DO GARÇOM - SISTEMA DE RESERVAS
# Servidor Flask específico para operações do garçom

# IMPORTAÇÕES E CONFIGURAÇÕES

from flask import Flask, request, jsonify, Response
import sqlite3
import datetime
import json
from flask_cors import CORS

# Configuração da aplicação Flask
app = Flask(__name__)
CORS(app)  # Permite requisições de diferentes origens

# Configuração do banco de dados
DB_PATH = 'reservas.db'

# FUNÇÕES DO BANCO DE DADOS

def conectar():
    #Estabelece conexão com o banco de dados SQLite

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acesso às colunas por nome
    return conn

# FUNÇÕES AUXILIARES

def converter_para_json(obj):
   #Converte data e hora para um formato compatível com JSON

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
    raise TypeError(f"Tipo nao serializavel: {type(obj)}")

# ROTAS DA API

@app.route('/reservas-disponiveis', methods=['GET'])
def reservas_disponiveis():
    #Lista todas as reservas disponíveis para confirmação
    
    try:
        # Conecta ao banco de dados
        con = conectar()
        cur = con.cursor()

        # Busca reservas não confirmadas
        cur.execute('''
            SELECT * FROM reservas 
            WHERE status = 'reservada'
            ORDER BY data, hora
        ''')
        
        rows = cur.fetchall()
        
        # Converte resultados para lista 
        resultado = [dict(row) for row in rows]

        # Desconecta do banco de dados
        cur.close()
        con.close()

        # Retorna resposta JSON
        return Response(
            json.dumps(resultado, default=converter_para_json), 
            mimetype='application/json'
        )
        
    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao buscar reservas disponiveis: {e}")
        return jsonify({'error': 'Erro no banco de dados'}), 500
    except Exception as e:
        print(f"Erro inesperado ao buscar reservas disponiveis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/confirmar/<int:id>', methods=['POST'])
def confirmar_reserva(id):
    #Confirma uma reserva específica

    # Extrai nome do garçom do corpo da requisição
    garcom = request.json.get('garcom') if request.json else None
    
    # Valida se o campo garçom foi preenchido 
    if not garcom:
        return jsonify({'mensagem': 'Campo "garcom" e obrigatorio'}), 400
    
    try:
        # Conecta ao banco de dados
        con = conectar()
        cur = con.cursor()

        # Verifica se a reserva existe e está disponível para confirmação
        cur.execute('''
            SELECT * FROM reservas 
            WHERE id = ? AND status = "reservada"
        ''', (id,))
        
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            con.close()
            return jsonify({
                'mensagem': 'Reserva nao encontrada ou ja confirmada'
            }), 404

        # Confirma a reserva e registra o garçom responsável
        cur.execute('''
            UPDATE reservas 
            SET status = "confirmada", garcom = ? 
            WHERE id = ?
        ''', (garcom, id))
        
        # Verifica se a atualização foi bem-sucedida
        if cur.rowcount == 0:
            cur.close()
            con.close()
            return jsonify({
                'mensagem': 'Erro ao confirmar reserva'
            }), 500
        
        # Confirma tarefa
        con.commit()
        cur.close()
        con.close()
        
        return jsonify({'mensagem': 'Reserva confirmada com sucesso'})
        
    except sqlite3.Error as e:
        print(f"Erro no banco de dados ao confirmar reserva {id}: {e}")
        return jsonify({'error': 'Erro no banco de dados'}), 500
    except Exception as e:
        print(f"Erro inesperado ao confirmar reserva {id}: {e}")
        return jsonify({'error': str(e)}), 500

# ROTA DE SAÚDE DA API

@app.route('/health', methods=['GET'])
def health_check():
    #Endpoint para verificar se a API está funcionando

    return jsonify({
        'status': 'online',
        'service': 'API do Garcom',
        'timestamp': datetime.datetime.now().isoformat()
    })

# TRATAMENTO DE ERROS

@app.errorhandler(404)
def not_found(error):
    #Tratamento para rotas não encontradas
    return jsonify({'error': 'Endpoint nao encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    #Tratamento para métodos HTTP não permitidos
    return jsonify({'error': 'Metodo nao permitido'}), 405

@app.errorhandler(500)
def internal_error(error):
    #Tratamento para erros internos do servidor
    return jsonify({'error': 'Erro interno do servidor'}), 500

# INICIALIZAÇÃO DA APLICAÇÃO

if __name__ == '__main__':
    print("🚀 Iniciando API do Garçom...")
    print("📍 Endpoints disponíveis:")
    print("   GET  /reservas-disponiveis - Lista reservas não confirmadas")
    print("   POST /confirmar/<id>       - Confirma uma reserva")
    print("   GET  /health               - Status da API")
    print("-" * 50)
    
    # Execução da aplicação
    app.run(port=5000, debug=True)