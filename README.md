<h1 align="center">
  <br>
  <img src="./assets/logo.png" alt="PrismaCare" width="120">
  <br>
  PrismaCare
  <br>
</h1>

<p align="center">
  Plataforma de gerenciamento de medicamentos para idosos — agendamentos, confirmações de dose e alertas automáticos para cuidadores.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white">
  <img alt="React Native" src="https://img.shields.io/badge/React_Native-0.81-61DAFB?style=flat-square&logo=react&logoColor=black">
  <img alt="Expo" src="https://img.shields.io/badge/Expo-54-000020?style=flat-square&logo=expo&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat-square&logo=typescript&logoColor=white">
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green?style=flat-square">
</p>

---

## Sobre o projeto

O PrismaCare é um sistema acadêmico voltado ao gerenciamento de medicamentos, pensado principalmente para idosos. O usuário cadastra seus remédios, define horários de uso e recebe lembretes automáticos. Se uma dose não for confirmada dentro do prazo, o sistema notifica os contatos de segurança (familiares ou cuidadores) via WhatsApp.

**Stack principal:**

| Camada | Tecnologia |
|---|---|
| API | FastAPI + Uvicorn |
| Banco de dados | SQLite |
| Autenticação | JWT (access + refresh com rotação) |
| Agendamento | APScheduler |
| Validação | Pydantic v2 |
| Mobile | React Native + Expo |
| Linguagem mobile | TypeScript (strict) |
| Navegação | React Navigation v7 |
| Infraestrutura | Docker + Nginx + SSL |

---

## Funcionalidades

- Cadastro e autenticação de usuários com JWT
- Login com Google em Android development build
- CRUD de medicamentos, contatos de segurança e agendamentos
- Listagem automática de doses do dia com status (`PENDENTE`, `CONFIRMADO`, `ATRASADO`)
- Confirmação de dose pelo app mobile
- Monitor automático: doses não confirmadas em 30 min geram notificação para os contatos
- Anti-duplicata de notificações por índice único + verificação na aplicação
- Rate limiting por IP e por usuário (login, refresh e API geral)
- Bloqueio progressivo de login após falhas consecutivas
- Revogação de sessão individual ou total (`logout-all`)
- Isolamento total de dados por usuário autenticado

---

## Estrutura do projeto

```
PrismaCare/
│
├── app/                          # Backend Python / FastAPI
│   ├── main.py                   # Entry point, routers, lifespan, APScheduler
│   ├── database.py               # Conexão SQLite e criação do schema
│   ├── security.py               # JWT, bcrypt, dependency injection
│   │
│   ├── core/
│   │   ├── config.py             # Settings carregadas do .env
│   │   ├── constants.py          # Enums de status (PENDENTE, CONFIRMADO, etc.)
│   │   ├── audit.py              # Log de eventos de autenticação
│   │   ├── rate_limit.py         # Rate limiter por IP e usuário
│   │   └── security_controls.py  # Enforcers e extração de IP
│   │
│   ├── middleware/
│   │   └── security_middleware.py # Headers de segurança, rate limit, log de erros
│   │
│   ├── routes/                   # Endpoints da API (um arquivo por domínio)
│   │   ├── auth_route.py         # /api/auth/*
│   │   ├── user_route.py         # /api/users/*
│   │   ├── medicamento_route.py  # /api/medicamentos/*
│   │   ├── contato_route.py      # /api/contatos/*
│   │   ├── agendamento_route.py  # /api/agendamentos/*
│   │   ├── dose_route.py         # /api/doses/*
│   │   ├── historico_route.py    # /api/doses/historico
│   │   ├── confirmacao_route.py  # /api/confirmacoes/*
│   │   ├── notificacao_route.py  # /api/notificacoes/*
│   │   └── monitor_route.py      # /api/monitor/*
│   │
│   ├── repositories/             # Acesso ao banco (queries SQLite)
│   │   ├── auth_repo.py
│   │   ├── user_repo.py
│   │   ├── medicamento_repo.py
│   │   ├── contato_repo.py
│   │   ├── agendamento_repo.py
│   │   ├── dose_repo.py
│   │   ├── historico_repo.py
│   │   ├── confirmacao_repo.py
│   │   └── notificacao_repo.py
│   │
│   ├── schemas/                  # Validação com Pydantic v2
│   │   ├── user_schema.py
│   │   ├── medicamento_schema.py
│   │   ├── contato_schema.py
│   │   ├── agendamento_schema.py
│   │   ├── dose_schema.py
│   │   ├── historico_schema.py
│   │   ├── confirmacao_schema.py
│   │   └── notificacao_schema.py
│   │
│   └── services/
│       └── monitor_service.py    # varrer_e_notificar() — varredura de doses atrasadas
│
├── src/                          # Frontend React Native / Expo
│   ├── screens/
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── ForgotPasswordScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── MedicamentosScreen.tsx
│   │   ├── AgendamentosScreen.tsx
│   │   ├── ContatosScreen.tsx
│   │   └── DosesScreen.tsx
│   │
│   ├── components/
│   │   ├── InputField.tsx        # Input reutilizável com ícone e validação
│   │   └── PrimaryButton.tsx     # Botão com gradiente e estado de loading
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx       # Contexto de autenticação (signIn / signOut)
│   │
│   ├── services/
│   │   └── api.ts                # Cliente HTTP com Bearer token
│   │
│   └── theme/
│       └── colors.ts             # Paleta de cores do sistema
│
├── assets/                       # Ícones e imagens do app
├── App.tsx                       # Navegação principal (Stack Navigator)
├── index.ts                      # Entry point do Expo
├── docker-compose.yml            # Backend + Nginx em containers
├── Dockerfile                    # Imagem Python 3.13-slim
├── nginx.conf                    # Reverse proxy com SSL (Let's Encrypt)
├── requirements.txt              # Dependências Python
├── package.json                  # Dependências Node / Expo
├── tsconfig.json                 # TypeScript strict mode
└── .env.example                  # Variáveis de ambiente (template)
```

