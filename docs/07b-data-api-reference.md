# 07b — Data API Reference (Spring Boot `/data/v1`)

> Postman-ready reference for the **Spring Boot Data Service** (`data-api` module).
> Source of truth: `data-api/src/main/java/com/hanoiheart/dataapi/controller/*.java` + `dto/*.java`.
> Contract baseline: [`07-api-design.md`](./07-api-design.md) §B. **Where code differs from §B, this doc reflects the code.**

---

## 0. Conventions

### Base URL & Port

| Env | Base URL |
|---|---|
| Local dev | `http://localhost:8081` |
| Port source | `application.yml` → `server.port: ${SERVER_PORT:8081}` (override via env) |
| Route prefix | `/data/v1` (all controllers under `/data/v1/...`) |

### Authentication — `X-API-Key` (demo, optional)

Controlled by `ApiKeyFilter` (`config/ApiKeyFilter.java`):

- If `hanoi-heart.api-key` (env: `DATA_API_KEY`) is **blank** → filter is **no-op**, all `/data/**` endpoints are **open**. This is the default local-dev behavior.
- If `DATA_API_KEY` is **set** → every `/data/**` request MUST carry header `X-API-Key: <key>`. Missing/invalid → **401** `{"error":{"code":"unauthorized","message":"Missing or invalid X-API-Key"}}`.

```
X-API-Key: demo-key-123
```

### CORS

`CorsConfig` allows origin `${CORS_ALLOWED_ORIGINS:-http://localhost:3000}` on path `/data/**`, methods `GET,POST,PUT,DELETE,OPTIONS`, all headers, exposed header `X-Total-Count`, credentials allowed, max-age 3600s.

### Common Error Envelope

All errors return `{"error":{"code","message"}}` (produced by `GlobalExceptionHandler`).

| HTTP | `code` | Trigger |
|---|---|---|
| 400 | `bad_request` | `IllegalArgumentException` (business validation) OR `MethodArgumentTypeMismatchException` (e.g. non-numeric `id` path param, bad date format) |
| 401 | `unauthorized` | Missing/invalid `X-API-Key` (only when `DATA_API_KEY` is configured) |
| 404 | `not_found` | `NoSuchElementException` / `ResourceNotFoundException` / `EntityNotFoundException` / `EmptyResultDataAccessException` — currently thrown by `DoctorService.get` & `HospitalInfoService.getCurrent` on missing row |
| 500 | `internal_error` | Catch-all `@ExceptionHandler(Exception.class)` — detail **not leaked** (generic "Unexpected server error") |

> **Behavioral note:** Single-resource lookups using `findById(...).orElseThrow(NoSuchElementException)` return **404 `not_found`** when the row is missing — currently `GET /data/v1/doctors/{id}` and `GET /data/v1/hospital-info`. Collection / sub-list endpoints return **200 with an empty result** for no-match (e.g. `GET /services/{id}/prices` → `[]`; filtered lists → empty `PageResponse`) rather than 404. See per-endpoint notes.

### Pagination Convention — `PageResponse<T>`

Used by paginated list endpoints (`/departments`, `/doctors`, `/services`). Non-paginated lists (`/bhyt-policies`, `/procedures`, `/channels`, `/appointment-slots`, `/doctors/{id}/schedules`, `/services/{id}/prices`) return bare JSON arrays.

```json
{
  "total": 137,
  "page": 0,
  "size": 20,
  "totalPages": 7,
  "items": [ /* DTO[] */ ]
}
```

| Field | Type | Notes |
|---|---|---|
| `total` | long | Total matching rows across all pages |
| `page` | int | Zero-indexed page number |
| `size` | int | Page size (may exceed `items.length` on last page) |
| `totalPages` | int | `ceil(total/size)` |
| `items` | T[] | DTOs for current page |

**Common query params:** `page` (int, default `0`, zero-indexed) and `size` (int, endpoint-specific default — see each endpoint).

**Date format:** all dates (`from`, `to`, `date`, `effectiveDate`) use ISO-8601 `yyyy-MM-dd` (enforced via `@DateTimeFormat(iso = DateTimeFormat.ISO.DATE)`).

---

## 1. Hospital Info

### `GET /data/v1/hospital-info`

Returns the single configured hospital info row. Controller: `HospitalInfoController`.

