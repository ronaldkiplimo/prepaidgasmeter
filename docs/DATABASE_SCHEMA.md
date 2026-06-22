# PrepaidGas Kenya — Database Schema

Production PostgreSQL schema for prepaid gas credit vending via M-Pesa and Stron Power meters.

## Architecture

```
Customer → M-Pesa STK Push → Django API → Stron VendingMeterPurchase → Gas Token → SMS/Email
```

## Core Tables

| Table | Description |
|-------|-------------|
| `users` | Auth users with roles: customer, landlord, distributor, admin |
| `customers` | Extended customer profiles with Stron customer ID |
| `meters` | Prepaid gas meters with credit, valve, tamper status |
| `meter_readings` | Consumption history |
| `transactions` | Purchase lifecycle with preview fields |
| `mpesa_transactions` | M-Pesa STK payment records |
| `tokens` | Generated gas credit tokens |
| `stron_transactions` | Stron API call audit log |
| `notifications` | In-app notification log |
| `sms_logs` | SMS delivery log (Africa's Talking / Twilio) |
| `email_logs` | Email delivery log (SendGrid / SMTP) |
| `audit_logs` | Immutable platform audit trail |
| `tariffs` | Gas pricing configuration |
| `system_settings` | M-Pesa, Stron, SMS provider config |

## Stron API Integration

Base URL: `http://www.server-newv.stronpower.com/api`

| Endpoint | Purpose |
|----------|---------|
| `QueryCustomerInfo` | Customer name, address, meter status |
| `QueryMeterInfo` | Meter type, serial, balance |
| `QueryMeterCredit` | Remaining credit/units |
| `QueryCustomerCredit` | Customer balance |
| `VendingMeterPreview` | Preview units before payment |
| `VendingMeterPurchase` | Vend after M-Pesa confirmation |
| `VendingMeter` | Direct vending |
| `ClearCredit` | Admin: reset balance |
| `ClearTamper` | Admin: clear tamper lock |

Auth payload on every request:
```json
{
  "CompanyName": "...",
  "UserName": "...",
  "PassWord": "..."
}
```

## Purchase Flow

1. `POST /api/v1/payments/preview/` — validate meter, preview units via Stron
2. `POST /api/v1/payments/purchase/` — create transaction, initiate STK Push
3. M-Pesa callback → verify payment
4. Celery: `VendingMeterPurchase` → save token
5. Celery: SMS + email notification
6. Dashboard updated

## User Roles

| Role | Capabilities |
|------|-------------|
| Customer | Register, buy gas, manage meters, view history |
| Landlord | Manage tenant meters, view usage/revenue |
| Distributor | Manage customers/meters, view sales |
| Admin | Full access, tariffs, Stron/M-Pesa config, audit logs |
