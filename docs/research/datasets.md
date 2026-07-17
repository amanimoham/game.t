# بحث الـ Datasets — لعبة الادخار للأطفال

> تاريخ البحث: 2026-07-17 · كل رابط تم التحقق من أنه يفتح فعلياً. الترخيص مذكور لكل مصدر لأن المنتج **تجاري**.
> رمز الترخيص: 🟢 = آمن تجارياً · 🟡 = غير محدد/تحقق قبل الشحن · 🔴 = غير تجاري (للبحث فقط، ممنوع تشحنه)

---

## المنهجية والتنبيهات الأساسية

- الأولوية للبيانات المفتوحة من Kaggle, UCI, Google Dataset Search, GitHub, OSF, والأوراق البحثية.
- **لا يوجد dataset مفتوح عن سلوك الادخار/تأجيل المكافأة لدى الأطفال الصغار (5–12)** — كل المصادر إما عمر 15 (PISA) أو بالغين. هذه فجوتك الأساسية وفرصتك لبناء أصل بيانات خاص.
- معظم بيانات "الإغراء / تأجيل المكافأة" هي بيانات بالغين — تُستخدم كـ *proxy* لمعايرة التصميم والصعوبة، لا كتمثيل مباشر لسلوك الأطفال.
- فخاخ ترخيص مهمة: ITC، EdNet، Junyi، Retail Rocket، Instacart كلها غير تجارية (🔴) — للبحث الداخلي فقط.

---

## 1) Financial Literacy for Children