**Auth:** See §0 (optional `X-API-Key`). **Query params:** none. **Path params:** none.

**200 Response** — `HospitalInfoDto` when a row is seeded. **404 `not_found`** if no row configured.

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `name` | String | Vietnamese full name |
| `shortName` | String | |
| `nameEn` | String | English name |
| `slogan` | String | |
| `addresses` | object\|null | Free-form JSON (parsed from DB string) |
| `hotline` | String | |
| `workingHours` | object\|null | Free-form JSON |
| `grade` | String | Hospital grade |
| `establishedYear` | Integer | |
| `website` | String | |

**Example 200:**
```json
{
  "id": 1,
  "name": "Bệnh viện Hữu nghị Hà Nội",
  "shortName": "BV Hữu nghị Hà Nội",
  "nameEn": "Hanoi Friendship Hospital",
  "slogan": "Because your health matters",
  "addresses": {
    "main": "Số 1 Trần Nguyên Đán, Khu đô thị mới Đại Kim, Hoàng Mai, Hà Nội",
    "campus_2": "Số 2 Phương Mai, Đống Đa, Hà Nội"
  },
  "hotline": "19006465",
  "workingHours": {
    "weekday": "07:00–16:30",
    "weekend": "07:00–11:30"
  },
  "grade": "Hạng 1",
  "establishedYear": 1960,
  "website": "https://benhvienhuunghihaNoi.vn"
}
```

**Errors:** §0 envelope. **404 `not_found`** when no hospital-info row seeded (`{"error":{"code":"not_found","message":"Hospital info not configured"}}`).

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/hospital-info" -H "X-API-Key: demo-key-123" | jq
```

---

## 2. Departments

### `GET /data/v1/departments`

List hospital departments, optionally filtered by active flag. Paginated (in-memory slice after sort). Controller: `DepartmentController`.

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `active` | Boolean | no | (all) | `true` | `true`=only active, `false`=only inactive, omitted=all |
| `page` | int | no | `0` | `0` | Zero-indexed |
| `size` | int | no | `50` | `20` | Page size |

**Path params:** none. **Auth:** §0.

**200 Response** — `PageResponse<DepartmentDto>`:

`DepartmentDto` fields:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `code` | String | Department code, e.g. `KHKBTN` |
| `name` | String | Vietnamese name |
| `nameEn` | String\|null | English name |
| `description` | String\|null | |
| `campus` | String\|null | e.g. `Cơ sở 1` |
| `floor` | String\|null | e.g. `Tầng 2, Khu B` |
| `workingHours` | String\|null | Free text |
| `phone` | String\|null | |
| `sortOrder` | Integer\|null | Sort priority (asc, nulls last) |
| `isActive` | Boolean\|null | |

**Example 200:**
```json
{
  "total": 2,
  "page": 0,
  "size": 50,
  "totalPages": 1,
  "items": [
    {
      "id": 1,
      "code": "KHKBTN",
      "name": "Khoa Khám bệnh Tự nguyện",
      "nameEn": "Voluntary Examination Department",
      "description": "Khám và tư vấn sức khỏe",
      "campus": "Cơ sở 1",
      "floor": "Tầng 2, Khu B",
      "workingHours": "07:00–16:30 (T2–T7)",
      "phone": "024.3855.0123",
      "sortOrder": 1,
      "isActive": true
    },
    {
      "id": 7,
      "code": "KH_CANLAM_SANG",
      "name": "Khoa Cận lâm sàng",
      "nameEn": "Paraclinical Department",
      "description": "Xét nghiệm và chẩn đoán hình ảnh",
      "campus": "Cơ sở 1",
      "floor": "Tầng 1, Khu A",
      "workingHours": "06:30–16:00 (T2–T7)",
      "phone": "024.3855.0456",
      "sortOrder": 2,
      "isActive": true
    }
  ]
}
```

**Errors:** `400 bad_request` — `page`/`size` non-numeric, or `active` not a valid boolean.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/departments?active=true&page=0&size=20" -H "X-API-Key: demo-key-123" | jq
```

---

## 3. Doctors

### `GET /data/v1/doctors`

List active doctors, optionally filtered by department. Paginated. Controller: `DoctorController`.

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `department` | Long | no | (all) | `1` | Department id; only active doctors in that department |
| `page` | int | no | `0` | `0` | Zero-indexed |
| `size` | int | no | `20` | `20` | Page size |

