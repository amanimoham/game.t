// Hackathon deck generator — "محاربة المغريات" (Arabic RTL, dark navy + orange).
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5

const BG = "141A33";
const PANEL = "1F2748";
const PANEL2 = "27305A";
const ORANGE = "FF7A3C";
const GOLD = "FFC24D";
const TEXT = "EEF1FF";
const MUTED = "A7ADCE";
const GOOD = "34D399";
const FONT = "Arial";
const W = 13.3;

function slideBase(title) {
  const s = pres.addSlide();
  s.background = { color: BG };
  if (title) {
    s.addText(title, {
      x: 0.6, y: 0.4, w: W - 1.2, h: 0.9,
      align: "right", rtlMode: true, fontFace: FONT, fontSize: 32, bold: true, color: ORANGE,
    });
  }
  return s;
}

function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.12,
    fill: { color: fill || PANEL },
    line: { color: PANEL2, width: 1 },
    shadow: { type: "outer", color: "0A0E20", blur: 8, offset: 3, angle: 90, opacity: 0.5 },
  });
}

function stat(s, x, y, w, number, label, color) {
  card(s, x, y, w, 1.7);
  const n = String(number).length;
  const fs = n <= 4 ? 40 : n <= 7 ? 30 : 23;
  s.addText(number, {
    x, y: y + 0.18, w, h: 0.85, align: "center", valign: "middle", rtlMode: true,
    fontFace: FONT, fontSize: fs, bold: true, color: color || GOLD, margin: 0,
  });
  s.addText(label, {
    x: x + 0.15, y: y + 1.02, w: w - 0.3, h: 0.55, align: "center", rtlMode: true,
    fontFace: FONT, fontSize: 13, color: MUTED, margin: 0, valign: "top",
  });
}

function row(s, x, y, w, h, emoji, header, desc) {
  card(s, x, y, w, h);
  // emoji badge circle (right side for RTL)
  const cx = x + w - 0.95;
  s.addShape(pres.ShapeType.ellipse, { x: cx, y: y + 0.25, w: 0.6, h: 0.6, fill: { color: PANEL2 } });
  s.addText(emoji, { x: cx, y: y + 0.25, w: 0.6, h: 0.6, align: "center", valign: "middle", fontSize: 22, margin: 0 });
  s.addText(header, {
    x: x + 0.3, y: y + 0.22, w: w - 1.4, h: 0.5, align: "right", rtlMode: true,
    fontFace: FONT, fontSize: 17, bold: true, color: TEXT, margin: 0, valign: "middle",
  });
  s.addText(desc, {
    x: x + 0.3, y: y + 0.72, w: w - 1.4, h: h - 0.9, align: "right", rtlMode: true,
    fontFace: FONT, fontSize: 12.5, color: MUTED, margin: 0, valign: "top",
  });
}

function chip(s, x, y, w, label) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h: 0.5, rectRadius: 0.25, fill: { color: PANEL2 }, line: { color: PANEL2, width: 1 },
  });
  s.addText(label, { x, y, w, h: 0.5, align: "center", valign: "middle", rtlMode: true, fontFace: FONT, fontSize: 13, color: TEXT, margin: 0 });
}

function pageNote(s, txt) {
  s.addText(txt, { x: 0.6, y: 6.9, w: W - 1.2, h: 0.4, align: "right", rtlMode: true, fontFace: FONT, fontSize: 11, italic: true, color: MUTED, margin: 0 });
}

// ---------- Slide 1: Title ----------
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addShape(pres.ShapeType.ellipse, { x: 5.9, y: 1.5, w: 1.5, h: 1.5, fill: { color: PANEL } });
  s.addText("🛡️", { x: 5.9, y: 1.5, w: 1.5, h: 1.5, align: "center", valign: "middle", fontSize: 54, margin: 0 });
  s.addText("محاربة المغريات", {
    x: 1, y: 3.15, w: W - 2, h: 1.0, align: "center", rtlMode: true, fontFace: FONT, fontSize: 54, bold: true, color: ORANGE, margin: 0,
  });
  s.addText("لعبة تعليمية تفاعلية لرفع الوعي الادخاري لدى الأطفال", {
    x: 1, y: 4.2, w: W - 2, h: 0.6, align: "center", rtlMode: true, fontFace: FONT, fontSize: 22, color: TEXT, margin: 0,
  });
  s.addText("الطفل يفتح مكافأته الرقمية بمحاربة المغريات وتعلّم تأجيل المكافأة", {
    x: 1, y: 4.9, w: W - 2, h: 0.5, align: "center", rtlMode: true, fontFace: FONT, fontSize: 15, italic: true, color: MUTED, margin: 0,
  });
  s.addText("عرض هاكاثون  •  نموذج أولي يعمل", {
    x: 1, y: 6.6, w: W - 2, h: 0.4, align: "center", rtlMode: true, fontFace: FONT, fontSize: 13, color: GOLD, margin: 0,
  });
}

