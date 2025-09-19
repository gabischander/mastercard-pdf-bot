# 🎯 Mastercard PDF Bot

Bot automatizado para coletar PDFs do Technical Resource Center da Mastercard usando Selenium.

## 🚀 Setup

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciais
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```bash
MASTERCARD_USER=seu-email@empresa.com
MASTERCARD_PASS=sua-senha-mastercard
```

### 3. Instalar ChromeDriver (se necessário)
```bash
# Mac
brew install chromedriver

# Ou será instalado automaticamente pelo webdriver-manager
```

## 🎮 Como usar

### Executar o bot:
```bash
python mastercard_bot.py
```

### Ou configurar via variáveis de ambiente:
```bash
export MASTERCARD_USER="seu-email@empresa.com"
export MASTERCARD_PASS="sua-senha"
python mastercard_bot.py
```

## 📁 Estrutura de pastas

```
mastercard-pdf-bot/
├── mastercard_bot.py          # Bot principal
├── requirements.txt           # Dependências
├── .env.example              # Exemplo de configuração
├── README.md                 # Este arquivo
├── mastercard_pdfs/          # PDFs baixados (criado automaticamente)
├── mastercard_bot.log        # Logs de execução
└── download_report.json      # Relatório de downloads
```

## 📊 O que o bot faz

✅ Abre navegador automatizado (Chrome)
✅ Faz login com suas credenciais
✅ Navega para seção de documentos
✅ Lista todos os PDFs disponíveis
✅ Baixa PDFs para pasta local
✅ Gera relatório detalhado
✅ Logs completos de execução

## ⚙️ Configurações

- **Limite de downloads**: Por padrão baixa apenas 5 PDFs para teste
- **Pasta de download**: `mastercard_pdfs/`
- **Timeout**: 30 segundos por download
- **Logs**: Salvos em `mastercard_bot.log`

## 🔧 Troubleshooting

### Chrome não encontrado:
```bash
# Instalar Chrome se necessário
# O webdriver-manager baixa automaticamente
```

### Problemas de login:
- Verifique se as credenciais estão corretas
- Teste login manual no site primeiro
- Verifique se não há captcha ou 2FA

### Downloads não funcionam:
- Verifique permissões da pasta
- Teste conexão com internet
- Chrome pode estar bloqueando downloads

## 🤖 Para produção

Para usar em produção com todos os PDFs:
```python
# Edite esta linha no código:
collector.collect_pdfs(limit=None)  # Remove o limite
```

## 🌩️ Integração com Google Cloud

Os PDFs podem ser automaticamente enviados para o bucket:
`mastercard-pdf-bot-staging`

Service Account: `mastercard-pdf-bot@infinitepay-staging.iam.gserviceaccount.com`