---

## Banco de dados

O schema é criado automaticamente na primeira execução. Tabelas e relacionamentos:

```
users
 └── medicamentos        (id_usuario → users.id)
      └── agendamentos   (id_medicamento → medicamentos.id)
           └── confirmacoes (id_agendamento → agendamentos.id)
                └── notificacoes (id_confirmacao → confirmacoes.id)

users
 └── contatos            (id_usuario → users.id)
      └── notificacoes   (id_contato → contatos.id)

users
 └── refresh_tokens      (user_id → users.id)
 └── auth_events         (user_id → users.id)
```

Campos extras de autenticação social ficam diretamente em `users`:

- `auth_provider`
- `google_sub`
- `avatar_url`

---

## Fluxo principal

```
Usuário cria conta
       ↓
   Faz login → recebe access token (15 min) + refresh token (14 dias)
       ↓
   Cadastra medicamento
       ↓
   Cria agendamento (horário + frequência + datas)
       ↓
   GET /api/doses/hoje → sistema gera confirmações PENDENTE automaticamente
       ↓
   Usuário confirma dose → status vira CONFIRMADO
       ↓
   Se não confirmada em 30 min → APScheduler marca como ATRASADO
       ↓
   Notificação gerada para contatos de segurança do usuário
```

---

## Endpoints da API

| Grupo | Método | Endpoint | Descrição |
|---|---|---|---|
| **Auth** | POST | `/api/auth/login` | Login com email e senha |
| | POST | `/api/auth/google` | Login com Google via `id_token` validado no backend |
| | POST | `/api/auth/refresh` | Renovar access token |
| | POST | `/api/auth/logout` | Revogar sessão atual |
| | POST | `/api/auth/logout-all` | Revogar todas as sessões |
| **Usuários** | POST | `/api/users` | Criar conta (público) |
| | GET | `/api/users/me` | Perfil do usuário autenticado |
| | DELETE | `/api/users/{id}` | Deletar conta |
| **Medicamentos** | GET/POST | `/api/medicamentos` | Listar / criar |
| | GET/PUT/DELETE | `/api/medicamentos/{id}` | Buscar / atualizar / remover |
| **Contatos** | GET/POST | `/api/contatos` | Listar / criar |
| | GET/PATCH/DELETE | `/api/contatos/{id}` | Buscar / atualizar / remover |
| **Agendamentos** | GET/POST | `/api/agendamentos` | Listar / criar |
| | GET/PATCH/DELETE | `/api/agendamentos/{id}` | Buscar / atualizar / remover |
| **Doses** | GET | `/api/doses/hoje` | Doses do dia com status |
| | GET | `/api/doses/historico?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD` | Histórico autenticado de doses por período. Se omitido, usa os últimos 30 dias |
| **Confirmações** | GET/POST | `/api/confirmacoes` | Listar / criar |
| | PUT | `/api/confirmacoes/{id}/confirmar` | Confirmar dose tomada |
| **Notificações** | GET/POST | `/api/notificacoes` | Listar / criar |
| **Monitor** | POST | `/api/monitor/varredura` | Disparar varredura manual, controlada por `ENABLE_MANUAL_MONITOR_ENDPOINT` |

