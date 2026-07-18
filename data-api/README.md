# Hanoi Heart Hospital — Data Service (`data-api`)

Spring Boot 3.4 + Java 21 REST service exposing **business master data** for Hanoi
Heart Hospital (hospital info, departments, doctors, schedules, services & prices,
BHYT policies, procedures, support channels, mock appointment slots).

Schema: PostgreSQL `hospital`. Migrations: Flyway. Real seed data parsed from
`data/raw/*.txt`.

## Endpoints (`/data/v1/*`)

| Method | Path |
|--------|------|
| GET | `/data/v1/hospital-info` |
| GET | `/data/v1/departments?active=true` |
| GET | `/data/v1/doctors?department={id}` |
| GET | `/data/v1/doctors/{id}/schedules?from&to` |
| GET | `/data/v1/services?category=&department=` |
| GET | `/data/v1/services/{id}/prices` |
| GET | `/data/v1/bhyt-policies?category=` |
| GET | `/data/v1/procedures?code=QT.25.01` |
| GET | `/data/v1/channels` |
| GET | `/data/v1/appointment-slots?doctor&date` |

List endpoints support pagination `?page&size`. CORS allows
`http://localhost:3000` by default.

## Quick start (docker compose)

From repo root:

```bash
docker compose up --build postgres data-api
# Service: http://localhost:8081/data/v1/hospital-info
```

## Run with Maven

```bash
cp .env.example .env      # edit DB creds
docker compose up -d postgres
mvn -q -DskipTests compile
mvn spring-boot:run
```

## Environment variables

| Var | Default | Description |
|-----|---------|-------------|
| `DB_HOST` | localhost | Postgres host |
| `DB_PORT` | 5432 | Postgres port |
| `DB` | hanoi_heart | Database name |
| `DB_USER` | hanoiheart | DB user |
| `DB_PASS` | hanoiheart | DB password |
| `SERVER_PORT` | 8081 | HTTP port |
| `CORS_ALLOWED_ORIGINS` | http://localhost:3000 | Comma-separated FE origins |

## Database migrations

`src/main/resources/db/migration/`
- `V1__init_hospital.sql` — schema + indexes
- `V2..V8__seed_*.sql` — real data seed (doctors, schedules, services, prices...)

Regenerate seed SQL from raw data:

```bash
python data-api/scripts/parse_schedule.py
python data-api/scripts/parse_services.py
```