**Path params:** none. **Auth:** §0.

> **Behavior:** Always filters `isActive = true` (see `DoctorRepository.findByIsActiveTrue` / `findByDepartmentIdAndIsActiveTrue`). No way to list inactive doctors via this endpoint.

**200 Response** — `PageResponse<DoctorDto>`:

`DoctorDto` fields:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `code` | String | Doctor code, e.g. `BS.00012` |
| `fullName` | String | e.g. `Nguyễn Văn A` (without title prefix) |
| `degree` | String\|null | e.g. `Tiến sĩ`, `Thạc sĩ` |
| `title` | String\|null | e.g. `Phó Giáo sư`, `Bác sĩ` |
| `departmentId` | Long\|null | |
| `departmentCode` | String\|null | |
| `departmentName` | String\|null | |
| `bio` | String\|null | Biography markdown |
| `avatarUrl` | String\|null | |

**Example 200:**
```json
{
  "total": 1,
  "page": 0,
  "size": 20,
  "totalPages": 1,
  "items": [
    {
      "id": 12,
      "code": "BS.00012",
      "fullName": "Nguyễn Văn A",
      "degree": "Tiến sĩ Y học",
      "title": "Phó Giáo sư, Bác sĩ CKII",
      "departmentId": 1,
      "departmentCode": "KHKBTN",
      "departmentName": "Khoa Khám bệnh Tự nguyện",
      "bio": "Hơn 25 năm kinh nghiệm nội tim mạch.",
      "avatarUrl": "https://cdn.benhvienhuunghihanoi.vn/doctors/12.jpg"
    }
  ]
}
```

**Errors:** `400 bad_request` — non-numeric `department`, `page`, or `size`.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/doctors?department=1&page=0&size=20" -H "X-API-Key: demo-key-123" | jq
```

---

### `GET /data/v1/doctors/{id}`

Get a single doctor by id.

**Path params:** `id` (Long, required) — doctor id. **Query params:** none. **Auth:** §0.

**200 Response** — `DoctorDto` (schema §3.1) when found.

> **Behavioral note:** `DoctorService.get(id)` calls `findById(...).orElseThrow(NoSuchElementException)` → mapped to **404 `not_found`** by `GlobalExceptionHandler` for an unknown id.

**Example 200** (found): see DoctorDto example above.

**Errors:**
- `400 bad_request` — `id` non-numeric (type mismatch): `{"error":{"code":"bad_request","message":"Invalid parameter: id"}}`.
- `404 not_found` — unknown id: `{"error":{"code":"not_found","message":"Doctor not found: id=…"}}`.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/doctors/12" -H "X-API-Key: demo-key-123" | jq
```

---

### `GET /data/v1/doctors/{id}/schedules`

List schedules (working shifts) for a doctor, optionally within a date range.

**Path params:** `id` (Long, required) — doctor id. **Auth:** §0.

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `from` | LocalDate (`yyyy-MM-dd`) | no | (none) | `2026-07-01` | Range start (inclusive) |
| `to` | LocalDate (`yyyy-MM-dd`) | no | (none) | `2026-07-31` | Range end (inclusive) |

> **Behavioral note:** The `from`/`to` filter is applied **only when BOTH are non-null**. If either is omitted, **all** schedules for the doctor are returned (no date filtering). Results sorted by `effectiveDate ASC, startTime ASC`.

**200 Response** — array of `DoctorScheduleDto`:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `doctorId` | Long | |
| `departmentId` | Long\|null | |
| `dayOfWeek` | Integer\|null | `1`=Monday … `7`=Sunday (java.time.DayOfWeek convention) |
| `effectiveDate` | LocalDate\|null | `yyyy-MM-dd` |
| `startTime` | LocalTime | `HH:mm:ss` |
| `endTime` | LocalTime | `HH:mm:ss` |
| `shift` | String\|null | e.g. `Sáng`, `Chiều` |
| `room` | String\|null | e.g. `Phòng 201, Khu B` |
| `note` | String\|null | |

