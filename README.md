# A3 Sistemas Distribuídos e Mobile


## Requisitos de Software

Para executar a aplicação, é necessário ter os seguintes softwares instalados:

- **Python 3.7 ou superior**  

- **Frameworks a serem instalados via `pip` ou `pip3`:**
  - `Flask`
  - `Flask-Cors` (Extensão para permitir CORS)
  - `requests`
  - `git` (Para clonar o Projeto)

- **Banco de Dados:**  
  - `SQLite` (já incluso no Python padrão)

- **Navegador Web:**  
  - Google Chrome, Firefox, Edge ou similar

- **Sistema Operacional Compatível:**  
  - Windows, Linux ou macOS

---

## Instalação

### 1. Obter o código via terminal

1. No terminal digite os comandos:
   
   ```bash
   git clone https://github.com/dan1esl/Servidor-Restaurant
   cd Servidor-Restaurante


### 2. Instalar o Python

1. Baixe o Python 3.7 ou superior no site oficial:  
 [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. **Durante a instalação, marque as opções:**
   - `Add Python to PATH`
   - `Use admin privileges when installing py.exe`

3. **Clique em `Install Now` e aguarde a finalização.**

4. **Após a conclusão da instalação, feche a janela.**

---

### 3. Instalar as Dependências

**Abra o terminal (Prompt de Comando no Windows ou Terminal no Linux/macOS) e execute o seguinte comando:**

- `pip install flask flask_cors requests` Para windows

- `pip3 install flask flask_cors requests` Para Linux/macOS

---

### 4. Execução da Aplicação
1. **Abrindo o Terminal na Pasta do Projeto**

   Para abrir o terminal diretamente na pasta onde o projeto está salvo:

- Abra o Explorador de Arquivos e navegue até a pasta do projeto.

- Clique uma vez na barra de endereços da janela.

- Digite cmd e pressione Enter.

- Isso abrirá uma janela de terminal já localizada no diretório do projeto.

2. Iniciando o Servidor Flask

Com o terminal aberto na pasta correta, execute o seguinte comando:

- `python servidor.py` Para Windows

- `python3 servidor.py` Para linux/macOS

O servidor Flask será iniciado e ficará disponível no endereço:

`http://localhost:5000`

3. Acesso via Navegador
Abra seu navegador preferido (Chrome, Firefox, Edge etc.) e acesse:

`http://localhost:5000`

Na tela inicial da aplicação, selecione o perfil com o qual deseja acessar:

  Atendente

  Garçom

  Gerente

## OBSERVAÇÃO: 
Caso haja algum erro inesperado durante o uso da aplicação, é
possível que o framework Flask instalado pelo usuário esteja desatualizado. Para
atualizá-lo, abra o Prompt de Comando normalmente (sem navegar até a pasta do
projeto), e execute o comando:

`pip install --upgrade flask` Windows

`pip3 install --upgrade flask` Linux/macOS
