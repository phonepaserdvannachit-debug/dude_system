# Dude Payment Sharing System — FastAPI Backend Phase 1

This backend is built for the production version of the Dude Payment Sharing System.

Current phase includes:

- FastAPI project structure
- SQLAlchemy 2.0 database setup
- Pydantic V2 settings and schemas
- JWT authentication
- BCrypt PIN/password verification
- `person`-only login
- Admin dependency foundation
- Health check endpoint
- Clean architecture foundation

Frontend UI is not changed in this phase.

## 1. Create Python environment

```bash
cd dude_backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Create `.env`

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Edit `.env` and confirm your local MariaDB database URL:

```env
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/dude_payment_system
```

## 3. Import database

Use phpMyAdmin or MySQL CLI to create/import the schema:

```bash
mysql -u root dude_payment_system < sql/dude_payment_system_v2.sql
```

If the database does not exist yet:

```sql
CREATE DATABASE dude_payment_system CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

## 4. Run the backend

```bash
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

## 5. Test endpoints

Health check:

```text
GET /api/v1/health
```

Login:

```text
POST /api/v1/auth/login
```

Body:

```json
{
  "username": "john",
  "password": "2580"
}
```

The backend never stores the 4-digit PIN as plain text. It verifies the submitted PIN against the BCrypt hash stored in `person.password_hash`.

Current seed users from the v2 SQL:

```text
john  / 2580
tar   / 1234
koung / 1234
sun   / 1234
top   / 1234
dan   / 3421
ko    / 1234
vick  / 1234
```

## 6. What comes next

Phase 2:

- Person API
- Category API
- Goods API

Phase 3:

- Bill creation transaction service
- Bill detail creation
- Share calculation
- Auto bookkeeper
- Payment status logic

Phase 4:

- Slip upload to Supabase Storage
- Contract messages
- Dashboard endpoint
- Settings endpoint