**Example 200:**
```json
[
  {
    "id": 101,
    "doctorId": 12,
    "departmentId": 1,
    "dayOfWeek": 2,
    "effectiveDate": "2026-07-21",
    "startTime": "07:30:00",
    "endTime": "11:30:00",
    "shift": "Sáng",
    "room": "Phòng 201, Khu B",
    "note": "Khám nội tim mạch"
  },
  {
    "id": 102,
    "doctorId": 12,
    "departmentId": 1,
    "dayOfWeek": 4,
    "effectiveDate": "2026-07-23",
    "startTime": "13:30:00",
    "endTime": "16:30:00",
    "shift": "Chiều",
    "room": "Phòng 201, Khu B",
    "note": null
  }
]
```

**Errors:** `400 bad_request` — `id` non-numeric, or `from`/`to` not `yyyy-MM-dd`.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/doctors/12/schedules?from=2026-07-01&to=2026-07-31" -H "X-API-Key: demo-key-123" | jq
```

---

## 4. Hospital Services & Prices

### `GET /data/v1/services`

List hospital services, optionally filtered by category and/or department. Paginated. Controller: `HospitalServiceController`.

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `category` | String | no | (all) | `Khám bệnh` | Blank treated as null (no filter) |
| `department` | Long | no | (all) | `1` | Department id |
| `page` | int | no | `0` | `0` | |
| `size` | int | no | `50` | `20` | |

**Path params:** none. **Auth:** §0.

**200 Response** — `PageResponse<HospitalServiceDto>`:

`HospitalServiceDto` fields:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `code` | String | Service code |
| `name` | String | Vietnamese name |
| `category` | String\|null | e.g. `Khám bệnh`, `Xét nghiệm` |
| `departmentId` | Long\|null | |
| `description` | String\|null | |

**Example 200:**
```json
{
  "total": 1,
  "page": 0,
  "size": 20,
  "totalPages": 1,
  "items": [
    {
      "id": 55,
      "code": "KHAMB_TN",
      "name": "Khám bệnh theo yêu cầu — Chuyên khoa Nội",
      "category": "Khám bệnh",
      "departmentId": 1,
      "description": "Khám và tư vấn chuyên khoa Nội tổng quát."
    }
  ]
}
```

**Errors:** `400 bad_request` — non-numeric `department`/`page`/`size`.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/services?category=Khám bệnh&department=1&page=0&size=20" -H "X-API-Key: demo-key-123" | jq
```

---

### `GET /data/v1/services/{id}/prices`

List price rows attached to a service. Sorted by `audience ASC, campus ASC`. **Not** paginated (bare array).

**Path params:** `id` (Long, required) — service id. **Query params:** none. **Auth:** §0.

> **Behavioral note:** No existence check on the service id. Unknown `id` → **`200 []`** (empty array), not 404.

**200 Response** — array of `ServicePriceDto`:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `priceVnd` | BigInteger | Integer VND amount (no decimals). Serialized as JSON number. |
| `audience` | String\|null | e.g. `BHYT`, `no_bhyt`, `foreigner` |
| `campus` | String\|null | e.g. `Cơ sở 1` |
| `effectiveDate` | LocalDate\|null | `yyyy-MM-dd` |
| `sourceUrl` | String\|null | Citation source |
| `note` | String\|null | |

**Example 200:**
```json
[
  {
    "id": 901,
    "priceVnd": 42100,
    "audience": "BHYT",
    "campus": "Cơ sở 1",
    "effectiveDate": "2026-07-01",
    "sourceUrl": "https://bcdvhnn.gov.vn/bienlai/901",
    "note": "Giá BHYT theo quyết định 1234/QĐ-BYT"
  },
  {
    "id": 902,
    "priceVnd": 150000,
    "audience": "no_bhyt",
    "campus": "Cơ sở 1",
    "effectiveDate": "2026-07-01",
    "sourceUrl": "https://bcdvhnn.gov.vn/bienlai/902",
    "note": null
  }
]
```

