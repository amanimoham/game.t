import { useEffect, useState } from "react";
import { api } from "./api.js";
import { Bar, ErrorBox, Spinner, StatusBadge } from "./ui.jsx";

const MONSTER_EMOJI = {
  instant_reward: "🛒",
  social_pressure: "👥",
  limited_offer: "⏳",
  spending: "💸",
};
const MONSTER_NAME = {
  instant_reward: "وحش الشراء السريع",
  social_pressure: "وحش ضغط الأصدقاء",
  limited_offer: "وحش العروض الوهمية",
  spending: "وحش الإنفاق",
};

export default function Game({ ctx, onExit }) {
  const { childToken, child, reward } = ctx;
  const [challenges, setChallenges] = useState([]);
  const [session, setSession] = useState(null);
  const [skills, setSkills] = useState({ patience: 0, saving_awareness: 0, impulse_control: 0 });
  const [defeated, setDefeated] = useState(new Set());
  const [selected, setSelected] = useState(null);
  const [shownAt, setShownAt] = useState(0);
  const [ai, setAi] = useState(null);
  const [vault, setVault] = useState({
    amount: reward ? Number(reward.amount) : null,
    unlocked_amount: reward ? Number(reward.unlocked_amount || 0) : 0,
    progress_pct: reward ? reward.progress_pct : 0,
    status: reward ? reward.status : "locked",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const levels = await api.levels(childToken);
        const all = (levels[0]?.challenges || []).slice().sort((a, b) => a.order_index - b.order_index);
        setChallenges(all);
        const s = await api.startSession(childToken);
        setSession(s);
        setSkills(s.skills);
        setAi({ encouragement: s.encouragement, suggested_monster: s.suggested_monster, difficulty: s.difficulty });
      } catch (err) { setError(err.message); } finally { setLoading(false); }
    })();
  }, []);

  const xp = Math.round((skills.patience || 0) + (skills.saving_awareness || 0) + (skills.impulse_control || 0));
  const completed = vault.status === "completed" || (challenges.length > 0 && defeated.size >= challenges.length);

  function openChallenge(ch) {
    if (defeated.has(ch.id)) return;
    setSelected(ch);
    setShownAt(Date.now());
  }

  async function choose(choice) {
    const reaction = Math.max(0, Date.now() - shownAt);
    try {
      const res = await api.submitDecision(childToken, session.session_id, selected.id, choice.key, reaction);
      setSkills(res.skills);
      setAi({ encouragement: res.encouragement, suggested_monster: res.next_suggested_monster, difficulty: res.difficulty, prediction: res.success_prediction });
      if (res.reward_progress) {
        setVault((v) => ({
          amount: res.reward_progress.amount != null ? Number(res.reward_progress.amount) : v.amount,
          unlocked_amount: Number(res.reward_progress.unlocked_amount),
          progress_pct: res.reward_progress.progress_pct,
          status: res.reward_progress.status,
        }));
      }
      if (res.defeated) setDefeated((prev) => new Set(prev).add(selected.id));
      setSelected(null);
    } catch (err) { setError(err.message); }
  }

  return (
    <>
      <div className="navbar">
        <div className="brand">
          <div className="brand-badge">🗺️</div>
          <div><h1>رحلة {child.nickname}</h1><p>غامر، حارب المغريات، وافتح كنزك</p></div>
        </div>
        <button className="btn-ghost" onClick={onExit}>رجوع للوحة الأب</button>
      </div>

      <div className="topbar">
        <div className="cell"><div className="v">{child.nickname}</div><div className="k">اللاعب</div></div>
        <div className="cell"><div className="v" style={{ color: "var(--gold-2)" }}>{xp}</div><div className="k">نقاط XP</div></div>
        <div className="cell"><div className="v">١</div><div className="k">المرحلة الحالية</div></div>
        <div className="cell"><div className="v" style={{ color: "var(--primary-d)" }}>{vault.progress_pct}%</div><div className="k">تقدّم المكافأة</div></div>
      </div>

      {error && <ErrorBox>{error}</ErrorBox>}
      {ai?.encouragement && <div className="encourage">💬 {ai.encouragement}</div>}

      {loading ? (
        <div className="card"><Spinner label="تُجهّز الخريطة..." /></div>
      ) : (
        <div className="game-grid">
          <div>
            {completed ? (
              <div className="card celebrate">
                <div className="big">🎉🏆</div>
                <h2>أحسنت! فتحت الخزنة</h2>
                <p className="muted">هزمت كل الوحوش وتعلّمت مقاومة المغريات — مكافأتك أصبحت لك!</p>
              </div>
            ) : selected ? (
              <div className="card">
                <div className="section-title">
                  <span className="dot">{MONSTER_EMOJI[selected.monster_code] || "👾"}</span>
                  <h3>التحدي الحالي — {MONSTER_NAME[selected.monster_code] || "وحش"}</h3>
                  {selected.is_final && <span className="badge badge-active" style={{ marginInlineStart: "auto" }}>التحدي النهائي</span>}
                </div>
                <p className="scenario">{selected.scenario}</p>
                {selected.choices.map((c) => (
                  <button key={c.key} className="choice" onClick={() => choose(c)}>{c.label}</button>
                ))}
                <button className="btn-ghost btn-sm" onClick={() => setSelected(null)}>إلغاء</button>
              </div>
            ) : (
              <div className="card">
                <div className="section-title"><span className="dot">🗺️</span><h3>خريطة المغامرة</h3></div>
                <div className="monsters">
                  {challenges.map((ch) => (
                    <div key={ch.id} className={`monster ${defeated.has(ch.id) ? "done" : ""}`} onClick={() => openChallenge(ch)}>
                      <div className="emoji">{MONSTER_EMOJI[ch.monster_code] || "👾"}</div>
                      <h4>{ch.is_final ? "الوحش النهائي" : MONSTER_NAME[ch.monster_code] || "وحش"}</h4>
                      <span className={`badge ${defeated.has(ch.id) ? "badge-ready" : "badge-info"}`}>
                        {defeated.has(ch.id) ? "مهزوم ✅" : `${ch.points} نقطة`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div>
            {/* المكافأة الكبرى */}
            <div className="card">
              <div className="section-title"><span className="dot">🎁</span><h3>المكافأة الكبرى</h3></div>
              <div className="reward-card">
                <div className="row spread">
                  <div className="amount">
                    {vault.amount != null ? Math.round(vault.unlocked_amount) : vault.progress_pct}
                    <small>{vault.amount != null ? `/ ${Math.round(vault.amount)} Robux` : "%"}</small>
                  </div>
                  <StatusBadge status={vault.status} />
                </div>
                <div style={{ margin: "12px 0 6px" }}><div className="bar gold"><span style={{ width: `${vault.progress_pct}%` }} /></div></div>
                <div className="reward-note">تُفتح الخزنة تدريجياً مع كل وحش تهزمه.</div>
              </div>
            </div>

            {/* المدرّب الذكي */}
            {ai && (
              <div className="card">
                <div className="section-title"><span className="dot">🤖</span><h3>المدرّب الذكي</h3></div>
                <div className="coach">
                  <div className="kpi"><b>{ai.difficulty ?? "-"}</b><span>الصعوبة</span></div>
                  <div className="kpi"><b>{ai.suggested_monster ? (MONSTER_EMOJI[ai.suggested_monster] || "🎯") : "-"}</b><span>الوحش المقترح</span></div>
                  <div className="kpi"><b>{ai.prediction ? Math.round(ai.prediction.probability * 100) + "%" : "-"}</b><span>توقّع الإكمال</span></div>
                </div>
                {[["الصبر", skills.patience], ["الوعي بالادخار", skills.saving_awareness], ["ضبط الاندفاع", skills.impulse_control]].map(([l, v]) => (
                  <div key={l} style={{ marginBottom: 10 }}>
                    <div className="row spread" style={{ marginBottom: 4 }}><span className="muted" style={{ fontSize: 12.5 }}>{l}</span><span className="muted" style={{ fontSize: 12.5 }}>{Math.round(v)}</span></div>
                    <Bar value={v} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
