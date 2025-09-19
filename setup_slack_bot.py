#!/usr/bin/env python3
"""
Script de configuração inicial do Bot Slack
"""

import os
import subprocess
import sys

def install_requirements():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_config():
    """Verifica se a configuração está correta"""
    print("\n🔍 Verificando configuração...")
    
    try:
        from slack_config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
        
        if SLACK_BOT_TOKEN == "xoxb-SEU-BOT-TOKEN-AQUI":
            print("❌ SLACK_BOT_TOKEN não configurado!")
            print("📝 Edite o arquivo slack_config.py e configure seu token do bot")
            return False
            
        if SLACK_APP_TOKEN == "xapp-SEU-APP-LEVEL-TOKEN-AQUI":
            print("❌ SLACK_APP_TOKEN não configurado!")
            print("📝 Edite o arquivo slack_config.py e configure seu token do app")
            return False
            
        print("✅ Configuração parece estar correta!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar configuração: {e}")
        return False

def main():
    """Função principal"""
    print("🤖 Configuração do Bot Slack")
    print("=" * 40)
    
    # Instala dependências
    if not install_requirements():
        return
    
    # Verifica configuração
    if not check_config():
        print("\n📋 Próximos passos:")
        print("1. Configure os tokens no arquivo slack_config.py")
        print("2. Execute este script novamente")
        print("3. Execute: python app.py")
        return
    
    print("\n🎉 Configuração concluída!")
    print("\n📋 Para iniciar o bot:")
    print("   python app.py")
    print("\n📋 Para testar:")
    print("1. Convide o bot para um canal do Slack")
    print("2. Mencione o bot com @nomedoseubot")
    print("3. Use os comandos /confluence ou /help")

if __name__ == "__main__":
    main()
