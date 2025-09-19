import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from slack_config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN

# Carrega as variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# --- CONFIGURAÇÃO ---
# Os tokens são carregados do arquivo slack_config.py
# Certifique-se de configurar os tokens corretos lá!
# --- FIM DA CONFIGURAÇÃO ---

# Inicializa o aplicativo com o token do bot
app = App(token=SLACK_BOT_TOKEN)

# Esta função será chamada sempre que alguém mencionar o bot com @
@app.event("app_mention")
def mention_handler(body, say):
    """
    Escuta por menções ao bot e responde com uma mensagem de teste.
    """
    # Pega o texto da mensagem que o usuário enviou
    texto_do_usuario = body["event"]["text"]
    
    print(f"Recebi uma menção: {texto_do_usuario}")
    
    # Envia uma resposta de volta para o canal do Slack
    say("Olá! Eu recebi sua mensagem. Ainda estou aprendendo a pesquisar no Confluence.")

# Comando slash para testar o bot
@app.command("/confluence")
def handle_confluence_command(ack, respond, command):
    """
    Comando slash para interagir com o bot
    """
    ack()  # Confirma que recebeu o comando
    
    # Resposta temporária
    respond("Comando recebido! Em breve poderei pesquisar no Confluence para você.")

# Comando para mostrar ajuda
@app.command("/help")
def handle_help_command(ack, respond, command):
    """
    Comando de ajuda
    """
    ack()
    
    help_text = """
🤖 *Comandos disponíveis:*
• `/confluence` - Pesquisar no Confluence (em desenvolvimento)
• `/help` - Mostrar esta mensagem de ajuda
• Mencione o bot com @ para interagir

*Status:* Bot em desenvolvimento - funcionalidades do Confluence serão adicionadas em breve!
    """
    
    respond(help_text)

# --- Bloco principal para iniciar o bot ---
if __name__ == "__main__":
    print("🤖 O bot está sendo iniciado em modo Socket...")
    print("📋 Certifique-se de que os tokens estão configurados no arquivo .env")
    
    # Verifica se os tokens estão configurados
    if SLACK_BOT_TOKEN == "xoxb-SEU-BOT-TOKEN-AQUI" or SLACK_APP_TOKEN == "xapp-SEU-APP-LEVEL-TOKEN-AQUI":
        print("⚠️  ATENÇÃO: Tokens não configurados!")
        print("📝 Configure os tokens no arquivo .env antes de executar o bot.")
        exit(1)
    
    # O SocketModeHandler é o que conecta nosso bot ao Slack de forma segura
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

