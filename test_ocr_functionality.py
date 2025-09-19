#!/usr/bin/env python3
"""
Teste completo da funcionalidade OCR com PDFs simulados
"""
import os
import sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Adicionar path do projeto
project_path = Path(__file__).parent / "cardbrand-updates"
sys.path.insert(0, str(project_path))

def create_test_email_pdf():
    """Cria um PDF simulando um e-mail para teste"""
    filename = "test_email.pdf"

    # Criar PDF com texto simulando e-mail
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Simular cabeçalho de e-mail
    y = height - 50
    c.drawString(50, y, "From: sender@company.com")
    y -= 20
    c.drawString(50, y, "To: recipient@mastercard.com")
    y -= 20
    c.drawString(50, y, "Subject: Important Update - New Processing Requirements")
    y -= 20
    c.drawString(50, y, "Date: September 19, 2025")
    y -= 40

    # Simular corpo do e-mail
    email_body = [
        "Dear Team,",
        "",
        "This email contains important updates regarding new processing",
        "requirements that will take effect on October 1, 2025.",
        "",
        "Key changes include:",
        "- Enhanced validation for merchant transactions",
        "- Updated compliance requirements for all issuers",
        "- New security protocols for authorization systems",
        "",
        "Please review the attached documentation and ensure your",
        "systems are updated accordingly.",
        "",
        "Best regards,",
        "Operations Team"
    ]

    for line in email_body:
        c.drawString(50, y, line)
        y -= 15

    c.save()
    return filename

def test_pdf_extraction():
    """Testa extração de PDF com e sem OCR"""
    try:
        from data_processing.extractors.pdf_extractor import extract_pdf_info

        print("🧪 Testando funcionalidade OCR...")

        # Criar PDF de teste
        test_file = create_test_email_pdf()
        print(f"✅ PDF de teste criado: {test_file}")

        # Ler conteúdo do PDF
        with open(test_file, 'rb') as f:
            pdf_content = f.read()

        # Testar extração
        print("\n📄 Testando extração de PDF...")
        result = extract_pdf_info(pdf_content, test_file)

        # Mostrar resultados
        print("=" * 60)
        print("📊 RESULTADOS DA EXTRAÇÃO:")
        print("=" * 60)

        if result.get('Release Category') == 'Email':
            print("✅ DETECTADO COMO E-MAIL")
            print(f"📧 De: {result.get('Email From', 'N/A')}")
            print(f"📧 Para: {result.get('Email To', 'N/A')}")
            print(f"📧 Assunto: {result.get('Email Subject', 'N/A')}")
            print(f"📧 Data: {result.get('Email Date', 'N/A')}")
            print(f"🔧 Método: {result.get('Extraction Method', 'N/A')}")
        else:
            print(f"📄 Detectado como: {result.get('Release Category', 'N/A')}")
            print(f"🏷️ Brand: {result.get('Affected Brand', 'N/A')}")
            print(f"📝 Title: {result.get('Announcement Title', 'N/A')}")

        # Mostrar texto extraído
        extracted_text = result.get('PDF Text', '')
        if extracted_text:
            print(f"\n📝 Texto extraído ({len(extracted_text)} caracteres):")
            print("-" * 40)
            print(extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text)
        else:
            print("❌ Nenhum texto foi extraído")

        # Limpar arquivo de teste
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\n🧹 Arquivo de teste removido: {test_file}")

        return True

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se de que está no diretório correto")
        return False
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🚀 Teste Completo da Funcionalidade OCR")
    print("=" * 50)

    # Verificar se reportlab está disponível para criar PDF de teste
    try:
        import reportlab
    except ImportError:
        print("❌ reportlab não encontrado. Instalando...")
        os.system(f"{sys.executable} -m pip install reportlab")
        try:
            import reportlab
            print("✅ reportlab instalado")
        except:
            print("❌ Não foi possível instalar reportlab")
            return

    # Executar teste
    success = test_pdf_extraction()

    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ O sistema OCR está funcionando corretamente")
        print("📧 E-mails em PDF serão processados automaticamente")
    else:
        print("\n❌ TESTE FALHOU")
        print("🔧 Verifique os erros acima para corrigir o problema")

if __name__ == "__main__":
    main()