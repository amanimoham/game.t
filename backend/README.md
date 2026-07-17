# محاربة المغريات — Backend

لعبة تعليمية للأطفال لرفع الوعي الادخاري. Backend إنتاجي مبني بـ FastAPI.

## التقنيات
- **FastAPI** (async) · **PostgreSQL** + **SQLAlchemy 2.0 (async)** + **Alembic**
- **Redis** (كاش/rate-limit/توكن) · **Celery** (مهام خلفية)
- **Docker** / **docker-compose** · جاهز للنشر على **Render**

## البنية
```
backend/
├── app/
│   ├── api/          # طبقة الـ REST (v1)
│   ├── core/         # الإعداد + اللوجينج
│   ├── database/     # المحرّك + الجلسات + Base
│   ├── models/       # جداول SQLAlchemy (12 جدول)
│   ├── schemas/      # Pydantic (تُملأ لاحقاً)
│   ├── services/     # منطق الأعمال
│   ├── game_engine/  # نظام محاربة المغريات + Decision Engine
│   ├── ai/           # واجهات الاستراتيجية (rule-based ثم ML)
│   ├── security/     # التشفير/التوكن/الحماية
│   └── worker/       # Celery
├── alembic/          # الهجرات
├── tests/
├── Dockerfile · docker-compose.yml · requirements.txt
```

## التشغيل محلياً (Docker)
```bash
cp .env.example .env          # عدّل القيم عند الحاجة
docker compose up --build     # يشغّل db + redis + api + worker
# الهجرات تُطبّق تلقائياً عند إقلاع الـ api (scripts/start.sh)
```
- التوثيق التفاعلي: http://localhost:8000/docs
- فحص الحياة: `GET /api/v1/health` · فحص القاعدة: `GET /api/v1/health/db`

## التشغيل بدون Docker (تطوير)
```bash
python -m venv .venv && source .venv/Scripts/activate   # ويندوز
pip install -r requirements.txt
# شغّل Postgres/Redis محلياً وحدّث .env
alembic upgrade head
uvicorn app.main:app --reload
```

## الهجرات (Alembic)
```bash
alembic upgrade head                       # تطبيق
alembic upgrade head --sql                 # معاينة الـ SQL بدون تنفيذ
alembic revision --autogenerate -m "msg"   # هجرة جديدة (راجعها دائماً)
```

## الاختبارات
```bash
pytest
```

## ملاحظات أمان (المستخدمون أطفال)
- لا PII للطفل؛ الطفل ملف تابع للأب يُصادَق بـ PIN مُجزّأ.
- المكافآت بنظام escrow؛ حالات مقفلة → مكتملة → مُسلّمة مع idempotency.
- الجداول الحسّاسة append-only (`child_decisions`, `behavior_events`, `audit_logs`).
