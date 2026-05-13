# PrismaCare
O PrismaCare é uma plataforma voltada ao agendamento e acompanhamento de medicamentos, permitindo que usuários cadastrem remédios, horários de uso e recebam lembretes automáticos por meio de integração com a API do WhatsApp.

## Segurança (Backend)
- Autenticação com JWT `access + refresh` com rotação/revogação de sessão.
- Endpoints de autenticação:
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
  - `POST /api/auth/logout`
  - `POST /api/auth/logout-all`

## Monitor de Doses Atrasadas
O sistema possui um motor de varredura automático que identifica confirmações com mais de 30 minutos de atraso e cria notificações para os contatos de segurança do usuário.

- **Execução automática:** a cada 5 minutos via APScheduler (inicia junto com o servidor).
- **Trigger manual:** `POST /api/monitor/varredura` (requer autenticação JWT).
- **Anti-duplicata:** duas camadas — verificação na aplicação + `UNIQUE INDEX` no banco.
- **Fluxo:** `confirmacao.status = 'pendente'` → notificação criada → `status` atualizado para `'atrasado_notificado'`.

## Configuração de ambiente
Copie `.env.example` e configure as variáveis obrigatórias:
- `JWT_SECRET` (obrigatória)
- `JWT_ALG`
- `ACCESS_TTL_MIN`
- `REFRESH_TTL_DAYS`
- `CORS_ALLOW_ORIGINS`
- `LOGIN_LOCKOUT_THRESHOLD`, `LOGIN_LOCKOUT_MINUTES`, `LOGIN_LOCKOUT_MAX_MINUTES`
- `RATE_LIMIT_LOGIN_PER_MIN`, `RATE_LIMIT_REFRESH_PER_MIN`, `RATE_LIMIT_API_PER_MIN`

---

## Como rodar o backend — Linux

1. Entre na pasta do projeto:
```bash
cd ~/PrismaCare
```

2. Crie e ative o ambiente virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Crie o arquivo de ambiente:
```bash
cp .env.example .env
```

5. Edite `.env` e defina pelo menos `JWT_SECRET` com um valor forte e único.

6. Suba a API (porta padrão 8000):
```bash
uvicorn app.main:app --reload
```

7. Ou em outra porta (exemplo 8010):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

8. Acesse a documentação:
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## Como rodar o backend — Windows

1. Abra o **PowerShell** e entre na pasta do projeto:
```powershell
cd $HOME\PrismaCare
```

2. Crie o ambiente virtual:
```powershell
python -m venv .venv
```

3. Ative o ambiente virtual:
```powershell
.venv\Scripts\Activate.ps1
```
> Se aparecer erro de política de execução, rode antes:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

4. Instale as dependências:
```powershell
pip install -r requirements.txt
```

5. Crie o arquivo de ambiente copiando o exemplo:
```powershell
copy .env.example .env
```

6. Abra `.env` em qualquer editor e defina pelo menos `JWT_SECRET` com um valor forte e único.

7. Suba a API (porta padrão 8000):
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. Acesse a documentação:
- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## Observações
- O banco SQLite (`prismacare.db`) é criado automaticamente na primeira execução.
- O backend carrega `.env` automaticamente na inicialização.
- Use os endpoints em `/api/auth/*` para autenticação.