// ---------- Slide 2: Problem ----------
{
  const s = slideBase("المشكلة");
  stat(s, 0.7, 1.7, 3.85, "بعمر 7", "تتشكّل العادات المالية للطفل (دراسة كامبريدج)", GOLD);
  stat(s, 4.72, 1.7, 3.85, "0", "بيانات مفتوحة عن ادخار الأطفال الصغار", ORANGE);
  stat(s, 8.75, 1.7, 3.85, "#1", "مشكلة edtech: التحفيز والاحتفاظ", GOOD);
  card(s, 0.7, 3.7, 11.9, 2.7);
  s.addText([
    { text: "الأطفال لا يملكون أداة ممتعة تعلّمهم الادخار وتأجيل المكافأة.", options: { bullet: true, breakLine: true } },
    { text: "التطبيقات التعليمية مملّة — الطفل يتركها بسرعة، والأب لا يرى أثراً.", options: { bullet: true, breakLine: true } },
    { text: "لا توجد بيانات مفتوحة تقيس سلوك ادخار الأطفال = فجوة سوقية وفرصة أصل بيانات خاص.", options: { bullet: true, breakLine: true } },
    { text: "النتيجة: جيل ينشأ دون مهارات مالية أساسية.", options: { bullet: true } },
  ], { x: 1.0, y: 3.95, w: 11.3, h: 2.2, align: "right", rtlMode: true, fontFace: FONT, fontSize: 16, color: TEXT, lineSpacingMultiple: 1.3 });
}

// ---------- Slide 3: Solution ----------
{
  const s = slideBase("الحل");
  const steps = [
    ["1", "يطلب الطفل مكافأة", "مثل 500 Robux"],
    ["2", "يشتريها الأب وتُقفل", "محفوظة داخل النظام"],
    ["3", "يحارب المغريات", "قرارات مالية سليمة"],
    ["4", "يفتح المكافأة تدريجياً", "تعلّم بالممارسة"],
  ];
  const w = 2.85, gap = 0.23;
  let x = 0.7;
  for (const [n, h, d] of steps) {
    card(s, x, 2.0, w, 2.6);
    s.addShape(pres.ShapeType.ellipse, { x: x + w / 2 - 0.35, y: 2.3, w: 0.7, h: 0.7, fill: { color: ORANGE } });
    s.addText(n, { x: x + w / 2 - 0.35, y: 2.3, w: 0.7, h: 0.7, align: "center", valign: "middle", fontFace: FONT, fontSize: 24, bold: true, color: BG, margin: 0 });
    s.addText(h, { x: x + 0.15, y: 3.2, w: w - 0.3, h: 0.7, align: "center", rtlMode: true, fontFace: FONT, fontSize: 16, bold: true, color: TEXT, margin: 0 });
    s.addText(d, { x: x + 0.15, y: 3.9, w: w - 0.3, h: 0.6, align: "center", rtlMode: true, fontFace: FONT, fontSize: 12.5, color: MUTED, margin: 0 });
    x += w + gap;
  }
  pageNote(s, "التعلّم بالممارسة: انتظار المكافأة نفسه يصبح لعبة تُدرّب تأجيل المكافأة.");
}

// ---------- Slide 4: Evolved idea ----------
{
  const s = slideBase("الفكرة المطوّرة");
  const rows = [
    ["🗺️", "خزنة الكنز", "إعادة تأطير القفل كمغامرة لا كعقوبة — الطفل يحرّر كنزه من الوحوش."],
    ["🎮", "متعة أولاً + فتح تدريجي", "اللعبة ممتعة بذاتها، والمكافأة تُفتح على دفعات (33% → 67% → 100%)."],
    ["🤖", "تخصيص بالذكاء الاصطناعي", "اختيار الوحش والصعوبة والرسالة حسب مستوى كل طفل."],
    ["📊", "لوحة رؤى للأب", "نمو الصبر وضبط الاندفاع — القيمة التي يدفع الأب مقابلها فعلاً."],
  ];
  let y = 1.7;
  for (const [e, h, d] of rows) { row(s, 0.7, y, 11.9, 1.15, e, h, d); y += 1.28; }
}

