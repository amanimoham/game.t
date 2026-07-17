# 🛡️ محاربة المغريات (Muharabat Al-Mughriyat)

لعبة تعليمية للأطفال ترفع الوعي الادخاري: الأب يشتري ويقفل مكافأة رقمية (مثل Robux)،
والطفل يفتحها تدريجياً عبر هزيمة "وحوش المغريات" واتخاذ قرارات مالية سليمة (تأجيل المكافأة،
مقاومة الشراء الاندفاعي، الحاجة مقابل الرغبة).

## البنية
```
game/
├── backend/     # FastAPI + PostgreSQL + SQLAlchemy 2.0 + Redis + Celery
├── frontend/    # React + Vite (RTL عربي)
└── docs/        # بحث الـ datasets واستراتيجية البيانات
```

## التشغيل السريع (بدون Docker — للعرض/التطوير)
```bash
# 1) الخلفية: Postgres مدمج + fakeredis على :8000
cd backend
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
python -m scripts.dev_run

# 2) الواجهة على :5173 (نافذة أخرى)
cd frontend
npm install
npm run dev
```
افتح http://localhost:5173

## التشغيل بـ Docker (production-like)
```bash
cd backend
cp .env.example .env
docker compose up --build      # postgres + redis + api + worker
python -m scripts.seed         # (مرة واحدة) تعبئة محتوى اللعبة
```

## المكوّنات الرئيسية
- **Auth:** JWT + refresh مع تدوير/إبطال في Redis، دخول الأب، دخول الطفل بـ PIN (COPPA).
- **Game Engine:** محرّك قرار نقي يحسب الصبر/الوعي/ضبط الاندفاع ويهزم الوحوش.
- **AI (rule-based, ML-ready):** اختيار الوحش، تعديل الصعوبة، رسالة التشجيع، توقّع الإكمال.
- **Reward Escrow:** فتح تدريجي للمكافأة مع سجل `reward_unlock_events` غير قابل للتغيير.
- **Dashboard:** رؤى الأب عن نمو مهارات الطفل.

## الاختبارات
```bash
cd backend && pytest        # 26 اختبار (يشمل e2e كامل على Postgres مدمج)
cd frontend && npm run build
```

## التوثيق
- [بحث الـ Datasets واستراتيجية البيانات](docs/research/datasets.md)
- [Backend README](backend/README.md) · [Frontend README](frontend/README.md)