Documentação interativa disponível em `/docs` (Swagger UI) após subir o backend.

---

## Segurança

- **JWT**: access token com TTL de 15 min + refresh token de 14 dias com rotação
- **bcrypt**: hash de senha com custo padrão
- **Refresh token**: armazenado como SHA-256 no banco; revogação individual e total
- **Rate limiting**: 10 req/min no login, 20/min no refresh, 120/min na API geral
- **Login lockout**: bloqueio progressivo após 5 falhas (configurável, máx. 60 min)
- **Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store` em rotas de auth
- **Isolamento**: todos os dados filtrados pelo `user_id` extraído do JWT
- **Auditoria**: log de eventos de autenticação sem exposição de senhas ou tokens

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e configure:

```env
JWT_SECRET=           # obrigatório — gere com: openssl rand -base64 32
JWT_ALG=HS256
GOOGLE_WEB_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
ACCESS_TTL_MIN=15
REFRESH_TTL_DAYS=14
CORS_ALLOW_ORIGINS=http://localhost:8081
ENABLE_MANUAL_MONITOR_ENDPOINT=false

LOGIN_LOCKOUT_THRESHOLD=5
LOGIN_LOCKOUT_MINUTES=15
LOGIN_LOCKOUT_MAX_MINUTES=60

RATE_LIMIT_LOGIN_PER_MIN=10
RATE_LIMIT_REFRESH_PER_MIN=20
RATE_LIMIT_API_PER_MIN=120
EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
```

Em VPS/produção, mantenha `ENABLE_MANUAL_MONITOR_ENDPOINT=false`. Essa flag bloqueia apenas o disparo manual via `POST /api/monitor/varredura`; a execução automática do APScheduler continua funcionando normalmente.

### Google Sign-In

- `GOOGLE_WEB_CLIENT_ID` é usado pelo backend como `audience` na validação do token Google.
- `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` é usado pelo app como `webClientId`.
- Além do Web Client ID, o Google Cloud também precisa de um OAuth client Android com package `com.caueshaze.prismacare` e os SHA-1/SHA-256 do development build.
- Google Sign-In não funciona no Expo Go. A validação deve ser feita em Android development build.

---

## Como rodar o backend

### Linux / macOS

```bash
# 1. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o ambiente
cp .env.example .env
# Edite .env e defina JWT_SECRET

# 4. Suba a API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Se aparecer erro de política de execução no Windows:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Com Docker

```bash
docker compose up --build
```

O backend sobe na porta `8743` atrás do Nginx. Configure o SSL com Certbot conforme `nginx.conf`.

**Swagger UI:** `http://localhost:8000/docs`

---

## Como rodar o frontend

```bash
# Instale as dependências
npm install

# Inicie o Expo
npm start

# Ou diretamente por plataforma
npm run android
npm run ios
```

Certifique-se de que o backend esteja acessível e defina `EXPO_PUBLIC_API_BASE_URL` no `.env` apontando para o endereço correto (veja `.env.example`).

---

## Observações

- O banco `prismacare.db` é criado automaticamente na primeira execução — não commitar.
- O APScheduler inicia junto com o servidor e varre doses atrasadas a cada 5 minutos.
- A integração real com WhatsApp ainda não está implementada; notificações são criadas com status `AGUARDANDO`.
- Recuperação de senha está em desenvolvimento.

---

## Licença

MIT © [Cauê Araujo](https://github.com/caueshaze)
