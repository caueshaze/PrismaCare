# PrismaCare
O PrismaCare é uma plataforma voltada ao agendamento e acompanhamento de medicamentos, permitindo que usuários cadastrem remédios, horários de uso e recebam lembretes automáticos por meio de integração com a API do WhatsApp.

## Segurança (Backend)
- Autenticação com JWT `access + refresh` com rotação/revogação de sessão.
- Endpoint legado `/api/login` mantido por compatibilidade temporária.
- Novos endpoints:
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
  - `POST /api/auth/logout`
  - `POST /api/auth/logout-all`

## Configuração de ambiente
Copie `.env.example` e configure as variáveis obrigatórias:
- `JWT_SECRET` (obrigatória)
- `JWT_ALG`
- `ACCESS_TTL_MIN`
- `REFRESH_TTL_DAYS`
- `CORS_ALLOW_ORIGINS`
- `LOGIN_LOCKOUT_THRESHOLD`, `LOGIN_LOCKOUT_MINUTES`, `LOGIN_LOCKOUT_MAX_MINUTES`
- `RATE_LIMIT_LOGIN_PER_MIN`, `RATE_LIMIT_REFRESH_PER_MIN`, `RATE_LIMIT_API_PER_MIN`

## Como rodar o backend (passo a passo)
1. Entrar na pasta do projeto:
```bash
cd /home/caue/PrismaCare
```

2. Criar e ativar ambiente virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar dependências:
```bash
pip install -r requirements.txt
```

4. Criar arquivo de ambiente:
```bash
cp .env.example .env
```

5. Editar `.env` e definir pelo menos:
- `JWT_SECRET` com um valor forte e único.

6. Subir a API (porta padrão 8000):
```bash
uvicorn app.main:app --reload
```

7. Subir a API em outra porta (exemplo 8010):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

8. Acessar documentação:
- Swagger: `http://127.0.0.1:8010/docs` (ou porta escolhida)
- OpenAPI JSON: `http://127.0.0.1:8010/openapi.json`

## Observações importantes
- O backend já carrega `.env` automaticamente na inicialização.
- O endpoint legado `/api/login` segue ativo por compatibilidade.
- O fluxo recomendado é usar os endpoints em `/api/auth/*`.