// ---------- Slide 5: Data sources ----------
{
  const s = slideBase("مصادر البيانات");
  const data = [
    ["PISA 2022 Financial Literacy", "OECD — معايرة الصعوبة", GOLD],
    ["CFPB Well-Being (ضبط النفس)", "حكومي — تأجيل المكافأة", GOOD],
    ["UCI Online Shoppers", "سلوك الشراء والإلحاح", ORANGE],
    ["ITC / Kirby MCQ (خصم زمني)", "قيم الإغراء ونقطة اللامبالاة", GOLD],
    ["Jo Wilder / Open Game Data", "تيليمتري ألعاب أطفال", GOOD],
    ["CFPB Building Blocks", "التدرّج العمري", ORANGE],
  ];
  const w = 3.85, hh = 1.5, gx = 0.2, gy = 0.25;
  let i = 0;
  for (const [name, use, col] of data) {
    const cxx = 0.7 + (i % 3) * (w + gx);
    const cyy = 1.75 + Math.floor(i / 3) * (hh + gy);
    card(s, cxx, cyy, w, hh);
    s.addText(name, { x: cxx + 0.2, y: cyy + 0.2, w: w - 0.4, h: 0.7, align: "right", rtlMode: false, fontFace: FONT, fontSize: 13.5, bold: true, color: col, margin: 0, valign: "top" });
    s.addText(use, { x: cxx + 0.2, y: cyy + 0.85, w: w - 0.4, h: 0.5, align: "right", rtlMode: true, fontFace: FONT, fontSize: 12, color: MUTED, margin: 0 });
    i++;
  }
  pageNote(s, "كل مصدر موثّق برابط رسمي — الأولوية للبيانات المفتوحة (Kaggle, UCI, OECD, CFPB).");
}

// ---------- Slide 6: Data used & cleaning ----------
{
  const s = slideBase("البيانات: الاستخدام والتنظيف");
  card(s, 6.75, 1.7, 5.85, 4.7);
  s.addText("البيانات المستخدمة", { x: 6.95, y: 1.9, w: 5.4, h: 0.5, align: "right", rtlMode: true, fontFace: FONT, fontSize: 18, bold: true, color: GOLD, margin: 0 });
  s.addText([
    { text: "درجات الكفاءة المالية (PISA)", options: { bullet: true, breakLine: true } },
    { text: "بنود ضبط النفس والتوجه المستقبلي (CFPB)", options: { bullet: true, breakLine: true } },
    { text: "أنماط الشراء والإلحاح (UCI)", options: { bullet: true, breakLine: true } },
    { text: "منحنيات الخصم الزمني (ITC/MCQ)", options: { bullet: true, breakLine: true } },
    { text: "تيليمتري اللعبة (بياناتنا الخاصة)", options: { bullet: true } },
  ], { x: 6.95, y: 2.5, w: 5.4, h: 3.7, align: "right", rtlMode: true, fontFace: FONT, fontSize: 14.5, color: TEXT, lineSpacingMultiple: 1.35 });

  card(s, 0.7, 1.7, 5.85, 4.7);
  s.addText("التنظيف والتجهيز", { x: 0.9, y: 1.9, w: 5.4, h: 0.5, align: "right", rtlMode: true, fontFace: FONT, fontSize: 18, bold: true, color: GOOD, margin: 0 });
  s.addText([
    { text: "فرز التراخيص: نشحن CC BY / Public Domain فقط، وNC للبحث.", options: { bullet: true, breakLine: true } },
    { text: "إزالة أي بيانات تعريف (بلا PII للأطفال).", options: { bullet: true, breakLine: true } },
    { text: "تطبيع القيم وتوحيد المقاييس (0–100).", options: { bullet: true, breakLine: true } },
    { text: "تحويل الأنماط إلى بروفايلات افتراضية للمعايرة.", options: { bullet: true, breakLine: true } },
    { text: "توليد ميزات (features) متوافقة مع نموذج ML لاحقاً.", options: { bullet: true } },
  ], { x: 0.9, y: 2.5, w: 5.4, h: 3.7, align: "right", rtlMode: true, fontFace: FONT, fontSize: 14.5, color: TEXT, lineSpacingMultiple: 1.35 });
}