**Errors:** `400 bad_request` — `id` non-numeric. No 404 path (returns `[]`).

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/services/55/prices" -H "X-API-Key: demo-key-123" | jq
```

---

## 5. BHYT Policies

### `GET /data/v1/bhyt-policies`

List BHYT (health insurance) policies. Sorted by `category ASC, code ASC` (or `code ASC` when category filter is set). Bare array (not paginated).

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `category` | String | no | (all) | `Điều trị` | Blank treated as null |

**Path params:** none. **Auth:** §0.

**200 Response** — array of `BhytPolicyDto`:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `code` | String | Policy code |
| `title` | String | |
| `category` | String\|null | |
| `summary` | String\|null | Short summary (AI-citable) |
| `detailsMd` | String\|null | Full details in Markdown |
| `sourceUrl` | String\|null | Citation |
| `effectiveDate` | LocalDate\|null | `yyyy-MM-dd` |

**Example 200:**
```json
[
  {
    "id": 33,
    "code": "QD-BHYT-2026-001",
    "title": "Mức hưởng BHYT 80% đối với người nghèo",
    "category": "Điều trị",
    "summary": "Người nghèo, cận nghèo được BHYT chi trả 80% chi phí khám chữa bệnh trong tuyến hợp đồng.",
    "detailsMd": "## Điều kiện áp dụng\n- Có thẻ BHYT còn hiệu lực\n...",
    "sourceUrl": "https://bhxh.gov.vn/qd-2026-001",
    "effectiveDate": "2026-01-01"
  }
]
```

**Errors:** §0 envelope. No 400 path for the optional `category` string.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/bhyt-policies?category=Điều trị" -H "X-API-Key: demo-key-123" | jq
```

---

## 6. Procedures

### `GET /data/v1/procedures`

List procedure steps. Sorted by `code ASC, stepNo ASC` (or `stepNo ASC` when `code` filter is set). Bare array.

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `code` | String | no | (all) | `QT.25.01` | Procedure code; filter returns all steps of that procedure |

**Path params:** none. **Auth:** §0.

**200 Response** — array of `ProcedureDto`:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `code` | String | Procedure code, e.g. `QT.25.01` |
| `title` | String\|null | Procedure title |
| `stepNo` | Integer\|null | Step number within the procedure |
| `name` | String\|null | Step name |
| `description` | String\|null | Step description |
| `responsibleRole` | String\|null | e.g. `Lễ tân`, `Điều dưỡng` |
| `relatedForm` | String\|null | Reference to a form/template |
| `sourceDoc` | String\|null | Source document id/url |

**Example 200:**
```json
[
  {
    "id": 201,
    "code": "QT.25.01",
    "title": "Quy trình tiếp nhận bệnh nhân nội trú",
    "stepNo": 1,
    "name": "Tiếp nhận hồ sơ",
    "description": "Bệnh nhân nộp CCCD và thẻ BHYT tại quế tiếp nhận.",
    "responsibleRole": "Lễ tân",
    "relatedForm": "BM.01-TiepNhan",
    "sourceDoc": "QĐ 25/2026/QĐ-BV"
  },
  {
    "id": 202,
    "code": "QT.25.01",
    "title": "Quy trình tiếp nhận bệnh nhân nội trú",
    "stepNo": 2,
    "name": "Đo sinh hiệu",
    "description": "Điều dưỡng đo HA, nhiệt độ, nhịp mạch.",
    "responsibleRole": "Điều dưỡng",
    "relatedForm": "BM.02-SinhHieu",
    "sourceDoc": "QĐ 25/2026/QĐ-BV"
  }
]
```

**Errors:** §0 envelope. No 400 path for optional `code` string.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/procedures?code=QT.25.01" -H "X-API-Key: demo-key-123" | jq
```

---

## 7. Support Channels

### `GET /data/v1/channels`

List active support channels (hotline, Zalo, Facebook, etc.). Sorted by `sortOrder ASC, id ASC`. Bare array. Controller: `SupportChannelController`.

**Query params:** none. **Path params:** none. **Auth:** §0.

> **Behavior:** Only returns rows with `isActive = true` (hard-coded filter in `SupportChannelService.list`).

**200 Response** — array of `SupportChannelDto`:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `channelType` | String | e.g. `hotline`, `zalo`, `facebook`, `website` |
| `label` | String | Display label |
| `url` | String\|null | |
| `phone` | String\|null | |
| `campus` | String\|null | |
| `sortOrder` | Integer\|null | Display order |

**Example 200:**
```json
[
  {
    "id": 1,
    "channelType": "hotline",
    "label": "Tổng đài hỗ trợ 24/7",
    "url": null,
    "phone": "19006465",
    "campus": null,
    "sortOrder": 1
  },
  {
    "id": 2,
    "channelType": "zalo",
    "label": "Zalo OA Bệnh viện",
    "url": "https://zalo.me/benhvienhuunghihanoi",
    "phone": null,
    "campus": null,
    "sortOrder": 2
  }
]
```

**Errors:** §0 envelope. No params → no validation errors possible.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/channels" -H "X-API-Key: demo-key-123" | jq
```

