# =============================================
# CLIENTE DE RELATÓRIOS - SISTEMA DE RESERVAS
# Script para gerar relatórios do sistema de reservas
# =============================================

# =============================================
# IMPORTAÇÕES
# =============================================

from datetime import datetime
import requests

# =============================================
# CONFIGURAÇÕES
# =============================================

BASE_URL = 'http://localhost:5000'  # URL base da API

# =============================================
# FUNÇÕES AUXILIARES
# =============================================

def get_json_safe(url):
    """
    Faz uma requisição GET de forma segura e retorna dados JSON
    
    Args:
        url (str): URL completa para fazer a requisição
        
    Returns:
        list: Lista com os dados JSON ou lista vazia em caso de erro
    """
    try:
        # Fazer requisição HTTP GET
        response = requests.get(url)
        
        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            try:
                # Tentar converter resposta para JSON
                return response.json()
            except ValueError:
                # Erro ao fazer parse do JSON
                print("❌ Erro: Resposta não é JSON válido.")
                print(f"Resposta recebida: {response.text}")
                return []
        else:
            # Erro HTTP (4xx, 5xx)
            print(f"❌ Erro HTTP: Status {response.status_code}")
            print(f"Resposta: {response.text}")
            return []
            
    except requests.RequestException as e:
        # Erro de conexão ou timeout
        print(f"❌ Erro na requisição: {e}")
        return []

def formatar_data(data_str):
    """
    Converte data do formato brasileiro (DD-MM-YYYY) para ISO (YYYY-MM-DD)
    
    Args:
        data_str (str): Data no formato DD-MM-YYYY
        
    Returns:
        str: Data no formato ISO (YYYY-MM-DD)
        
    Raises:
        ValueError: Se a data estiver em formato inválido
    """
    try:
        return datetime.strptime(data_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Data deve estar no formato DD-MM-YYYY")

def exibir_reservas(reservas, titulo):
    """
    Exibe uma lista de reservas de forma formatada
    
    Args:
        reservas (list): Lista de reservas (dicionários)
        titulo (str): Título do relatório
    """
    print(f"\n{'='*60}")
    print(f"📊 {titulo}")
    print(f"{'='*60}")
    
    if not reservas:
        print("📝 Nenhuma reserva encontrada.")
        return
    
    print(f"📈 Total de reservas: {len(reservas)}")
    print("-" * 60)
    
    for i, reserva in enumerate(reservas, 1):
        print(f"🔸 Reserva #{i}")
        print(f"   ID: {reserva.get('id', 'N/A')}")
        print(f"   📅 Data: {reserva.get('data', 'N/A')}")
        print(f"   🕐 Hora: {reserva.get('hora', 'N/A')}")
        print(f"   🪑 Mesa: {reserva.get('mesa', 'N/A')}")
        print(f"   👥 Pessoas: {reserva.get('pessoas', 'N/A')}")
        print(f"   👤 Responsável: {reserva.get('responsavel', 'N/A')}")
        print(f"   📋 Status: {reserva.get('status', 'N/A')}")
        
        # Exibir garçom apenas se houver
        if reserva.get('garcom'):
            print(f"   🧑‍💼 Garçom: {reserva.get('garcom')}")
        
        print("-" * 40)

# =============================================
# FUNÇÕES DE RELATÓRIO
# =============================================

def relatorio_por_periodo():
    """
    Gera relatório de reservas por período específico
    """
    print("\n=== RELATÓRIO POR PERÍODO ===")
    
    try:
        # Coletar datas do usuário
        inicio = input("📅 Data início (DD-MM-YYYY): ")
        fim = input("📅 Data fim (DD-MM-YYYY): ")
        
        # Converter datas para formato ISO
        inicio_formatado = formatar_data(inicio)
        fim_formatado = formatar_data(fim)
        
        # Fazer requisição para a API
        url = f'{BASE_URL}/relatorio/periodo?inicio={inicio_formatado}&fim={fim_formatado}'
        reservas = get_json_safe(url)
        
        # Exibir resultados
        titulo = f"RESERVAS DE {inicio} A {fim}"
        exibir_reservas(reservas, titulo)
        
    except ValueError as e:
        print(f"❌ Erro nos dados informados: {e}")
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")

def relatorio_por_mesa():
    """
    Gera relatório de todas as reservas de uma mesa específica
    """
    print("\n=== RELATÓRIO POR MESA ===")
    
    try:
        # Coletar número da mesa
        mesa = input("🪑 Número da mesa: ")
        
        # Validar se é um número
        if not mesa.isdigit():
            print("❌ Número da mesa deve ser um valor numérico")
            return
        
        # Fazer requisição para a API
        url = f'{BASE_URL}/relatorio/mesa/{mesa}'
        reservas = get_json_safe(url)
        
        # Exibir resultados
        titulo = f"RESERVAS DA MESA {mesa}"
        exibir_reservas(reservas, titulo)
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")

def relatorio_por_garcom():
    """
    Gera relatório de reservas confirmadas por um garçom específico
    """
    print("\n=== RELATÓRIO POR GARÇOM ===")
    
    try:
        # Coletar nome do garçom
        nome = input("🧑‍💼 Nome do garçom: ")
        
        # Validar se o nome não está vazio
        if not nome.strip():
            print("❌ Nome do garçom não pode estar vazio")
            return
        
        # Fazer requisição para a API
        url = f'{BASE_URL}/relatorio/garcom/{nome}'
        reservas = get_json_safe(url)
        
        # Exibir resultados
        titulo = f"RESERVAS CONFIRMADAS POR {nome.upper()}"
        exibir_reservas(reservas, titulo)
        
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")

# =============================================
# PROGRAMA PRINCIPAL
# =============================================

def exibir_menu():
    """
    Exibe o menu principal do sistema
    """
    print("=" * 60)
    print("📊 SISTEMA DE RELATÓRIOS - RESERVAS")
    print("=" * 60)
    print("1 - Relatório por período")
    print("2 - Relatório por mesa")
    print("3 - Relatório por garçom")
    print("0 - Sair")
    print("-" * 60)

def main():
    """
    Função principal que controla o fluxo do programa
    """
    while True:
        exibir_menu()
        
        try:
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                relatorio_por_periodo()
            elif opcao == '2':
                relatorio_por_mesa()
            elif opcao == '3':
                relatorio_por_garcom()
            elif opcao == '0':
                print("👋 Saindo do sistema de relatórios...")
                break
            else:
                print("❌ Opção inválida! Escolha um número de 0 a 3.")
            
            # Pausa para o usuário visualizar o resultado
            if opcao in ['1', '2', '3']:
                input("\n⏸️  Pressione ENTER para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            input("\n⏸️  Pressione ENTER para continuar...")

# EXECUÇÃO DO PROGRAMA

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("🔧 Verifique se a API está rodando em http://localhost:5000")