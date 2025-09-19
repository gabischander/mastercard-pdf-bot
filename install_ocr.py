#!/usr/bin/env python3
"""
Script para instalação e configuração do OCR (Tesseract)
"""
import os
import platform
import subprocess
import sys

def run_command(command, shell=False):
    """Executa comando do sistema"""
    try:
        result = subprocess.run(
            command if shell else command.split(),
            capture_output=True,
            text=True,
            shell=shell
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_python_packages():
    """Instala pacotes Python necessários"""
    print("📦 Instalando pacotes Python...")
    packages = ["pytesseract", "Pillow", "pdf2image"]

    for package in packages:
        print(f"  Instalando {package}...")
        success, stdout, stderr = run_command(f"{sys.executable} -m pip install {package}")
        if success:
            print(f"  ✅ {package} instalado")
        else:
            print(f"  ❌ Erro ao instalar {package}: {stderr}")
            return False
    return True

def install_tesseract_macos():
    """Instala Tesseract no macOS"""
    print("🍎 Detectado macOS - instalando Tesseract...")

    # Verificar se Homebrew está instalado
    success, stdout, stderr = run_command("which brew")
    if not success:
        print("❌ Homebrew não encontrado. Por favor, instale o Homebrew primeiro:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False

    # Instalar tesseract via Homebrew
    print("  Instalando tesseract via Homebrew...")
    success, stdout, stderr = run_command("brew install tesseract")
    if success:
        print("  ✅ Tesseract instalado via Homebrew")
        return True
    else:
        print(f"  ❌ Erro ao instalar tesseract: {stderr}")
        return False

def install_tesseract_linux():
    """Instala Tesseract no Linux"""
    print("🐧 Detectado Linux - instalando Tesseract...")

    # Tentar diferentes gerenciadores de pacote
    managers = [
        ("apt-get", "sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-por"),
        ("yum", "sudo yum install -y tesseract tesseract-langpack-por"),
        ("dnf", "sudo dnf install -y tesseract tesseract-langpack-por"),
        ("pacman", "sudo pacman -S --noconfirm tesseract tesseract-data-por")
    ]

    for manager, command in managers:
        success, stdout, stderr = run_command(f"which {manager}")
        if success:
            print(f"  Usando {manager}...")
            success, stdout, stderr = run_command(command, shell=True)
            if success:
                print(f"  ✅ Tesseract instalado via {manager}")
                return True
            else:
                print(f"  ❌ Erro com {manager}: {stderr}")

    print("❌ Não foi possível instalar automaticamente. Instale manualmente:")
    print("   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-por")
    print("   CentOS/RHEL: sudo yum install tesseract tesseract-langpack-por")
    return False

def install_tesseract_windows():
    """Instruções para Windows"""
    print("🪟 Detectado Windows")
    print("❗ Instalação manual necessária:")
    print("1. Baixe o instalador do Tesseract:")
    print("   https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Execute o instalador como administrador")
    print("3. Instale no caminho padrão: C:\\Program Files\\Tesseract-OCR")
    print("4. Adicione ao PATH do sistema ou o script detectará automaticamente")
    return True

def test_tesseract():
    """Testa se o Tesseract está funcionando"""
    print("🧪 Testando instalação do Tesseract...")

    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✅ Tesseract funcionando - Versão: {version}")

        # Testar idiomas disponíveis
        langs = pytesseract.get_languages()
        print(f"  📝 Idiomas disponíveis: {', '.join(langs)}")

        if 'por' in langs:
            print("  ✅ Português detectado")
        else:
            print("  ⚠️ Português não encontrado - OCR funcionará apenas em inglês")

        return True

    except Exception as e:
        print(f"  ❌ Erro ao testar Tesseract: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Instalador OCR para Mastercard PDF Bot")
    print("=" * 50)

    # Detectar sistema operacional
    system = platform.system().lower()
    print(f"💻 Sistema: {platform.system()} {platform.release()}")

    # Instalar pacotes Python
    if not install_python_packages():
        print("❌ Falha na instalação dos pacotes Python")
        sys.exit(1)

    # Instalar Tesseract baseado no SO
    if system == "darwin":  # macOS
        if not install_tesseract_macos():
            sys.exit(1)
    elif system == "linux":
        if not install_tesseract_linux():
            sys.exit(1)
    elif system == "windows":
        install_tesseract_windows()
        print("\n⏸️ Complete a instalação manual do Windows e execute novamente para testar")
        sys.exit(0)
    else:
        print(f"❌ Sistema operacional não suportado: {system}")
        sys.exit(1)

    # Testar instalação
    print("\n" + "=" * 50)
    if test_tesseract():
        print("🎉 Instalação concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Execute: python -c \"from cardbrand-updates.data_processing.extractors.ocr_extractor import setup_tesseract; print('OCR:', setup_tesseract())\"")
        print("2. Teste com um PDF de e-mail usando seu bot")
    else:
        print("❌ Instalação incompleta - verifique os erros acima")
        sys.exit(1)

if __name__ == "__main__":
    main()