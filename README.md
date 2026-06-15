# Prepaid Electricity Token Vending Platform

Production-ready platform for purchasing prepaid electricity tokens via M-Pesa STK Push, with token generation through the Stron Vending API.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐
│  React Web  │     │ Flutter App │     │  Django REST API │
│  (Vite)     │────▶│  (Mobile)   │────▶│  + PostgreSQL    │
└─────────────┘     └─────────────┘     └────────┬─────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────┐
                    │                              │                  │
              ┌─────▼─────┐              ┌─────────▼────────┐  ┌─────▼─────┐
              │  M-Pesa   │              │  Stron Vending   │  │  Celery   │
              │  Daraja   │              │  API             │  │  + Redis  │
              └───────────┘              └──────────────────┘  └───────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5, Django REST Framework, SimpleJWT |
| Database | PostgreSQL 16 |
| Task Queue | Celery + Redis |
| Frontend | React 18, Vite, TailwindCSS |
| Mobile | Flutter 3 |
| Payments | M-Pesa Daraja STK Push |
| Vending | Stron Vending API |
| Docs | drf-spectacular (OpenAPI/Swagger) |
| Deployment | Docker Compose, GitHub Actions CI/CD |

## Features

- User registration and JWT authentication (phone number login)
- Multiple meter management per user
- M-Pesa STK Push payment initiation
- Payment webhook verification with idempotency
- Async token generation via Stron Vending API
- SMS and email token delivery notifications
- Transaction history and token history
- Admin dashboard with revenue and audit stats
- Immutable audit logging
- OpenAPI documentation at `/api/docs/`

## Quick Start

### Prerequisites

- Docker and Docker Compose
- M-Pesa Daraja sandbox credentials
- Stron Vending API credentials

### 1. Clone and configure

```bash
git clone <repo-url> prepaidgasmeter
cd prepaidgasmeter
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials
```

### 2. Start with Docker

```bash
docker compose up -d --build
```

Services:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 3. Create admin user

```bash
docker compose exec backend python manage.py createsuperuser
```

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
# In another terminal:
celery -A config worker -l info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Mobile:**
```bash
cd mobile
flutter pub get
flutter run --dart-define=API_URL=http://10.0.2.2:8000/api/v1
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register user |
| POST | `/api/v1/auth/login/` | Login (JWT) |
| POST | `/api/v1/auth/logout/` | Logout (blacklist token) |
| GET | `/api/v1/auth/profile/` | User profile |
| GET/POST | `/api/v1/meters/` | List/add meters |
| POST | `/api/v1/payments/purchase/` | Initiate token purchase |
| GET | `/api/v1/payments/transactions/` | Transaction history |
| POST | `/api/v1/payments/mpesa/callback/` | M-Pesa webhook |
| GET | `/api/v1/tokens/history/` | Token history |
| GET | `/api/v1/audit/dashboard/` | Admin dashboard stats |
| GET | `/api/v1/audit/logs/` | Admin audit logs |
| GET | `/api/docs/` | Swagger UI |

## Purchase Flow

1. User selects meter and amount → `POST /payments/purchase/`
2. Backend creates transaction and initiates M-Pesa STK Push
3. User confirms payment on phone
4. M-Pesa sends callback → `POST /payments/mpesa/callback/`
5. Celery task calls Stron API to generate token
6. Celery task sends SMS + email with token
7. Transaction marked as completed

## Database Schema

See [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for the full ERD and table definitions.

## Project Structure

```
prepaidgasmeter/
├── backend/           # Django REST API
│   ├── apps/
│   │   ├── accounts/  # User auth
│   │   ├── meters/    # Meter management
│   │   ├── payments/  # M-Pesa + transactions
│   │   ├── tokens/    # Stron vending + tokens
│   │   ├── notifications/  # SMS + email
│   │   └── audit/     # Audit logs + admin dashboard
│   └── config/        # Django settings
├── frontend/          # React + Vite + TailwindCSS
├── mobile/            # Flutter app
├── docs/              # Database schema docs
├── .github/workflows/ # CI/CD pipelines
└── docker-compose.yml
```

## CI/CD

- **backend.yml** — Python tests, lint, Docker build on push/PR
- **frontend.yml** — Node build and Docker build
- **deploy.yml** — Push images to registry and deploy via SSH (requires secrets)

Required GitHub secrets for deployment:
- `REGISTRY_URL`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`
- `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`

## Environment Variables

See [backend/.env.example](backend/.env.example) for all configuration options including M-Pesa, Stron, email, and SMS settings.

## License

MIT
