#!/usr/bin/env python3
"""
Teste Gmail API com credenciais existentes
"""
import sys
from pathlib import Path

# Adicionar path do projeto
project_path = Path(__file__).parent / "cardbrand-updates"
sys.path.insert(0, str(project_path))

def test_gmail_real():
    """Testa Gmail API real"""
    try:
        from integrations.gmail_monitor import GmailKeywordMonitor
        from config.email_config import get_gmail_api_config

        print("🧪 Testando Gmail API com Credenciais Existentes")
        print("=" * 50)

        config = get_gmail_api_config()
        monitor = GmailKeywordMonitor(config)

        print("📧 Tentando autenticar...")
        if monitor.authenticate():
            print("✅ SUCESSO! Gmail API autenticado!")
            print("🔍 Testando busca de e-mails...")

            # Fazer uma busca teste
            emails = monitor.search_keyword_emails()
            print(f"📧 Encontrados: {len(emails)} e-mails com palavras-chave")

            if len(emails) > 0:
                print("\n📋 Exemplo de e-mail encontrado:")
                email = emails[0]
                print(f"   • De: {email.get('from', 'N/A')}")
                print(f"   • Assunto: {email.get('subject', 'N/A')}")
                print(f"   • É forward: {email.get('is_forward', False)}")
            else:
                print("\n💡 Nenhum e-mail com #cardbrand encontrado")
                print("   Para testar: envie um e-mail para você com #cardbrand no assunto")

            print("\n🎉 GMAIL API FUNCIONANDO!")
            print("✅ Pode usar as mesmas credenciais dos outros projetos")
            return True

        else:
            print("❌ Falha na autenticação")
            return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gmail_real()

    if success:
        print("\n" + "=" * 50)
        print("🎯 PRÓXIMOS PASSOS:")
        print("=" * 50)
        print("1. ✅ Gmail API funcionando!")
        print("2. 📧 Para testar keywords:")
        print("   • Envie e-mail para você com #cardbrand no assunto")
        print("   • Ou encaminhe um e-mail + adicione #cardbrand")
        print("3. 🚀 Integrar no bot principal")
    else:
        print("\n❌ Verifique se Gmail API está habilitada no mesmo projeto Google Cloud")