| Dataset | المصدر | العينات | أبرز Features | مجاني؟ | تجاري؟ | ملاءمة /10 |
|---|---|---|---|---|---|---|
| [PISA 2022 Financial Literacy](https://webfs.oecd.org/pisa2022/index.html) | OECD | ~97,000 طالب (15 سنة، 20 دولة) | درجة الوعي المالي، فهم الادخار/الإنفاق، حيازة حساب بنكي، مصروف، SES، الدولة | 🟢 مجاني | 🟡 البيانات CC BY 4.0، لكن **أسئلة الاختبار NC** — لا تنسخ نصوص الأسئلة | **9** |
| [CFPB Financial Well-Being Survey (PUF 2016)](https://www.consumerfinance.gov/data-research/financial-well-being-survey-data/) | CFPB (حكومة أمريكية) | 6,394 بالغ · 217 متغير | مقياس الرفاه المالي 10 بنود، **بنود ضبط النفس/التوجه المستقبلي**، سلوك الادخار، المواقف | 🟢 مجاني | 🟢 Public Domain (الأنظف) | **7** |
| [FINRA NFCS](https://www.finrafoundation.org/nfcs-data-and-downloads) | FINRA Foundation | ~25,000+ بالغ/موجة | اختبار الوعي المالي 5 أسئلة، سلوك الادخار، صندوق الطوارئ، الميزانية، القلق المالي | 🟢 مجاني | 🟡 لا ترخيص صريح — تحقق قبل الشحن | **6** |
| [World Bank Global Findex](https://www.worldbank.org/en/publication/globalfindex/download-data) | World Bank | ~150,000+ بالغ/موجة · 140+ دولة | ملكية حساب، **سلوك الادخار** (طوارئ/تقاعد)، الدفع الرقمي، المرونة المالية، مقسّمة بالعمر (15–24) | 🟢 مجاني | 🟡 غالباً CC BY 4.0 — تحقق لكل ملف | **5** |
| [Kaggle: Student Spending](https://www.kaggle.com/datasets/sumanthnimmagadda/student-spending-dataset) | مساهم Kaggle | ~1,000 صف | العمر، الدخل الشهري، الإنفاق حسب الفئة، طريقة الدفع، **الادخار الشهري** (قد تكون بيانات تخليقية) | 🟢 مجاني | 🟡 تحقق من حقل الترخيص بالصفحة | **5** |

**كيفية الاستخدام داخل المنتج:**
- **PISA** → معايرة مستويات الصعوبة على "نطاقات الكفاءة" الحقيقية، وبناء بروفايلات "أطفال" افتراضية، والتحقق أن ألعاب "الحاجة مقابل الرغبة" تقيس نفس البُنى الحقيقية. (اكتب أسئلتك بنفسك — لا تنسخ نصوص PISA).
- **CFPB** → أثمن مصدر: يحتوي بنود **ضبط النفس وتأجيل المكافأة** الحقيقية التي هي جوهر لعبتك؛ استخدمها كأساس لمقياس "الإرادة/التقدّم" داخل اللعبة.
- **FINRA** → نمذجة شخصية **الأب/الوالد** (الطرف الدافع في حلقتك) وفحص المعرفة المالية عند الأونبوردنغ.
- **Findex** → تحجيم السوق حسب الدولة، وتحديد خطوط أساس واقعية "كم يدّخر الشباب".
- **Student Spending** → قالب لنموذج بيانات المصروف/الميزانية داخل اللعبة وتوليد بروفايلات إنفاق افتراضية للبروتوتايب.

---

## 2) Behavioral Economics (اتخاذ القرار / تأجيل المكافأة / التحكم بالاندفاع)

| Dataset | المصدر | العينات | أبرز Features | مجاني؟ | تجاري؟ | ملاءمة /10 |
|---|---|---|---|---|---|---|
| [ITC — Intertemporal Choice DB](https://osf.io/3wsae/) | OSF (تجميع 87 دراسة) | 11,852 شخص · 1,172,644 محاولة | مكافأة قريبة-صغيرة، بعيدة-كبيرة، مدة التأخير، الاختيار، زمن الاستجابة، العمر، الدولة | 🟢 مجاني | 🔴 **CC BY-NC-SA — للبحث فقط** | 8 (بحث) / 3 (شحن) |
| [Kirby MCQ-27 (beezdiscounting)](https://github.com/brentkaplan/beezdiscounting) | Brent Kaplan / GitHub | مجموعة مثال + محرّك حساب | subjectid, questionid (1–27), response (0/1)، يحسب معدل الخصم *k* | 🟢 مجاني | 🟡 الكود GPL-2.0 (أعِد كتابة المنطق)؛ المنهج/الأسئلة حرة | **7** |
| [Delay Discounting — Open Task + Normative](https://osf.io/65bg7/) | OSF (ورقة MDPI) | عيّنة معيارية للبالغين | اختيارات الخصم الزمني، بارامترات الخصم المحسوبة، + مهمة قابلة للتعديل + سكربتات R | 🟢 مجاني | 🟡 غالباً CC BY 4.0 — تحقق من مكوّن OSF | **6** |
| [IGT — 617 Healthy Participants](https://osf.io/8t7rm) | Journal of Open Psychology Data / OSF | 617 مشارك | مصفوفات اختيار الأوراق (A–D)، مصفوفات الربح/الخسارة، مؤشر الدراسة | 🟢 مجاني | 🟢 CC BY-SA 4.0 | **5** |
| [UCI Drug Consumption (Quantified)](https://archive.ics.uci.edu/dataset/373/drug+consumption+quantified) | UCI | 1,885 مستجيب | **درجة الاندفاعية BIS-11**، البحث عن الإثارة ImpSS، Big Five، العمر، الجنس | 🟢 مجاني | 🟢 CC BY 4.0 (الأنظف) | **4** |

**كيفية الاستخدام داخل المنتج:**
- **ITC** (بحث فقط) → المصدر الأغنى لنمذجة الإغراءات: اشتق نقاط "خذ الآن مقابل انتظر" قرب نقطة اللامبالاة البشرية الحقيقية حتى تكون قرارات اللعبة صعبة فعلاً؛ استخدم زمن الاستجابة لتمييز "الخطف الاندفاعي السريع" عن "الانتظار المتأنّي".
- **MCQ-27** → بنك جاهز لسيناريوهات الإغراء ("$54 الآن مقابل $55 بعد 117 يوم")؛ أعِد صياغتها للأطفال، وابنِ **محرّك صعوبة قائم على معدل الخصم** يقدّر إرادة الطفل من اختياراته ويصعّد التحدي.
- **IGT / UCI Drug (BIS-11)** → نمذجة **طيف "قابلية الإغراء"** لشخصيات الأعداء/مستويات الصعوبة (استخدم بُنية الاندفاعية فقط، تجاهل محتوى المخدرات تماماً).

---

## 3) Gamification & Learning Analytics

| Dataset | المصدر | العينات | أبرز Features | مجاني؟ | تجاري؟ | ملاءمة /10 |
|---|---|---|---|---|---|---|
| [Predict Student Performance from Game Play (Jo Wilder)](https://www.kaggle.com/competitions/predict-student-performance-from-game-play/data) | Learning Agency Lab / Field Day (Kaggle) | ~26M حدث · ~23,500 جلسة | session_id, event_name, elapsed_time, level, إحداثيات الشاشة/الغرفة, fqid, labels لكل سؤال | 🟢 مجاني | 🟢 CC BY 4.0 | **9** |
| [Open Game Data (Field Day Lab)](https://opengamedata.fielddaylab.wisc.edu/) | UW-Madison Field Day | 21+ لعبة · 2–10M حدث/يوم | schema موحّد: session_id, app_id, event_name, event_data(JSON), timestamp, sequence_index + طبقة feature-extractor | 🟢 مجاني | 🟢 بيانات مفتوحة (تحقق لكل لعبة) | **9** |
| [OULAD](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset) | Open University / UCI | 32,593 طالب · ~10M تفاعل | ديموغرافيا, final_result, sum_click يومي, نوع النشاط, درجات التقييم | 🟢 مجاني | 🟢 CC BY 4.0 | **6** |
| [ASSISTments 2009-2010](https://sites.google.com/site/assistmentsdata/home/2009-2010-assistment-data/skill-builder-data-2009-2010) | WPI | ~525,000 تفاعل · ~4,000 طالب | user_id, skill, correct, attempt_count, hint_count, ms_first_response, mastery | 🟢 مجاني | 🟡 attribution فقط — غامض للشحن | **6** |
| [EdNet (Riiid)](https://github.com/riiid/ednet) | Riiid AI Research | ~95M تفاعل · 784,309 طالب | timestamp, question_id, user_answer, elapsed_time, action_type, أحداث دفع/كوبون (KT4) | 🟢 مجاني | 🔴 CC BY-NC — للبحث فقط | 5 |
| [Junyi Academy](https://www.kaggle.com/datasets/junyiacademy/learning-activity-public-dataset-by-junyi-academy) | Junyi (تايوان) | ~16M محاولة · 72,000+ طالب K-12 | is_correct, total_sec_taken, attempt_cnt, used_hint_cnt, level, **رسم بياني للمتطلبات السابقة** | 🟢 مجاني | 🔴 CC BY-NC-SA — للبحث فقط | 5 |

**كيفية الاستخدام داخل المنتج:**
- **Jo Wilder + Open Game Data** هما الأقرب والأوضح تجارياً: **انسخ منهما schema التيليمتري مباشرة** (أحداث موقّتة مصنّفة مع session/level/coords)، وابنِ عليها نماذج knowledge-tracing وتكييف الصعوبة قبل ما تجمع بياناتك. Open Game Data فيها لعبتا اقتصاد (**Bloom, Lakeland**) — الأقرب موضوعياً للادخار.
- **OULAD** → قالب لنمذجة "clickstream يومي → نتيجة" لبناء نموذج churn/retention ("أي طفل يتوقف عن فتح التطبيق").
- **ASSISTments** → مرجع schema لتيليمتري الإتقان (محاولات، تلميحات، زمن → mastery) لتصميم السقالات (scaffolding).
- **EdNet / Junyi** (بحث فقط) → مرجع معماري لتتبّع المعرفة ورسم شجرة المتطلبات ("عدّ النقود → الميزانية → أهداف الادخار").

---

## 4) Consumer Behavior (الشراء الاندفاعي / الندرة / التأثير الاجتماعي)

| Dataset | المصدر | العينات | أبرز Features | مجاني؟ | تجاري؟ | ملاءمة /10 |
|---|---|---|---|---|---|---|
| [UCI Online Shoppers Purchasing Intention](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset) | UCI | 12,330 جلسة | PageValues, BounceRates, **SpecialDay** (قرب المناسبات), Month, VisitorType, Revenue | 🟢 مجاني | 🟢 CC BY 4.0 | **8** |
| [Mendeley: Mobile App Impulse Buying](https://data.mendeley.com/datasets/njvcdh6mkz/1) | Mendeley (Wijaya & Budiman 2023) | 628 مستجيب | Likert: البيئة الاجتماعية، منظور الوقت، التصفح المتعوي/النفعي، **سلوك الشراء الاندفاعي** | 🟢 مجاني | 🟢 CC BY 4.0 | **7** |
| [UCI Online Retail (I & II)](https://archive.ics.uci.edu/dataset/352/online+retail) | UCI | 541,909 سطر (I) · ~1M (II) | InvoiceNo (إلغاءات بـ"C"), Description, Quantity, UnitPrice, Date, Country | 🟢 مجاني | 🟢 CC BY 4.0 | **6** |
| [Marketing A/B Testing](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) | Kaggle (faviovaz) | ~588,000 مستخدم | test group (ad/psa), converted, total ads seen, most-ads day/hour | 🟢 مجاني | 🟡 لا ترخيص واضح — تحقق | **6** |
| [Retail Rocket Clickstream](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) | Retail Rocket | 2.75M حدث · 1.4M زائر | event (view/addtocart/transaction), itemid, **available** (توفّر المخزون عبر الزمن), category_tree | 🟢 مجاني | 🔴 CC BY-NC — للبحث فقط | 7 (بحث) |
| [CFPB Consumer Complaint DB](https://www.consumerfinance.gov/data-research/consumer-complaints/) | CFPB | ملايين الشكاوى | Product, Issue, narrative, company, state, date | 🟢 مجاني | 🟢 Public Domain | **4** |

**كيفية الاستخدام داخل المنتج:**
- **Online Shoppers (SpecialDay)** → معايرة كيف يرفع قرب المناسبة احتمال الشراء → أحداث إغراء موسمية داخل اللعبة، وتصعيد الصعوبة مع عمق التصفح.
- **Mendeley Impulse Buying** → أوزان "البيئة الاجتماعية مقابل التصفح المتعوي مقابل ضغط الوقت" لموازنة **أي أنواع الإغراءات** أقوى، وتصميم استبيان "قابلية الإغراء" مُكيّف للأطفال.
- **Online Retail** → عيّنات أسماء/أسعار/أحجام سلة واقعية لملء "المتجر" بأشياء مغرية؛ الإلغاءات تنمذج آلية "التراجع/الندم".
- **Retail Rocket** (بحث فقط) → حقل `available` يشفّر الندرة زمنياً لتصميم آليات الإلحاح؛ ومعدلات "أضف للسلة ثم تخلَّ عنها" لضبط كم مرة "يكاد" الإغراء يمسك اللاعب.
- **CFPB Complaints** → تأريض روايات "عواقب عدم الادخار" (ديون، سحب على المكشوف) بسيناريوهات مناسبة للعمر.

---

## 5) Child Development Psychology (أخلاقي)

| المصدر | الناشر | العينات | أبرز المتغيرات/النتائج | مجاني؟ | تجاري؟ | ملاءمة /10 |
|---|---|---|---|---|---|---|
| [Habit Formation in Young Children (Whitebread & Bingham 2013)](https://altorwealth.com/wp-content/uploads/2024/04/the-money-advice-service-habit-formation-and-learning-in-young-children-may2013.pdf) | Money Advice Service / Cambridge | تقرير تجميعي | **العادات المالية تتشكّل بعمر 7**؛ تحت 8 لا يميّزون الكماليات عن الضروريات؛ التركيز على التنظيم الذاتي | 🟢 مجاني | 🟡 Crown copyright — استشهد بالنتائج فقط | **10** |
| [CFPB Building Blocks of Youth Financial Capability](https://www.consumerfinance.gov/data-research/research-reports/building-blocks-help-youth-achieve-financial-capability/) | CFPB | نموذج + دليل قياس | 3 لبنات: **الوظيفة التنفيذية / العادات والأعراف / المعرفة واتخاذ القرار** حسب مراحل النمو + بنود قياس | 🟢 مجاني | 🟢 Public Domain | **9** |
| [CFPB Money As You Grow](https://www.consumerfinance.gov/consumer-tools/money-as-you-grow/) | CFPB | مورد ممارسة | معالم حسب العمر: تركيز، مثابرة، صبر، فهم المقايضات، الادخار نحو هدف | 🟢 مجاني | 🟢 Public Domain | **9** |
| [NICHD SECCYD (Marshmallow)](https://www.icpsr.umich.edu/web/DSDR/studies/21940) | NICHD / ICPSR | ~1,300 طفل (n=702 marshmallow @54 شهر) | **زمن انتظار تأجيل المكافأة**، الوظيفة التنفيذية، البيئة المنزلية، نتائج طولية | 🟢 (تسجيل) | 🟡 شروط ICPSR — لا إعادة توزيع | **8** |
| [PSID Child Development Supplement](https://psidonline.isr.umich.edu/cds/default.aspx) | Univ. Michigan ISR | CDS-I: ~3,563 طفل | قدرة معرفية، رفاه اجتماعي/عاطفي، **مذكرات استخدام الوقت**، دخل/تنشئة الوالدين | 🟢 (تسجيل) | 🟡 شروط ISR — لا إعادة توزيع | **7** |
| [NLSY79 Child & Young Adult](https://www.bls.gov/nls/nlsy79-children.htm) | US BLS | >10,000 طفل · 16 جولة | قدرة معرفية، مزاج، نمو حركي/اجتماعي، مشاكل سلوكية، كفاءة ذاتية | 🟢 مجاني | 🟢 Public Domain | **7** |

**كيفية الاستخدام داخل المنتج:**
- **Habit Formation + Money As You Grow + Building Blocks** = عمودك الفقري لتصميم **التدرّج العمري**: طبقة 5–7 تركّز على التنظيم الذاتي وتأجيل المكافأة (لا حساب)، لا تُدخل "الحاجة مقابل الرغبة" قبل ~8 سنوات، وكل معلم عمري = معيار إكمال مستوى.
- **SECCYD** → تأريض آليات تأجيل المكافأة على **توزيعات زمن الانتظار الحقيقية** ومُعدِّلاتها (الثقة/البيئة تؤثر على الانتظار). مهم: استخدم نتائج إعادة التحقق **لتجنّب المبالغة** — أطّر تأجيل المكافأة كمهارة قابلة للتعلّم لا كمصير حتمي.
- **PSID-CDS / NLSY** → معايرة منحنيات الصعوبة العمرية بمقاييس الانتباه/ضبط النفس الحقيقية (أطوال المؤقّتات، إيقاع المكافأة) بدل التخمين.

---

## الطقم الموصى به للبدء (آمن تجارياً)

| الغرض | المصدر | الترخيص |
|---|---|---|
| قياس فهم الطفل للمال (معايرة الصعوبة) | PISA 2022 FinLit | 🟢 |
| بنود ضبط النفس/تأجيل المكافأة | CFPB Well-Being (PUF) | 🟢 |
| نمذجة الأب الدافع | FINRA NFCS | 🟡 |
| schema التيليمتري + knowledge tracing | Jo Wilder + Open Game Data | 🟢 |
| محتوى الإغراءات (أسعار/مناسبات/ندرة) | UCI Online Shoppers + Online Retail + Mendeley Impulse | 🟢 |
| التدرّج العمري وأهداف التعلّم | CFPB Building Blocks + Money As You Grow | 🟢 |
| معايرة تأجيل المكافأة | UCI Drug (BIS-11) + IGT 617 | 🟢 |

**للبحث الداخلي فقط (لا تشحن نماذج مدرّبة عليها):** ITC Database, EdNet, Junyi, Retail Rocket, Instacart.

---

## Schema مقترح لقاعدة بيانات اللعبة

مبني بحيث يكون متوافقاً مع pipelines الـ knowledge-tracing المفتوحة (نمط Open Game Data / Jo Wilder) وجاهزاً للتوسّع التجاري.

```sql
-- ============ الحسابات والعلاقة أب/طفل ============
users (                        -- الآباء (الحساب المالك، COPPA: الموافقة عبر الأب)
  user_id UUID PK,
  email TEXT UNIQUE,
  role TEXT,                   -- 'parent'
  country TEXT, locale TEXT,
  created_at TIMESTAMPTZ
)

children (                     -- ملف الطفل (بيانات مجهّلة، بلا PII زائدة)
  child_id UUID PK,
  parent_user_id UUID FK->users,
  display_name TEXT,           -- اسم مستعار فقط
  birth_year INT,              -- السنة فقط لا التاريخ الكامل (تقليل PII)
  age_tier TEXT,               -- '5-7' | '8-10' | '11-13' حسب Building Blocks
  created_at TIMESTAMPTZ
)

-- ============ حلقة المكافأة (Robux وغيرها) ============
reward_requests (              -- الطفل يطلب مكافأة، الأب يموّلها، تبقى مقفلة
  request_id UUID PK,
  child_id UUID FK, parent_user_id UUID FK,
  reward_type TEXT,            -- 'robux' | 'giftcard' | ...
  amount_nominal NUMERIC,      -- 500
  currency TEXT,
  status TEXT,                 -- 'requested'|'funded'|'locked'|'unlocked'|'released'
  unlock_rule JSONB,           -- {stages_required, min_score, ...}
  funded_at TIMESTAMPTZ, unlocked_at TIMESTAMPTZ
)

reward_ledger (                -- سجل مالي لا يتغيّر (audit)
  entry_id BIGINT PK,
  request_id UUID FK,
  event TEXT,                  -- 'fund'|'lock'|'unlock'|'release'|'refund'
  amount NUMERIC, at TIMESTAMPTZ
)

-- ============ المحتوى التعليمي ============
concepts (                     -- شجرة المفاهيم (need-vs-want, delayed gratification ...)
  concept_id UUID PK,
  code TEXT,                   -- 'need_vs_want'
  min_age_tier TEXT,
  prereq_ids UUID[]            -- المتطلبات السابقة (نمط Junyi graph)
)

levels (
  level_id UUID PK,
  concept_id UUID FK,
  order_index INT,
  difficulty_base NUMERIC,     -- تُضبط ديناميكياً لاحقاً
  completion_rule JSONB
)

temptations (                  -- كتالوج الإغراءات (مشتق من consumer-behavior data)
  temptation_id UUID PK,
  archetype TEXT,              -- 'limited_offer'|'peer_pressure'|'flashy_item'|'impulse_buy'
  intensity NUMERIC,           -- معايرة من ITC/Mendeley
  cost_in_savings NUMERIC,
  social_pressure_flag BOOL,
  scarcity_flag BOOL,          -- من حقل available بـ Retail Rocket
  content JSONB                -- نص/أصول مناسبة للعمر
)

-- ============ التيليمتري (نمط Open Game Data) ============
sessions (
  session_id UUID PK,
  child_id UUID FK,
  app_version TEXT,
  started_at TIMESTAMPTZ, ended_at TIMESTAMPTZ,
  device JSONB
)

events (                       -- الجدول الأضخم — كل تفاعل موقّت
  event_id BIGINT PK,
  session_id UUID FK,
  child_id UUID FK,
  event_name TEXT,             -- 'level_start'|'temptation_shown'|'choice_made'|'wait'|'grab'|'hint'|'level_complete'
  sequence_index INT,
  elapsed_ms BIGINT,           -- منذ بداية الجلسة (نمط Jo Wilder)
  level_id UUID, temptation_id UUID,
  event_data JSONB,            -- {choice:'wait'|'buy', reaction_ms, hints_used, ...}
  at TIMESTAMPTZ
)

-- ============ التقدّم والقرارات (وقود الـ AI) ============
choices (                      -- كل قرار "انتظر مقابل خذ الآن" (نمط ITC/MCQ)
  choice_id BIGINT PK,
  child_id UUID FK, level_id UUID, temptation_id UUID,
  sooner_value NUMERIC, later_value NUMERIC, delay_units INT,
  decision TEXT,               -- 'wait_for_later' | 'take_now'
  reaction_ms INT,             -- سرعة الاندفاع
  outcome TEXT,                -- 'resisted' | 'gave_in'
  at TIMESTAMPTZ
)

progress (                     -- حالة الطفل الحالية لكل مفهوم
  child_id UUID, concept_id UUID,
  mastery NUMERIC,             -- 0..1 (knowledge tracing)
  attempts INT, resisted_count INT, gave_in_count INT,
  current_difficulty NUMERIC,  -- يعدّلها نموذج الصعوبة
  estimated_discount_k NUMERIC,-- معدل الخصم المقدّر (من MCQ logic)
  updated_at TIMESTAMPTZ,
  PRIMARY KEY (child_id, concept_id)
)

encouragement_events (         -- أي رسالة تشجيع عُرضت وأثرها (تدريب bandit)
  id BIGINT PK,
  child_id UUID FK, message_id TEXT,
  context JSONB,               -- {after:'gave_in', streak:2, mastery:0.4}
  shown_at TIMESTAMPTZ,
  next_choice_outcome TEXT     -- reward signal: هل تحسّن القرار التالي؟
)

model_predictions (            -- تسجيل تنبؤات الـ AI للمراقبة والتقييم
  id BIGINT PK, child_id UUID FK,
  model_name TEXT, model_version TEXT,
  input_features JSONB, prediction JSONB, at TIMESTAMPTZ
)
```

---

## البيانات التي تُجمع من المستخدم داخل اللعبة

> مبدأ COPPA/GDPR-K: **الحد الأدنى من البيانات**، موافقة الأب، بلا PII للطفل، ونمذجة اللاعب على الجهاز قدر الإمكان.

**أساسية (لازمة للحلقة):**
- طلب المكافأة: النوع، القيمة، التمويل، حالة القفل/الفتح.
- الفئة العمرية (السنة فقط) لاختيار الطبقة.
- تقدّم المستويات والمفاهيم (mastery لكل مفهوم).

**سلوكية (وقود الـ AI) — الأهم لأنها لا توجد في أي dataset مفتوح:**
- لكل إغراء: `temptation_id`, نوع الإغراء، القرار (انتظر/خذ الآن)، **زمن رد الفعل (ms)**، النتيجة (قاوم/استسلم).
- سلاسل المقاومة/الاستسلام (streaks)، عدد المحاولات، استخدام التلميحات.
- المؤقّت المتبقّي عند اتخاذ القرار (قياس الإلحاح).
- زمن كل جلسة، معدل العودة (retention)، نقطة التوقّف داخل المستوى.
- استجابة الطفل لرسائل التشجيع (تحسّن القرار التالي أم لا).

**اختيارية/سياقية (بموافقة صريحة):**
- الدولة/اللغة (للتوطين والمعايرة).
- استبيان قصير مُكيّف للأطفال لتقدير "قابلية الإغراء" (مشتق من MCQ/Mendeley).

**لا تُجمع:** اسم حقيقي كامل، تاريخ ميلاد كامل، موقع دقيق، أي معرّف قابل للربط بالطفل خارج اللعبة.

---

## بيانات تدريب نماذج الـ AI (4 مهام)

كل الميزات تأتي من جداول `events / choices / progress / encouragement_events` أعلاه. البيانات المفتوحة (CC BY فقط) تُستخدم للـ **bootstrapping/pretraining** والبيانات الخاصة للـ fine-tuning.

**١. اختيار نوع الإغراء المناسب للطفل**
- النوع: تصنيف/توصية (contextual bandit).
- Features: mastery الحالي لكل مفهوم، تاريخ القرارات حسب archetype، معدل الخصم المقدّر، الفئة العمرية، آخر النتائج، زمن رد الفعل المتوسط.
- Target: archetype الإغراء الذي يعظّم التعلّم دون إحباط.
- Bootstrap من: Mendeley Impulse (أوزان أنواع الإغراء)، UCI Online Shoppers (تأثير المناسبة).

**٢. تعديل مستوى الصعوبة (Dynamic Difficulty)**
- النوع: انحدار/سياسة تكيّفية.
- Features: mastery، نسبة المقاومة الأخيرة، زمن رد الفعل، محاولات/تلميحات، إشارات الإحباط (تكرار الفشل، الخروج المبكر).
- Target: `current_difficulty` التالي (قيمة الإغراء × التأخير) قرب "منطقة النمو" (نجاح ~70–80%).
- Bootstrap من: ITC/MCQ (منحنيات نقطة اللامبالاة)، Jo Wilder/OULAD (منحنيات التعلّم والانخراط).

**٣. اختيار رسالة التشجيع المناسبة**
- النوع: contextual bandit / RL (المكافأة = تحسّن القرار التالي).
- Features: نتيجة الحدث السابق (استسلم/قاوم)، الـ streak، mastery، الفئة العمرية، الوقت داخل الجلسة.
- Target: `message_id` الذي يرفع احتمال المقاومة التالية.
- إشارة التدريب: جدول `encouragement_events.next_choice_outcome`.
- تأطير أخلاقي: من Building Blocks/Money As You Grow — كافئ الصبر والمثابرة، لا تُشعِر الطفل بالذنب.

**٤. توقّع احتمال نجاح الطفل في الادخار**
- النوع: تصنيف احتمالي (calibrated).
- Features: اتجاه mastery عبر الزمن، نسبة المقاومة، انتظام العودة، معدل الخصم المقدّر، طول streaks، عمر × مقاييس ضبط النفس.
- Target: هل أكمل الطفل مسار الادخار وفتح المكافأة دون "انهيار"؟
- Bootstrap من: CFPB Well-Being (بنود ضبط النفس/التوجه المستقبلي ↔ سلوك الادخار)، PISA (كفاءة ↔ سلوك)، SECCYD (زمن الانتظار ↔ النتائج).
- استخدام أخلاقي: للتدخّل الداعم (مزيد تشجيع/سقالات)، **لا** لوصم الطفل أو التنبؤ بمصيره.

---

## الفجوات والخطوات التالية

1. **الفجوة الحرجة:** لا بيانات مفتوحة عن ادخار/تأجيل مكافأة الأطفال الصغار → اجمع بياناتك الخاصة عبر التيليمتري (بموافقة الأب). هذه ستكون **الميزة التنافسية والأصل الدفاعي** للمنتج.
2. ابدأ فوراً بتصميم schema الأحداث بنمط Open Game Data حتى تصبح بياناتك متوافقة مع pipelines المفتوحة عند جمعها.
3. للبيانات المُطبّقة قبل توفّر بياناتك: استخدم الطقم الآمن (CC BY / Public Domain) للـ bootstrapping والبروفايلات الافتراضية.
4. **الترخيص:** لا تشحن نماذج مدرّبة على ITC/EdNet/Junyi/Retail Rocket/Instacart (NC).
5. **الأخلاقيات:** COPPA/GDPR-K، نمذجة على الجهاز، تأطير تأجيل المكافأة كمهارة قابلة للتعلّم لا كحكم على الطفل.
```