---

## 8. Appointment Slots

### `GET /data/v1/appointment-slots`

List available appointment slots (mock — production would proxy HIS). Sorted by `startTime ASC`. Bare array. Controller: `AppointmentSlotController`.

**Query params:**

| Param | Type | Required | Default | Example | Notes |
|---|---|---|---|---|---|
| `doctor` | Long | no | (none) | `12` | Doctor id |
| `date` | LocalDate (`yyyy-MM-dd`) | no | (none) | `2026-07-21` | Specific date |

**Path params:** none. **Auth:** §0.

> **Behavioral note (important):** The service only returns rows when **`date` is non-null**.
> - `date` set, `doctor` set → slots for that doctor on that date.
> - `date` set, `doctor` null → all slots on that date.
> - `date` null (regardless of `doctor`) → **`200 []`** (empty array). Always include `date`.

**200 Response** — array of `AppointmentSlotDto`:

| Field | Type | Notes |
|---|---|---|
| `id` | Long | |
| `doctorId` | Long | |
| `departmentId` | Long\|null | |
| `date` | LocalDate | `yyyy-MM-dd` |
| `startTime` | LocalTime | `HH:mm:ss` |
| `endTime` | LocalTime | `HH:mm:ss` |
| `capacity` | Integer | Defaults to 0 if null in DB |
| `bookedCount` | Integer | Defaults to 0 if null in DB |
| `available` | Integer | `max(0, capacity - bookedCount)` |
| `isAvailable` | Boolean\|null | |

**Example 200:**
```json
[
  {
    "id": 5001,
    "doctorId": 12,
    "departmentId": 1,
    "date": "2026-07-21",
    "startTime": "07:30:00",
    "endTime": "08:00:00",
    "capacity": 5,
    "bookedCount": 2,
    "available": 3,
    "isAvailable": true
  },
  {
    "id": 5002,
    "doctorId": 12,
    "departmentId": 1,
    "date": "2026-07-21",
    "startTime": "08:00:00",
    "endTime": "08:30:00",
    "capacity": 5,
    "bookedCount": 5,
    "available": 0,
    "isAvailable": false
  }
]
```

**Errors:** `400 bad_request` — `doctor` non-numeric or `date` not `yyyy-MM-dd`.

**curl:**
```bash
curl -s "http://localhost:8081/data/v1/appointment-slots?doctor=12&date=2026-07-21" -H "X-API-Key: demo-key-123" | jq
```

---

## 9. Postman Quick-Start

**Environment variables:** `base_url` = `http://localhost:8081`; `api_key` = `demo-key-123` (leave blank if server `DATA_API_KEY` env is unset).

**Collection-level headers:**

| Key | Value |
|---|---|
| `X-API-Key` | `{{api_key}}` |
| `Accept` | `application/json` |
| `Accept-Language` | `vi` (optional; per docs/07 §B intent) |

### Collection Skeleton (import as raw JSON)

```json
{
  "info": { "name": "BV Hữu nghị Hà Nội — Data API", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json" },
  "variable": [
    { "key": "base_url", "value": "http://localhost:8081" },
    { "key": "api_key", "value": "" }
  ],
  "item": [
    { "name": "Hospital Info",     "request": { "method": "GET", "url": "{{base_url}}/data/v1/hospital-info" } },
    { "name": "Departments",       "request": { "method": "GET", "url": "{{base_url}}/data/v1/departments?active=true" } },
    { "name": "Doctors (list)",    "request": { "method": "GET", "url": "{{base_url}}/data/v1/doctors?department=1&page=0&size=20" } },
    { "name": "Doctor by id",      "request": { "method": "GET", "url": "{{base_url}}/data/v1/doctors/12" } },
    { "name": "Doctor schedules",  "request": { "method": "GET", "url": "{{base_url}}/data/v1/doctors/12/schedules?from=2026-07-01&to=2026-07-31" } },
    { "name": "Services",          "request": { "method": "GET", "url": "{{base_url}}/data/v1/services?category=Khám bệnh" } },
    { "name": "Service prices",    "request": { "method": "GET", "url": "{{base_url}}/data/v1/services/55/prices" } },
    { "name": "BHYT policies",     "request": { "method": "GET", "url": "{{base_url}}/data/v1/bhyt-policies" } },
    { "name": "Procedures",        "request": { "method": "GET", "url": "{{base_url}}/data/v1/procedures?code=QT.25.01" } },
    { "name": "Channels",          "request": { "method": "GET", "url": "{{base_url}}/data/v1/channels" } },
    { "name": "Appointment slots", "request": { "method": "GET", "url": "{{base_url}}/data/v1/appointment-slots?doctor=12&date=2026-07-21" } }
  ]
}
```

