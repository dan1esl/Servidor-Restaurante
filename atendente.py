# CRIAR E CANCELAR RESERVAS
# Script para interagir com a API de reservas

import requests
from datetime import datetime


BASE_URL = 'http://localhost:5000/atendente'  # URL base da API

# FUNÇÕES AUXILIARES

def converter_data_para_iso(data_input):

    #Converte data do formato brasileiro para o formato do banco de dados
    try:
        return datetime.strptime(data_input, '%d-%m-%Y').strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("Data deve estar no formato DD-MM-YYYY")

def fazer_requisicao_post(url, dados):
    #Faz uma requisição POST e trata a resposta
    
    try:
        response = requests.post(url, json=dados)
        print(f"Status Code: {response.status_code}")
        
        # Verifica se a resposta foi bem-sucedida
        if response.status_code == 200 and response.text.strip():
            print("✅ Sucesso:", response.json())
        else:
            print("❌ Erro ou resposta vazia:", response.text)
            
    except requests.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except ValueError as e:
        print(f"❌ Erro ao processar resposta JSON: {e}")
        print(f"Resposta recebida: {response.text}")

def fazer_requisicao_delete(url):
    #Faz uma requisição DELETE e trata a resposta
    
    try:
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        
        # Verifica se a resposta foi bem-sucedida 
        if response.status_code == 200 and response.text.strip():
            print("✅ Sucesso:", response.json())
        else:
            print("❌ Erro ou resposta vazia:", response.text)
            
    except requests.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except ValueError as e:
        print(f"❌ Erro ao processar resposta JSON: {e}")
        print(f"Resposta recebida: {response.text}")

def criar_nova_reserva():
    #Coleta dados do usuário e cria uma nova reserva
    
    print("\n=== CRIAR NOVA RESERVA ===")
    
    # Coleta dados da reserva
    try:
        
        #Dados da reserva
        data_input = input("📅 Data (DD-MM-YYYY): ")
        data_iso = converter_data_para_iso(data_input)
        
        hora = input("🕐 Hora (HH:MM): ")
        mesa = int(input("🪑 Mesa: "))
        pessoas = int(input("👥 Quantidade de pessoas: "))
        responsavel = input("👤 Nome do responsável: ")
        
        # Dados montados para mandar para a API 
        dados_reserva = {
            'data': data_iso,
            'hora': hora,
            'mesa': mesa,
            'pessoas': pessoas,
            'responsavel': responsavel
        }
        
        # Faz a requisição para criar reserva
        url = f"{BASE_URL}/reserva"
        fazer_requisicao_post(url, dados_reserva)
        
    except ValueError as e:
        print(f"❌ Erro nos dados informados: {e}")
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")

def cancelar_reserva_existente():

    #Realiza o cancelamento
    print("\n=== CANCELAR RESERVA ===")
    
    try:
        # Coleta o ID da reserva
        id_reserva = input("🔢 ID da reserva: ")
        
        # Valida se o ID é um número
        if not id_reserva.isdigit():
            print("❌ ID deve ser um número válido")
            return
        
        # Requisição para cancelar reserva
        url = f"{BASE_URL}/reserva/{id_reserva}"
        fazer_requisicao_delete(url)
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")

# PROGRAMA PRINCIPAL

def main():
    #Função principal que exibe o menu e processa a escolha do usuário
    
    print("=" * 50)
    print("🍽️  SISTEMA DE RESERVAS - CLIENTE")
    print("=" * 50)
    print("1 - Criar reserva")
    print("2 - Cancelar reserva")
    print("0 - Sair")
    print("-" * 50)
    
    try:
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1':
            criar_nova_reserva()
        elif opcao == '2':
            cancelar_reserva_existente()
        elif opcao == '0':
            print("👋 Saindo do sistema...")
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 0.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()