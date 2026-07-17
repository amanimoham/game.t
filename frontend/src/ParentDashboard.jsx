import { useEffect, useState } from "react";
import { api } from "./api.js";
import { Bar, Empty, ErrorBox, Header, Metric, SavingBalanceCard, SkillCard, Spinner, StatusBadge } from "./ui.jsx";
import SmartBankingSection from "./banking.jsx";
import AddRewardFlow from "./payment.jsx";

const AGE_GROUPS = ["5-7", "8-10", "11-13"];

export default function ParentDashboard({ token, onPlay, onLogout }) {
  const [children, setChildren] = useState([]);
  const [insights, setInsights] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    api.me(token).then((u) => setEmail(u.email)).catch(() => {});
  }, []);

  const totals = children.reduce(
    (acc, c) => {
      const r = (insights[c.id]?.rewards || [])[0];
      if (r) { acc.target += Number(r.amount); acc.current += Number(r.unlocked_amount); }
      return acc;
    },
    { target: 0, current: 0 }
  );

  async function refresh() {
    setError("");
    try {
      const kids = await api.listChildren(token);
      setChildren(kids);
      const entries = await Promise.all(
        kids.map(async (c) => {
          try { return [c.id, await api.insights(token, c.id)]; }
          catch { return [c.id, null]; }
        })
      );
      setInsights(Object.fromEntries(entries));
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  useEffect(() => { refresh(); }, []);

  return (
    <>
      <Header email={email} onLogout={onLogout} />

      <SavingBalanceCard current={totals.current} target={totals.target} />

      <AddChildCard token={token} onAdded={refresh} />

      {!loading && children.length > 0 && (
        <AddRewardFlow token={token} children={children} onDone={refresh} />
      )}

      <ErrorBox>{error}</ErrorBox>

      {loading ? (
        <div className="card"><Spinner label="جارٍ تحميل رحلات الأبطال..." /></div>
      ) : children.length === 0 ? (
        <div className="card"><Empty icon="🦸">لا يوجد أبطال بعد — أضف بطلاً لتبدأ رحلته التعليمية.</Empty></div>
      ) : (
        children.map((c) => (
          <ChildJourney key={c.id} token={token} child={c} data={insights[c.id]} onPlay={onPlay} onChanged={refresh} />
        ))
      )}

      <SmartBankingSection token={token} childrenList={children} />
    </>
  );
}

function AddChildCard({ token, onAdded }) {
  const [nickname, setNickname] = useState("");
  const [ageGroup, setAgeGroup] = useState("8-10");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function add(e) {
    e.preventDefault();
    setError(""); setBusy(true);
    try { await api.createChild(token, nickname, ageGroup); setNickname(""); onAdded(); }
    catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return (
    <div className="card">
      <div className="section-title"><span className="dot">➕</span><h2>إضافة بطل جديد</h2></div>
      <form onSubmit={add} className="row" style={{ alignItems: "flex-end" }}>
        <div className="field"><label>الاسم المستعار</label><input value={nickname} onChange={(e) => setNickname(e.target.value)} placeholder="اسم البطل" required /></div>
        <div className="field" style={{ maxWidth: 160 }}>
          <label>الفئة العمرية</label>
          <select value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)}>
            {AGE_GROUPS.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <button type="submit" className="btn" disabled={busy}>{busy ? "..." : "إضافة"}</button>
      </form>
      <ErrorBox>{error}</ErrorBox>
    </div>
  );
}

function ChildJourney({ token, child, data, onPlay, onChanged }) {
  const skills = data?.skills || { patience: 0, saving_awareness: 0, impulse_control: 0 };
  const rewards = data?.rewards || [];
  const reward = rewards[0] || null;
  const journey = reward?.progress_pct ?? 0;
  const xp = Math.round((skills.patience || 0) + (skills.saving_awareness || 0) + (skills.impulse_control || 0));
  const defeated = data?.defeated_monsters || [];
  const resist = Math.round((data?.resist_rate || 0) * 100);

  const [pin, setPin] = useState("");
  const [amount, setAmount] = useState("500");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function savePin() {
    setError(""); setMsg("");
    try { await api.setPin(token, child.id, pin); setMsg("تم حفظ الرقم السري ✅"); }
    catch (e) { setError(e.message); }
  }
  async function fund() {
    setError(""); setBusy(true);
    try { await api.createReward(token, child.id, amount); onChanged(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function play() {
    setError("");
    try { const res = await api.childLogin(token, child.id, pin); onPlay({ childToken: res.access_token, child, reward }); }
    catch { setError("احفظ الرقم السري ثم أدخله الصحيح للعب"); }
  }

  const nextChallenge = journey >= 100 ? "🎉 اكتملت المغامرة" : "التحدي التالي في المغامرة";

  return (
    <>
      {/* Hero — بطل الرحلة */}
      <div className="card card-hero">
        <div className="row spread">
          <div className="row" style={{ gap: 14 }}>
            <div className="brand-badge" style={{ background: "rgba(255,255,255,.18)" }}>🦸</div>
            <div>
              <div style={{ fontSize: 12, opacity: 0.85 }}>بطل الرحلة</div>
              <div style={{ fontSize: 22, fontWeight: 800 }}>{child.nickname}</div>
              <div className="row" style={{ gap: 6, marginTop: 6 }}>
                <span className="chip" style={{ background: "rgba(255,255,255,.16)", color: "#fff", border: 0 }}>الفئة {child.age_group}</span>
                <span className="chip" style={{ background: "rgba(255,255,255,.16)", color: "#fff", border: 0 }}>المرحلة الأولى</span>
              </div>
            </div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 30, fontWeight: 900 }}>{xp}</div>
            <div style={{ fontSize: 12, opacity: 0.85 }}>نقطة خبرة XP</div>
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <div className="row spread" style={{ marginBottom: 6 }}>
            <span style={{ fontSize: 13 }}>تقدّم الرحلة</span>
            <span style={{ fontSize: 13, fontWeight: 700 }}>{journey}%</span>
          </div>
          <div className="bar gold"><span style={{ width: `${journey}%` }} /></div>
        </div>
      </div>

      {/* Actions */}
      <div className="card tight">
        <div className="row" style={{ alignItems: "flex-end" }}>
          <div className="field" style={{ maxWidth: 170 }}>
            <label>الرقم السري للبطل (٤ أرقام)</label>
            <input value={pin} onChange={(e) => setPin(e.target.value)} inputMode="numeric" maxLength={8} placeholder="••••" />
          </div>
          <button className="btn-outline" onClick={savePin}>حفظ الرقم</button>
          <button className="btn" onClick={play}>🎮 العب الآن</button>
          {msg && <span className="muted" style={{ fontSize: 13 }}>{msg}</span>}
        </div>
        <ErrorBox>{error}</ErrorBox>
      </div>

      <div className="grid-2">
        {/* المكافأة الكبرى */}
        <div className="card">
          <div className="section-title"><span className="dot">🎁</span><h3>المكافأة الكبرى</h3></div>
          {reward ? (
            <div className="reward-card">
              <div className="row spread">
                <div className="amount">{Math.round(reward.amount)} <small>Robux</small></div>
                <StatusBadge status={reward.status} />
              </div>
              <div style={{ margin: "12px 0 6px" }}>
                <div className="row spread" style={{ marginBottom: 4 }}>
                  <span className="muted" style={{ fontSize: 12.5 }}>{Math.round(reward.unlocked_amount)} مفتوح</span>
                  <span className="muted" style={{ fontSize: 12.5 }}>{reward.progress_pct}%</span>
                </div>
                <div className="bar gold"><span style={{ width: `${reward.progress_pct}%` }} /></div>
              </div>
              <div className="reward-note">المكافأة محفوظة حتى إكمال الرحلة التعليمية.</div>
            </div>
          ) : (
            <>
              <Empty icon="🔒">لا توجد مكافأة بعد — اشترِ واقفل مكافأة ليبدأ التحدي.</Empty>
              <div className="row" style={{ alignItems: "flex-end" }}>
                <div className="field" style={{ maxWidth: 150 }}><label>قيمة المكافأة</label><input value={amount} onChange={(e) => setAmount(e.target.value)} inputMode="numeric" /></div>
                <button className="btn-gold" onClick={fund} disabled={busy}>{busy ? "..." : "اشترِ واقفل المكافأة"}</button>
              </div>
            </>
          )}
        </div>

        {/* تقدم المغامرة */}
        <div className="card">
          <div className="section-title"><span className="dot">🗺️</span><h3>تقدم المغامرة</h3></div>
          <div className="grid-2" style={{ gap: 12 }}>
            <Metric value={`${defeated.length}/3`} label="مراحل مكتملة" tone="green" />
            <Metric value={xp} label="نقاط الخبرة XP" tone="gold" />
            <Metric value={defeated.length} label="وحوش مهزومة" />
            <Metric value={`${resist}%`} label="نسبة القرارات الصائبة" />
          </div>
          <div style={{ marginTop: 14 }}>
            <div className="muted" style={{ fontSize: 12.5, marginBottom: 6 }}>الوحوش المهزومة</div>
            <div className="row" style={{ gap: 6 }}>
              {defeated.length ? defeated.map((m, i) => <span key={i} className="chip">{m}</span>) : <span className="muted" style={{ fontSize: 13 }}>لا شيء بعد</span>}
            </div>
            <div className="muted" style={{ fontSize: 13, marginTop: 12 }}>القادم: {nextChallenge}</div>
          </div>
        </div>
      </div>

      {/* مهارات مالية مكتسبة */}
      <div className="card">
        <div className="section-title"><span className="dot">🧠</span><h3>مهارات مالية مكتسبة</h3></div>
        <div className="grid-4">
          <SkillCard icon="⏳" name="الصبر وتأجيل المكافأة" value={skills.patience} />
          <SkillCard icon="🧭" name="اتخاذ القرار" value={resist} />
          <SkillCard icon="⚖️" name="التمييز بين الاحتياج والرغبة" value={skills.saving_awareness} />
          <SkillCard icon="🛡️" name="مقاومة المغريات" value={skills.impulse_control} />
        </div>
      </div>
    </>
  );
}
