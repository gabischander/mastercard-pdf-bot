#!/bin/bash
echo "🚀 Setup do Mastercard PDF Bot"
echo "==============================="

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    echo "Instale Python3 primeiro"
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado!"
    echo "Instale pip3 primeiro"
    exit 1
fi

echo "✅ pip3 encontrado"

# Instala dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# Verifica se Chrome está instalado (Mac)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ ! -d "/Applications/Google Chrome.app" ]; then
        echo "⚠️  Chrome não encontrado em /Applications/"
        echo "Instale o Google Chrome ou o ChromeDriver será baixado automaticamente"
    else
        echo "✅ Google Chrome encontrado"
    fi
fi

# Cria arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "✏️  Configure suas credenciais em .env"
else
    echo "✅ Arquivo .env já existe"
fi

# Testa setup
echo "🧪 Testando setup..."
python3 test_setup.py

echo ""
echo "🎉 Setup concluído!"
echo ""
echo "Para usar o bot:"
echo "1. Configure suas credenciais em .env"
echo "2. Execute: python3 mastercard_bot_simple.py"
echo ""
