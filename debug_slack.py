#!/usr/bin/env python3
"""
Script de debug para verificar conexão com Slack
"""

import os
from slack_sdk import WebClient
from slack_config import SLACK_BOT_TOKEN

def test_slack_connection():
    """Testa a conexão com o Slack"""
    print("🔍 Testando conexão com Slack...")
    
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        response = client.auth_test()
        
        if response["ok"]:
            print("✅ Conexão com Slack OK!")
            print(f"📋 Bot: {response['user']}")
            print(f"📋 Team: {response['team']}")
            print(f"📋 URL: {response['url']}")
            return True
        else:
            print(f"❌ Erro na autenticação: {response['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_bot_info():
    """Testa informações do bot"""
    print("\n🔍 Testando informações do bot...")
    
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        response = client.bots_info()
        
        if response["ok"]:
            bot_info = response["bot"]
            print("✅ Informações do bot obtidas!")
            print(f"📋 Nome: {bot_info['name']}")
            print(f"📋 ID: {bot_info['id']}")
            return True
        else:
            print(f"❌ Erro ao obter info do bot: {response['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_socket_mode():
    """Testa se Socket Mode está configurado"""
    print("\n🔍 Testando Socket Mode...")
    
    try:
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        from slack_config import SLACK_APP_TOKEN
        
        print("✅ SocketModeHandler importado com sucesso")
        print(f"📋 App Token configurado: {SLACK_APP_TOKEN[:20]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro no Socket Mode: {e}")
        return False

def main():
    """Função principal de debug"""
    print("🐛 Debug do Bot Slack")
    print("=" * 30)
    
    # Testa conexão básica
    if not test_slack_connection():
        print("\n❌ Problema na conexão básica com Slack")
        return
    
    # Testa informações do bot
    if not test_bot_info():
        print("\n❌ Problema ao obter informações do bot")
        return
    
    # Testa Socket Mode
    if not test_socket_mode():
        print("\n❌ Problema com Socket Mode")
        return
    
    print("\n🎉 Todos os testes de conexão passaram!")
    print("\n📋 Possíveis problemas:")
    print("1. Bot não foi convidado para o canal")
    print("2. Socket Mode não está ativado no app")
    print("3. Permissões insuficientes")
    print("4. Bot está offline no Slack")

if __name__ == "__main__":
    main()

