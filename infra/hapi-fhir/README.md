# HAPI FHIR Local Stack

Folder này quản lý HAPI FHIR local cho `chatbot-service`.

Stack này chỉ phục vụ local/dev/test. Không gộp vào `docker-compose.yml` chính vì compose chính đang được CI/CD copy lên VPS để deploy production.

## Thành phần

- HAPI FHIR JPA Server: `http://localhost:8080/fhir`
- PostgreSQL riêng cho HAPI FHIR: host debug `localhost:5434`
- Seed data FHIR tiếng Việt dạng synthetic, nạp qua FHIR REST API

Ứng dụng chỉ được đọc dữ liệu qua FHIR REST endpoint. Không query trực tiếp database Postgres của HAPI.

## Chạy lần đầu

Chạy từ root project:

```powershell
cd D:\PROGRAMMING\Competition\VAIC_2026\VAIC_2026_BanhDaCua

docker compose -f infra/hapi-fhir/docker-compose.yml up -d

python infra/hapi-fhir/scripts/wait_for_hapi.py
python infra/hapi-fhir/scripts/seed_fhir_data.py
python infra/hapi-fhir/scripts/check_connection.py
```

Chatbot local đang dùng:

```env
FHIR_BASE_URL=http://localhost:8080/fhir
```

## Reset dữ liệu FHIR

Lệnh này xóa volume Postgres của HAPI FHIR:

```powershell
docker compose -f infra/hapi-fhir/docker-compose.yml down -v
docker compose -f infra/hapi-fhir/docker-compose.yml up -d

python infra/hapi-fhir/scripts/wait_for_hapi.py
python infra/hapi-fhir/scripts/seed_fhir_data.py
python infra/hapi-fhir/scripts/check_connection.py
```

## Seed data

Seed nằm ở:

```text
infra/hapi-fhir/seed/vietnamese-clinical-data-transaction-bundle.json
```

Dữ liệu hiện có:

- `Patient/vn-patient-001` đến `Patient/vn-patient-020`
- `Encounter`
- `Observation`
- `DiagnosticReport`
- `MedicationRequest`
- Một số resource phụ trợ như `Condition`, `Practitioner`, `Organization`, `Location`

Bundle dùng `PUT` với fixed FHIR ID, nên chạy lại seed sẽ cập nhật resource cũ thay vì tạo bản ghi trùng.

Không seed `Appointment` trong FHIR v1. Lịch hẹn cá nhân sẽ do backend-service/HIS quản lý.

## Kiểm tra trực tiếp FHIR

```powershell
Invoke-RestMethod http://localhost:8080/fhir/metadata
Invoke-RestMethod http://localhost:8080/fhir/Patient/vn-patient-001
Invoke-RestMethod "http://localhost:8080/fhir/Observation?patient=Patient/vn-patient-001&_sort=-date&_count=5"
Invoke-RestMethod "http://localhost:8080/fhir/DiagnosticReport?patient=Patient/vn-patient-001&_sort=-date&_count=5"
Invoke-RestMethod "http://localhost:8080/fhir/MedicationRequest?patient=Patient/vn-patient-001&_sort=-authoredon&_count=5"
```

## Test chatbot bằng Postman

Gửi trực tiếp tới `chatbot-service`:

```json
{
  "sessionId": "test-fhir-001",
  "text": "ket qua xet nghiem cua toi",
  "userRole": "USER",
  "allowedPatientIds": ["vn-patient-001"],
  "context": {},
  "lang": "vi"
}
```

Kỳ vọng:

```text
route = AUTHENTICATED_FHIR
intent = LAB_RESULT
needsHandoff = false
answer có dữ liệu FHIR
```

## Kết nối khi chạy trong Docker

Nếu sau này chatbot chạy cùng Docker network với FHIR stack, dùng service name:

```env
FHIR_BASE_URL=http://hapi-fhir:8080/fhir
```

Hiện tại FHIR stack này chưa thuộc production deploy.

## Dừng stack

```powershell
docker compose -f infra/hapi-fhir/docker-compose.yml down
```

Xóa cả dữ liệu:

```powershell
docker compose -f infra/hapi-fhir/docker-compose.yml down -v
```
