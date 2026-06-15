# Database Schema

PostgreSQL schema for the Prepaid Electricity Token Vending Platform.

## Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ meters : owns
    users ||--o{ transactions : makes
    users ||--o{ notifications : receives
    users ||--o{ audit_logs : generates
    meters ||--o{ transactions : "used in"
    transactions ||--|| payments : has
    transactions ||--o| electricity_tokens : generates
    transactions ||--o{ notifications : triggers

    users {
        uuid id PK
        varchar username
        varchar email
        varchar phone_number UK
        varchar national_id
        boolean is_verified
        timestamp created_at
        timestamp updated_at
    }

    meters {
        uuid id PK
        uuid user_id FK
        varchar meter_number
        varchar account_number
        varchar nickname
        varchar meter_type
        varchar utility_provider
        varchar location
        boolean is_active
        boolean is_primary
        timestamp created_at
        timestamp updated_at
    }

    transactions {
        uuid id PK
        varchar reference UK
        uuid user_id FK
        uuid meter_id FK
        decimal amount
        varchar status
        varchar phone_number
        text failure_reason
        jsonb metadata
        timestamp created_at
        timestamp updated_at
        timestamp completed_at
    }

    payments {
        uuid id PK
        uuid transaction_id FK UK
        varchar method
        varchar status
        decimal amount
        varchar phone_number
        varchar checkout_request_id
        varchar merchant_request_id
        varchar mpesa_receipt_number
        timestamp mpesa_transaction_date
        jsonb callback_payload
        timestamp created_at
        timestamp updated_at
    }

    electricity_tokens {
        uuid id PK
        uuid transaction_id FK UK
        varchar token
        decimal token_units
        decimal token_amount
        varchar meter_number
        varchar stron_receipt_number
        varchar status
        jsonb stron_response
        timestamp generated_at
        timestamp delivered_at
    }

    notifications {
        uuid id PK
        uuid user_id FK
        varchar channel
        varchar notification_type
        varchar recipient
        varchar subject
        text message
        varchar status
        uuid transaction_id FK
        text error_message
        timestamp sent_at
        timestamp created_at
    }

    audit_logs {
        uuid id PK
        uuid user_id FK
        varchar action
        varchar resource_type
        varchar resource_id
        jsonb details
        inet ip_address
        text user_agent
        timestamp created_at
    }
```

## Tables

### users
Extended Django auth user. Phone number is the login identifier.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| username | VARCHAR(150) | UNIQUE, NOT NULL |
| email | VARCHAR(254) | |
| phone_number | VARCHAR(15) | UNIQUE, NOT NULL, INDEX |
| national_id | VARCHAR(20) | |
| is_verified | BOOLEAN | DEFAULT FALSE |
| password | VARCHAR(128) | NOT NULL |
| is_staff | BOOLEAN | DEFAULT FALSE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | AUTO |
| updated_at | TIMESTAMPTZ | AUTO |

### meters
Customer electricity meters. Soft-deleted via `is_active`.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users, NOT NULL |
| meter_number | VARCHAR(20) | NOT NULL, INDEX |
| account_number | VARCHAR(30) | |
| nickname | VARCHAR(100) | |
| meter_type | VARCHAR(20) | single_phase, three_phase, prepaid |
| utility_provider | VARCHAR(100) | DEFAULT 'Kenya Power' |
| location | VARCHAR(255) | |
| is_active | BOOLEAN | DEFAULT TRUE |
| is_primary | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMPTZ | AUTO |
| updated_at | TIMESTAMPTZ | AUTO |

**Unique:** (user_id, meter_number)

### transactions
End-to-end purchase lifecycle from payment to token delivery.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| reference | VARCHAR(50) | UNIQUE, NOT NULL, INDEX |
| user_id | UUID | FK → users, PROTECT |
| meter_id | UUID | FK → meters, PROTECT |
| amount | DECIMAL(12,2) | NOT NULL |
| status | VARCHAR(30) | INDEX |
| phone_number | VARCHAR(15) | NOT NULL |
| failure_reason | TEXT | |
| metadata | JSONB | DEFAULT {} |
| created_at | TIMESTAMPTZ | AUTO, INDEX |
| updated_at | TIMESTAMPTZ | AUTO |
| completed_at | TIMESTAMPTZ | |

**Status values:** pending → payment_initiated → payment_confirmed → token_generating → completed | failed | refunded

### payments
M-Pesa STK Push payment records (1:1 with transactions).

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| transaction_id | UUID | FK → transactions, UNIQUE |
| method | VARCHAR(20) | mpesa_stk, mpesa_paybill |
| status | VARCHAR(20) | INDEX |
| amount | DECIMAL(12,2) | NOT NULL |
| phone_number | VARCHAR(15) | NOT NULL |
| checkout_request_id | VARCHAR(100) | INDEX |
| merchant_request_id | VARCHAR(100) | |
| mpesa_receipt_number | VARCHAR(50) | INDEX |
| mpesa_transaction_date | TIMESTAMPTZ | |
| callback_payload | JSONB | DEFAULT {} |
| created_at | TIMESTAMPTZ | AUTO |
| updated_at | TIMESTAMPTZ | AUTO |

### electricity_tokens
Generated prepaid tokens from Stron Vending API.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| transaction_id | UUID | FK → transactions, UNIQUE |
| token | VARCHAR(100) | NOT NULL |
| token_units | DECIMAL(12,2) | DEFAULT 0 |
| token_amount | DECIMAL(12,2) | NOT NULL |
| meter_number | VARCHAR(20) | NOT NULL, INDEX |
| stron_receipt_number | VARCHAR(50) | |
| status | VARCHAR(20) | pending, generated, delivered, failed |
| stron_response | JSONB | DEFAULT {} |
| generated_at | TIMESTAMPTZ | AUTO |
| delivered_at | TIMESTAMPTZ | |

### notifications
SMS and email delivery log.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users |
| channel | VARCHAR(10) | sms, email, push |
| notification_type | VARCHAR(30) | |
| recipient | VARCHAR(255) | NOT NULL |
| subject | VARCHAR(255) | |
| message | TEXT | NOT NULL |
| status | VARCHAR(20) | pending, sent, failed |
| transaction_id | UUID | FK → transactions, NULL |
| error_message | TEXT | |
| sent_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | AUTO |

### audit_logs
Immutable audit trail. No updates or deletes permitted via admin.

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FK → users, NULL |
| action | VARCHAR(50) | NOT NULL, INDEX |
| resource_type | VARCHAR(50) | NOT NULL, INDEX |
| resource_id | VARCHAR(50) | |
| details | JSONB | DEFAULT {} |
| ip_address | INET | |
| user_agent | TEXT | |
| created_at | TIMESTAMPTZ | AUTO, INDEX |

## Indexes

- `users.phone_number` — login lookup
- `meters.meter_number` — meter search
- `meters(user_id, is_active)` — user meter list
- `transactions.reference` — payment reconciliation
- `transactions(user_id, status)` — user transaction filter
- `transactions.created_at` — reporting
- `payments.checkout_request_id` — M-Pesa callback lookup
- `payments.mpesa_receipt_number` — receipt search
- `audit_logs(action, created_at)` — audit queries
- `audit_logs(user_id, created_at)` — user activity

## Purchase Flow

```
User → POST /purchase/ → Transaction(payment_initiated)
     → M-Pesa STK Push → Payment(pending)
     → User confirms on phone
     → M-Pesa callback → Payment(success) → Transaction(payment_confirmed)
     → Celery: generate_token_task → Stron API → ElectricityToken(generated)
     → Celery: send_token_notification_task → SMS + Email → Token(delivered)
     → Transaction(completed)
```
