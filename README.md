# PrepaidGas Kenya

Production-ready prepaid gas credit vending platform for Kenya. Customers buy gas credit via M-Pesa; the system communicates with **Stron Power** prepaid gas meters through the official Vending API v3.0.17.

Comparable to M-Gas, UMS Kenya, Kensmart Utilities, QuickMeters, and PayGo Energy.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, TailwindCSS, React Query, Zustand |
| Backend | Django 5, DRF, SimpleJWT, Celery, Redis |
| Database | PostgreSQL 16 |
| Payments | Safaricom M-Pesa Daraja (STK Push) |
| Vending | Stron Power API v3.0.17 |
| SMS | Africa's Talking / Twilio |
| Email | SendGrid / SMTP |
| Deploy | Docker, GitHub Actions |

## Quick Start

```bash
cp backend/.env.example backend/.env
# Configure STRON_* and MPESA_* credentials
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| Web App | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs/ |
| Stron Swagger | http://www.server-newv.stronpower.com/swagger/docs/v3.0.17 |

**Demo credentials** (after seed):
- Admin: `254700000001` / `Admin@12345`
- Customer: `254712345678` / `Demo@12345`

## Purchase Flow

```
Customer enters meter + amount
  → Stron VendingMeterPreview (units/fees)
  → M-Pesa STK Push
  → Callback verification
  → Stron VendingMeter (or VendingMeterDirectly when configured)
  → Token saved → SMS + Email → Dashboard updated
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register/` | Register (customer/landlord/distributor) |
| POST | `/api/v1/auth/login/` | JWT login (phone + password) |
| GET | `/api/v1/meters/` | List meters |
| POST | `/api/v1/payments/preview/` | Preview gas units |
| POST | `/api/v1/payments/purchase/` | Buy via M-Pesa |
| POST | `/api/v1/payments/mpesa/callback/` | M-Pesa webhook |
| GET | `/api/v1/tokens/history/` | Token history |
| GET | `/api/v1/reports/analytics/` | Admin analytics |
| POST | `/api/v1/stron/clear-credit/` | Admin: clear meter credit |
| POST | `/api/v1/stron/clear-tamper/` | Admin: clear tamper |

## Project Structure

```
prepaidgasmeter/
├── backend/          Django REST API
│   ├── apps/accounts/    Users, roles, customer profiles
│   ├── apps/core/          Tariffs, system settings, seed data
│   ├── apps/meters/        Gas meter management
│   ├── apps/payments/      M-Pesa + transactions
│   ├── apps/tokens/        Stron vending + gas tokens
│   ├── apps/notifications/ SMS/email with delivery logs
│   ├── apps/audit/         Audit logs + admin dashboard
│   └── apps/reports/       Analytics + sales reports
├── web/              Next.js 15 customer + admin portal
├── mobile/           Flutter app (optional)
├── docs/             Database schema
└── docker-compose.yml
```

## Stron Configuration

```env
STRON_BASE_URL=http://www.server-newv.stronpower.com/api
STRON_DIRECT_API_URL=http://www.server-api.stronpower.com/api
STRON_COMPANY_NAME=your-company
STRON_USERNAME=your-username
STRON_PASSWORD=your-password
STRON_VEND_BY_UNIT=false
STRON_USE_DIRECT_VENDING=false
```

Use `STRON_USE_DIRECT_VENDING=true` only when meters/customer pricing are not preloaded in Stron's vending management system and you want to call `VendingMeterDirectly`.

## Production Deployment

See `.github/workflows/` for CI/CD. Deploy with Docker Compose on AWS/DigitalOcean behind Nginx + Cloudflare.

```bash
docker compose -f docker-compose.yml up -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_data
docker compose exec backend python manage.py createsuperuser
```

## License

MIT
