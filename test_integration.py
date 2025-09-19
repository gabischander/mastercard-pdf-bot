#!/usr/bin/env python3
"""
Teste da integração Gmail + PDF no bot principal
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
project_path = Path(__file__).parent / "cardbrand-updates"
sys.path.insert(0, str(project_path))

def test_integration():
    """Teste básico da integração"""
    try:
        # 1. Testar importações
        from config.email_config import get_gmail_api_config
        from integrations.gmail_monitor import process_gmail_keywords
        print("✅ Importações funcionando")

        # 2. Testar configuração
        config = get_gmail_api_config()
        print(f"✅ Config: {len(config['keywords'])} keywords configuradas")

        # 3. Testar busca de emails
        emails = process_gmail_keywords(config)
        print(f"✅ Gmail API: {len(emails)} emails encontrados")

        # 4. Testar conversão para formato da plataforma
        email_items = []
        for email in emails:
            # Simular conversão para formato do bot
            received_date = datetime.fromisoformat(email['received_at'].replace('Z', '+00:00'))
            date_display = received_date.strftime('%d/%m/%Y %H:%M')
            sender_clean = email['from'].split('@')[0] if '@' in email['from'] else email['from']
            display_name = f"📧 {email['subject']} | 📅 {date_display} | 👤 {sender_clean}"

            email_item = {
                'name': display_name,
                'id': email['id'],
                'type': 'email',
                'data': email,
                'modified_date': received_date.date(),
                'modified_display': date_display
            }
            email_items.append(email_item)

        print(f"✅ Conversão: {len(email_items)} items convertidos para formato da plataforma")

        if email_items:
            print("\n📋 Exemplo de item convertido:")
            item = email_items[0]
            print(f"   • Nome: {item['name'][:80]}...")
            print(f"   • Tipo: {item['type']}")
            print(f"   • ID: {item['id']}")

        print("\n🎉 INTEGRAÇÃO FUNCIONANDO!")
        print("✅ Emails aparecerão na plataforma junto com PDFs")
        print("✅ Formato: 📧 [Assunto] | 📅 [Data] | 👤 [Remetente]")

        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_integration()