#!/usr/bin/env python3
"""
Script de teste para OCR de e-mails em PDF
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent / "cardbrand-updates"))

def test_email_pdf(pdf_path):
    """Testa extração de e-mail de um PDF"""
    try:
        from data_processing.extractors.pdf_extractor import extract_pdf_info
        from data_processing.extractors.ocr_extractor import setup_tesseract

        # Verificar se OCR está disponível
        if not setup_tesseract():
            print("❌ Tesseract não está disponível")
            print("Execute: python install_ocr.py")
            return False

        print(f"🔍 Testando extração do arquivo: {pdf_path}")

        # Ler arquivo PDF
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        # Extrair informações
        info = extract_pdf_info(pdf_content, os.path.basename(pdf_path))

        # Mostrar resultados
        print("\n📧 Resultados da extração:")
        print("=" * 50)

        if info.get('Release Category') == 'Email':
            print(f"✅ Detectado como: E-mail")
            print(f"📧 De: {info.get('Email From', 'Não encontrado')}")
            print(f"📧 Para: {info.get('Email To', 'Não encontrado')}")
            print(f"📧 Assunto: {info.get('Email Subject', 'Não encontrado')}")
            print(f"📧 Data: {info.get('Email Date', 'Não encontrada')}")
            print(f"📧 Método: {info.get('Extraction Method', 'Desconhecido')}")
            print(f"\n📄 Corpo do e-mail (primeiras 200 chars):")
            print(info.get('Email Body', 'Não encontrado')[:200] + "...")
        else:
            print(f"📄 Detectado como: Documento")
            print(f"📄 Texto extraído (primeiras 200 chars):")
            print(info.get('PDF Text', 'Não encontrado')[:200] + "...")

        print(f"\n📊 Total de caracteres extraídos: {len(info.get('PDF Text', ''))}")

        return True

    except Exception as e:
        print(f"❌ Erro durante extração: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal"""
    print("🧪 Teste de OCR para E-mails em PDF")
    print("=" * 40)

    # Verificar se foi fornecido um arquivo
    if len(sys.argv) < 2:
        print("❗ Uso: python test_email_ocr.py <caminho_do_pdf>")
        print("📝 Exemplo: python test_email_ocr.py /path/to/email.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    # Verificar se arquivo existe
    if not os.path.exists(pdf_path):
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)

    # Executar teste
    success = test_email_pdf(pdf_path)

    if success:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou")
        sys.exit(1)

if __name__ == "__main__":
    main()