// ---------- Slide 7: Data usage ----------
{
  const s = slideBase("كيف نستخدم البيانات");
  const rows = [
    ["🎯", "معايرة الصعوبة", "نطاقات كفاءة PISA تضبط صعوبة المراحل."],
    ["👾", "نمذجة الإغراءات", "سلوك المستهلك يصمّم أنواع الوحوش وشدّتها."],
    ["🧠", "قياس ضبط النفس", "بنود CFPB تؤطّر مقاييس الصبر والاندفاع."],
    ["🔒", "أصلنا الدفاعي", "تيليمتري اللعبة = بيانات لا يملكها أحد لتدريب الـ AI."],
  ];
  const w = 5.85, hh = 1.9;
  const pos = [[0.7, 1.75], [6.75, 1.75], [0.7, 3.85], [6.75, 3.85]];
  rows.forEach((r, i) => row(s, pos[i][0], pos[i][1], w, hh, r[0], r[1], r[2]));
}

// ---------- Slide 8: Tech stack ----------
{
  const s = slideBase("التقنيات المستخدمة");
  const chips = ["FastAPI", "PostgreSQL", "SQLAlchemy 2.0", "Alembic", "Redis", "Celery", "Docker", "React + Vite", "JWT + Refresh", "Argon2", "Pytest", "Render"];
  const cols = 4, cw = 2.85, ch = 0.5, gx = 0.2, gy = 0.35;
  chips.forEach((c, i) => {
    const x = 0.7 + (i % cols) * (cw + gx);
    const y = 1.8 + Math.floor(i / cols) * (ch + gy);
    chip(s, x, y, cw, c);
  });
  card(s, 0.7, 4.7, 11.9, 1.7);
  s.addText([
    { text: "معماريّة: ", options: { bold: true, color: GOLD } },
    { text: "Modular Monolith قابل للتوسّع  •  ", options: {} },
    { text: "دفتر أستاذ مالي غير قابل للتغيير (escrow)  •  ", options: {} },
    { text: "تيليمتري append-only (event-sourced)  •  ", options: {} },
    { text: "AI كاستراتيجية قابلة للحقن (rule-engine → ML)", options: {} },
  ], { x: 0.95, y: 4.95, w: 11.4, h: 1.2, align: "right", rtlMode: true, fontFace: FONT, fontSize: 14.5, color: TEXT, lineSpacingMultiple: 1.3 });
}

// ---------- Slide 9: Prototype ----------
{
  const s = slideBase("النموذج الأولي (يعمل الآن)");
  const steps = [
    ["دخول الأب", "تسجيل آمن (JWT)"],
    ["لوحة الأب", "طفل + PIN + قفل مكافأة"],
    ["اللعبة", "خزنة + وحوش + قرارات"],
    ["الرؤى", "نمو المهارات + توقّع AI"],
  ];
  const w = 2.85, gap = 0.23;
  let x = 0.7;
  steps.forEach(([h, d], i) => {
    card(s, x, 2.1, w, 2.3);
    s.addText(String(i + 1), { x: x + 0.2, y: 2.25, w: 0.6, h: 0.5, align: "right", rtlMode: true, fontFace: FONT, fontSize: 20, bold: true, color: ORANGE, margin: 0 });
    s.addText(h, { x: x + 0.2, y: 2.95, w: w - 0.4, h: 0.6, align: "right", rtlMode: true, fontFace: FONT, fontSize: 16, bold: true, color: TEXT, margin: 0 });
    s.addText(d, { x: x + 0.2, y: 3.55, w: w - 0.4, h: 0.7, align: "right", rtlMode: true, fontFace: FONT, fontSize: 12.5, color: MUTED, margin: 0 });
    x += w + gap;
  });
  pageNote(s, "يعمل بدون Docker عبر Postgres مدمج + fakeredis — جاهز للعرض المباشر.");
}

