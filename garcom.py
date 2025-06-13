from flask import Flask, request, jsonify, Response
import sqlite3
import datetime
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  
DB_PATH = 'reservas.db'


def conectar():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn


def converter_para_json(obj):

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


@app.route('/reservas-disponiveis', methods=['GET'])
def reservas_disponiveis():
    
    try:
        con = conectar()
        cur = con.cursor()

        cur.execute('''
            SELECT * FROM reservas 
            WHERE status = 'reservada'
            ORDER BY data, hora
        ''')
        
        rows = cur.fetchall()
        
        resultado = [dict(row) for row in rows]

        cur.close()
        con.close()

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

    garcom = request.json.get('garcom') if request.json else None
    
    if not garcom:
        return jsonify({'mensagem': 'Campo "garcom" e obrigatorio'}), 400
    
    try:
        con = conectar()
        cur = con.cursor()

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

        cur.execute('''
            UPDATE reservas 
            SET status = "confirmada", garcom = ? 
            WHERE id = ?
        ''', (garcom, id))
        
        if cur.rowcount == 0:
            cur.close()
            con.close()
            return jsonify({
                'mensagem': 'Erro ao confirmar reserva'
            }), 500
        
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


@app.route('/health', methods=['GET'])
def health_check():

    return jsonify({
        'status': 'online',
        'service': 'API do Garcom',
        'timestamp': datetime.datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint nao encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Metodo nao permitido'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    print("🚀 Iniciando API do Garçom...")
    print("📍 Endpoints disponíveis:")
    print("   GET  /reservas-disponiveis - Lista reservas não confirmadas")
    print("   POST /confirmar/<id>       - Confirma uma reserva")
    print("   GET  /health               - Status da API")
    print("-" * 50)
    
    app.run(port=5000, debug=True)