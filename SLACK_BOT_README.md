# 🤖 Bot Slack - Confluence

Este é o bot Slack que irá integrar com o Confluence para pesquisar documentos automaticamente.

## 🚀 Configuração Rápida

### 1. Instalar Dependências
```bash
python setup_slack_bot.py
```

### 2. Configurar Tokens
Edite o arquivo `slack_config.py` e substitua os tokens:

```python
SLACK_BOT_TOKEN = "xoxb-SEU-TOKEN-REAL-AQUI"
SLACK_APP_TOKEN = "xapp-SEU-TOKEN-REAL-AQUI"
```

### 3. Iniciar o Bot
```bash
python app.py
```

## 📋 Como Obter os Tokens

### Bot Token (xoxb-...)
1. Vá para [api.slack.com/apps](https://api.slack.com/apps)
2. Selecione seu app
3. Vá em "OAuth & Permissions"
4. Copie o "Bot User OAuth Token"

### App Token (xapp-...)
1. No mesmo app, vá em "Basic Information"
2. Role até "App-Level Tokens"
3. Crie um novo token com escopo `connections:write`
4. Copie o token gerado

## 🧪 Testando o Bot

### 1. Convidar para Canal
No Slack, digite:
```
/invite @nomedoseubot
```

### 2. Testar Menção
Mencione o bot:
```
@nomedoseubot Olá!
```

### 3. Testar Comandos
```
/confluence
/help
```

## 🔧 Funcionalidades Atuais

- ✅ Responde a menções (@bot)
- ✅ Comando `/confluence` (em desenvolvimento)
- ✅ Comando `/help`
- ✅ Conexão segura via Socket Mode

## 🚧 Próximas Funcionalidades

- 🔄 Integração com Confluence
- 🔄 Pesquisa de documentos
- 🔄 Respostas inteligentes
- 🔄 Cache de resultados

## 🛠️ Estrutura do Projeto

```
├── app.py                 # Bot principal
├── slack_config.py        # Configuração de tokens
├── setup_slack_bot.py     # Script de configuração
├── requirements.txt       # Dependências
└── SLACK_BOT_README.md    # Este arquivo
```

## ⚠️ Segurança

- **NUNCA** compartilhe os tokens
- **NUNCA** suba o arquivo `slack_config.py` para repositórios públicos
- Use variáveis de ambiente em produção

## 🐛 Solução de Problemas

### Bot não responde
1. Verifique se os tokens estão corretos
2. Confirme que o bot foi convidado para o canal
3. Verifique se o Socket Mode está ativado no app

### Erro de conexão
1. Verifique sua conexão com a internet
2. Confirme que o App Token tem escopo `connections:write`
3. Verifique se o bot está online no Slack

## 📞 Suporte

Se encontrar problemas, verifique:
1. Logs do terminal onde executou `python app.py`
2. Configuração dos tokens
3. Permissões do app no Slack
