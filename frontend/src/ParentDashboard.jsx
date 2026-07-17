import { useEffect, useState } from "react";
import { api } from "./api.js";

const AGE_GROUPS = ["5-7", "8-10", "11-13"];

export default function ParentDashboard({ token, onPlay, onLogout }) {
  const [children, setChildren] = useState([]);
  const [error, setError] = useState("");
  const [nickname, setNickname] = useState("");
  const [ageGroup, setAgeGroup] = useState("8-10");
  const [insights, setInsights] = useState({}); // child_id -> insights

  async function refresh() {
    try {
      setChildren(await api.listChildren(token));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function addChild(e) {
    e.preventDefault();
    setError("");
    try {
      await api.createChild(token, nickname, ageGroup);
      setNickname("");
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadInsights(childId) {
    try {
      const data = await api.insights(token, childId);
      setInsights((prev) => ({ ...prev, [childId]: data }));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <div className="row spread">
        <h2>لوحة الأب</h2>
        <button className="ghost" onClick={onLogout}>
          خروج
        </button>
      </div>

      <div className="card">
        <h3>إضافة طفل</h3>
        <form onSubmit={addChild} className="row" style={{ alignItems: "flex-end" }}>
          <div className="field">
            <label>الاسم المستعار</label>
            <input value={nickname} onChange={(e) => setNickname(e.target.value)} required />
          </div>
          <div className="field">
            <label>الفئة العمرية</label>
            <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)}>
              {AGE_GROUPS.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
          <button type="submit">إضافة</button>
        </form>
      </div>

      {error && <div className="error">{error}</div>}

      {children.map((child) => (
        <ChildCard
          key={child.id}
          token={token}
          child={child}
          insights={insights[child.id]}
          onLoadInsights={() => loadInsights(child.id)}
          onPlay={onPlay}
        />
      ))}
      {children.length === 0 && <p className="muted">لا يوجد أطفال بعد — أضف طفلاً للبدء.</p>}
    </>
  );
}

function ChildCard({ token, child, insights, onLoadInsights, onPlay }) {
  const [pin, setPin] = useState("");
  const [amount, setAmount] = useState("500");
  const [reward, setReward] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function savePin() {
    setError("");
    setMsg("");
    try {
      await api.setPin(token, child.id, pin);
      setMsg("تم حفظ الرقم السري ✅");
    } catch (err) {
      setError(err.message);
    }
  }

  async function fund() {
    setError("");
    setMsg("");
    try {
      const r = await api.createReward(token, child.id, amount);
      setReward(r);
      setMsg(`تم قفل ${r.amount} Robux 🔒`);
    } catch (err) {
      setError(err.message);
    }
  }

  async function play() {
    setError("");
    try {
      const res = await api.childLogin(token, child.id, pin);
      onPlay({ childToken: res.access_token, child, reward });
    } catch (err) {
      setError("أدخل الرقم السري الصحيح للطفل أولاً");
    }
  }

  return (
    <div className="card">
      <div className="row spread">
        <h3>
          {child.nickname} <span className="tag">{child.age_group}</span>
        </h3>
        <button className="ghost" onClick={onLoadInsights}>
          الرؤى
        </button>
      </div>

      <div className="row" style={{ alignItems: "flex-end" }}>
        <div className="field" style={{ maxWidth: 160 }}>
          <label>الرقم السري للطفل (٤ أرقام)</label>
          <input
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            inputMode="numeric"
            maxLength={8}
            placeholder="****"
          />
        </div>
        <button className="ghost" onClick={savePin}>
          حفظ الرقم
        </button>
        <div className="field" style={{ maxWidth: 160 }}>
          <label>قيمة المكافأة (Robux)</label>
          <input value={amount} onChange={(e) => setAmount(e.target.value)} inputMode="numeric" />
        </div>
        <button className="gold" onClick={fund}>
          اشترِ واقفل المكافأة
        </button>
        <button onClick={play}>🎮 العب الآن</button>
      </div>

      {msg && <p className="muted">{msg}</p>}
      {error && <div className="error">{error}</div>}

      {insights && (
        <div style={{ marginTop: 12 }}>
          <div className="ai">
            <div className="kpi">
              <b>{Math.round((insights.success_prediction.probability || 0) * 100)}%</b>
              <span>احتمال الإكمال</span>
            </div>
            <div className="kpi">
              <b>{Math.round((insights.resist_rate || 0) * 100)}%</b>
              <span>نسبة المقاومة</span>
            </div>
            <div className="kpi">
              <b>{insights.total_decisions}</b>
              <span>عدد القرارات</span>
            </div>
          </div>
          <SkillBars skills={insights.skills} />
          <p className="muted">
            الوحوش المهزومة: {insights.defeated_monsters.join("، ") || "لا شيء بعد"}
          </p>
        </div>
      )}
    </div>
  );
}

export function SkillBars({ skills }) {
  const items = [
    ["الصبر", skills.patience],
    ["الوعي بالادخار", skills.saving_awareness],
    ["ضبط الاندفاع", skills.impulse_control],
  ];
  return (
    <div className="skills">
      {items.map(([label, val]) => (
        <div className="skill" key={label}>
          <div className="row spread">
            <span className="muted">{label}</span>
            <span className="muted">{Math.round(val)}</span>
          </div>
          <div className="bar">
            <span style={{ width: `${Math.min(100, val)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