---

## 10. Contract-vs-Code Mismatches (vs `docs/07-api-design.md` §B)

Items below are observations, not bugs. Code is source of truth.

| # | Area | docs/07 says | Code does | Impact |
|---|---|---|---|---|
| 1 | Hospital info shape | `{ name, address[], hotline, workingHours, grade }` | DTO adds `id, shortName, nameEn, slogan, establishedYear, website`; field is `addresses` (plural, free-form JSON object), not `address[]` | Frontend must read `addresses` (object, not array) |
| 2 | Appointment slots | `{ start, end, capacity, booked, available }` | DTO fields are `startTime, endTime, capacity, bookedCount, available` (+ `id, doctorId, departmentId, date, isAvailable`) | Field-name rename; FE must use `startTime/endTime/bookedCount` |
| 3 | Not-found behavior | (Implied 404 envelope) | `GET /doctors/{id}` & `GET /hospital-info` → **404** (`NoSuchElementException`); `GET /services/{id}/prices` → **200 []** for unknown id | Doctors/hospital-info now 404 correctly; only `services/{id}/prices` still returns `[]` — consider 404 for consistency |
| 4 | Schedule filtering | `?from&to` | Filter applies only when **both** `from` AND `to` are present | Single-bound ranges not supported — must always pass both |
| 5 | Appointment slots filter | `?doctor&date` | Returns `[]` unless `date` is present (doctor alone returns empty) | Must always pass `date` |
| 6 | Doctors list | (Implies all doctors) | Always `isActive=true`; no flag to include inactive | Cannot fetch inactive doctors via this endpoint |
| 7 | Channels list | `{ channelType, label, url, phone }` | Adds `id, campus, sortOrder`; only returns `isActive=true` | Extra fields additive; non-active hidden |
| 8 | Extra fields in DTOs | (Various) | DTOs add `description`, `note`, `sourceDoc`, `effectiveDate`, etc. — all additive | FE-facing, non-breaking |
| 9 | Endpoints not implemented | docs/07 §B.3 also lists `/kb/articles`, `/faqs`, `/emergency-protocols` | **No controllers exist** for these 3 endpoints | KB / FAQ / emergency-protocol retrieval not yet wired in data-api (likely owned by AI/FastAPI side instead) |
| 10 | Auth | `X-API-Key` (demo) | Enforced only when `DATA_API_KEY` env non-blank; default = open | Dev = no auth; prod = required |
| 11 | Admin CRUD | docs/07 §B note: "Admin CRUD … guard `X-API-Key`, MVP có thể skip" | No POST/PUT/DELETE controllers | Matches MVP scope (seed via Flyway) |
| 12 | CORS exposed header | (Not specified) | `X-Total-Count` exposed but **not set** by any controller (pagination metadata is in body via `PageResponse`) | Header is a no-op today |

---

## 11. Unresolved Questions

1. ~~Should `GET /doctors/{id}` & `GET /hospital-info` return 404?~~ **Resolved** — they now 404 (`NoSuchElementException`). **Open:** should `GET /services/{id}/prices` also 404 (instead of `200 []`) for an unknown service id? Recommend aligning before FE integration.
2. Should `/appointment-slots` support `doctor`-only filter (no date)? Currently returns `[]`.
3. Should `/doctors/{id}/schedules` support partial date ranges (`from` only / `to` only)? Currently requires both.
4. Are `/kb/articles`, `/faqs`, `/emergency-protocols` (docs/07 §B.3) intended for this service, or owned by the FastAPI AI gateway?
5. Is `Accept-Language` actually consumed? docs/07 §B implies i18n (R10), but no controller reads the header — `nameEn` fields exist but selection logic is absent.