// ---------- Slide 10: Results ----------
{
  const s = slideBase("النتائج");
  stat(s, 0.7, 1.75, 3.85, "26/26", "اختبار ناجح (يشمل e2e على Postgres حقيقي)", GOOD);
  stat(s, 4.72, 1.75, 3.85, "33→67→100%", "فتح الخزنة تدريجياً (تحقّق حيّ)", GOLD);
  stat(s, 8.75, 1.75, 3.85, "17", "REST endpoints جاهزة", ORANGE);
  card(s, 0.7, 3.75, 11.9, 2.65);
  s.addText([
    { text: "تدفّق كامل مُتحقّق: تسجيل → طفل → قفل مكافأة → لعب → فتح 500 Robux → لوحة الأب.", options: { bullet: true, breakLine: true } },
    { text: "الواجهة تبني في أقل من ثانيتين، وجُرّبت حيّاً في المتصفح.", options: { bullet: true, breakLine: true } },
    { text: "بق حقيقي اكتشفه الاختبار في المتصفح (تقدّم المكافأة) — وأُصلح وأُثبت.", options: { bullet: true, breakLine: true } },
    { text: "منتج قابل للعرض المباشر، لا مجرد شرائح.", options: { bullet: true } },
  ], { x: 0.95, y: 4.0, w: 11.4, h: 2.2, align: "right", rtlMode: true, fontFace: FONT, fontSize: 15.5, color: TEXT, lineSpacingMultiple: 1.3 });
}

// ---------- Slide 11: AI ----------
{
  const s = slideBase("الذكاء الاصطناعي (rule-engine → ML)");
  const rows = [
    ["🎯", "اختيار الوحش", "يستهدف أضعف مهارة لدى الطفل."],
    ["⚖️", "تعديل الصعوبة", "يبقي النجاح في منطقة النمو (~70–80%)."],
    ["💬", "رسالة التشجيع", "داعمة لا موبّخة، حسب السياق."],
    ["🔮", "توقّع الإكمال", "احتمال إكمال الرحلة يُعرض للأب."],
  ];
  const w = 5.85, hh = 1.55;
  const pos = [[0.7, 1.7], [6.75, 1.7], [0.7, 3.4], [6.75, 3.4]];
  rows.forEach((r, i) => row(s, pos[i][0], pos[i][1], w, hh, r[0], r[1], r[2]));
  card(s, 0.7, 5.2, 11.9, 1.2, PANEL2);
  s.addText("المسار: نفس الـ features الحيّة ← dataset تدريب (CSV/JSONL مع label الإكمال) ← نموذج ML مستقبلاً بلا إعادة بناء.", {
    x: 0.95, y: 5.35, w: 11.4, h: 0.9, align: "right", rtlMode: true, fontFace: FONT, fontSize: 14, bold: true, color: GOLD, margin: 0, valign: "middle",
  });
}

// ---------- Slide 12: Future ----------
{
  const s = slideBase("المستقبل");
  const items = [
    ["نماذج ML حقيقية", "تحلّ محل قواعد الـ AI باستخدام بياناتنا المتراكمة."],
    ["دفع وتسليم حقيقي", "تكامل Stripe + أكواد Robux."],
    ["محتوى أوسع", "وحوش ومراحل ومسارات تعلّم أكثر."],
    ["توسّع وإطلاق", "نشر على Render لآلاف الأطفال."],
  ];
  let y = 1.8;
  items.forEach(([h, d], i) => {
    card(s, 0.7, y, 11.9, 1.05);
    s.addShape(pres.ShapeType.ellipse, { x: 11.35, y: y + 0.27, w: 0.5, h: 0.5, fill: { color: GOOD } });
    s.addText(String(i + 1), { x: 11.35, y: y + 0.27, w: 0.5, h: 0.5, align: "center", valign: "middle", fontFace: FONT, fontSize: 18, bold: true, color: BG, margin: 0 });
    s.addText(h, { x: 0.95, y: y + 0.13, w: 10, h: 0.45, align: "right", rtlMode: true, fontFace: FONT, fontSize: 17, bold: true, color: TEXT, margin: 0 });
    s.addText(d, { x: 0.95, y: y + 0.55, w: 10, h: 0.4, align: "right", rtlMode: true, fontFace: FONT, fontSize: 12.5, color: MUTED, margin: 0 });
    y += 1.18;
  });
  s.addText("محاربة المغريات — نحوّل انتظار المكافأة إلى مهارة تدوم مدى الحياة.", {
    x: 0.7, y: 6.7, w: W - 1.4, h: 0.5, align: "center", rtlMode: true, fontFace: FONT, fontSize: 15, italic: true, color: ORANGE, margin: 0,
  });
}

pres.writeFile({ fileName: "hackathon.pptx" }).then((f) => console.log("WROTE", f));
