# 🚀 Quick Start - Mastercard PDF Bot

## 1️⃣ Setup Automático (Recomendado)
```bash
./setup.sh
```

## 2️⃣ Setup Manual
```bash
# Instalar dependências
pip3 install -r requirements.txt

# Configurar credenciais
cp .env.example .env
# Edite .env com suas credenciais

# Testar setup
python3 test_setup.py
```

## 3️⃣ Executar Bot
```bash
# Versão simples (recomendada para teste)
python3 mastercard_bot_simple.py

# Ou com variáveis de ambiente
export MASTERCARD_USER="seu-email@empresa.com"
export MASTERCARD_PASS="sua-senha"
python3 mastercard_bot_simple.py
```

## 📁 Arquivos Importantes

- `mastercard_bot_simple.py` - Bot principal (simples)
- `test_setup.py` - Teste das dependências
- `requirements.txt` - Dependências Python
- `.env.example` - Exemplo de configuração
- `setup.sh` - Setup automático

## ⚡ Teste Rápido

1. Configure credenciais em `.env`
2. Execute: `python3 test_setup.py`
3. Se OK, execute: `python3 mastercard_bot_simple.py`

## 🎯 Resultado

PDFs baixados em: `mastercard_pdfs/`
