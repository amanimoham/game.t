import { useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import { SkillBars } from "./ParentDashboard.jsx";

const MONSTER_EMOJI = {
  instant_reward: "🛒",
  social_pressure: "👥",
  limited_offer: "⏳",
  spending: "💸",
};

export default function Game({ ctx, onExit }) {
  const { childToken, child, reward } = ctx;
  const [challenges, setChallenges] = useState([]);
  const [session, setSession] = useState(null);
  const [skills, setSkills] = useState({ patience: 0, saving_awareness: 0, impulse_control: 0 });
  const [defeated, setDefeated] = useState(new Set());
  const [selected, setSelected] = useState(null);
  const [shownAt, setShownAt] = useState(0);
  const [result, setResult] = useState(null);
  const [ai, setAi] = useState(null);
  const [vault, setVault] = useState({
    amount: reward ? Number(reward.amount) : null,
    unlocked_amount: 0,
    progress_pct: 0,
    status: reward ? reward.status : "locked",
  });
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
      } catch (err) {
        setError(err.message);
      }
    })();
  }, []);

  function openChallenge(ch) {
    if (defeated.has(ch.id)) return;
    setSelected(ch);
    setResult(null);
    setShownAt(Date.now());
  }

  async function choose(choice) {
    const reaction = Math.max(0, Date.now() - shownAt);
    try {
      const res = await api.submitDecision(childToken, session.session_id, selected.id, choice.key, reaction);
      setSkills(res.skills);
      setResult(res);
      setAi({
        encouragement: res.encouragement,
        suggested_monster: res.next_suggested_monster,
        difficulty: res.difficulty,
        prediction: res.success_prediction,
      });
      if (res.reward_progress) {
        setVault((v) => ({
          amount: res.reward_progress.amount != null ? Number(res.reward_progress.amount) : v.amount,
          unlocked_amount: Number(res.reward_progress.unlocked_amount),
          progress_pct: res.reward_progress.progress_pct,
          status: res.reward_progress.status,
        }));
      }
      if (res.defeated) {
        setDefeated((prev) => new Set(prev).add(selected.id));
      }
      setSelected(null);
    } catch (err) {
      setError(err.message);
    }
  }

  const completed = vault.status === "completed";
  const allDone = challenges.length > 0 && defeated.size >= challenges.length;

  return (
    <>
      <div className="row spread">
        <h2>🗺️ رحلة {child.nickname}</h2>
        <button className="ghost" onClick={onExit}>
          رجوع للوحة الأب
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <Vault vault={vault} />

      {ai && (
        <div className="card">
          <div className="encourage">{ai.encouragement}</div>
          <div className="ai">
            <div className="kpi">
              <b>{ai.difficulty ?? "-"}</b>
              <span>الصعوبة (AI)</span>
            </div>
            <div className="kpi">
              <b>{ai.suggested_monster ? MONSTER_EMOJI[ai.suggested_monster] || "🎯" : "-"}</b>
              <span>الوحش المقترح (AI)</span>
            </div>
            <div className="kpi">
              <b>{ai.prediction ? Math.round(ai.prediction.probability * 100) + "%" : "-"}</b>
              <span>توقّع الإكمال (AI)</span>
            </div>
          </div>
          <SkillBars skills={skills} />
        </div>
      )}

      {completed || allDone ? (
        <div className="card celebrate">
          <div className="big">🎉🏆</div>
          <h2>أحسنت! فتحت الخزنة</h2>
          <p className="muted">
            هزمت كل الوحوش وتعلّمت مقاومة المغريات — مكافأتك أصبحت لك!
          </p>
        </div>
      ) : selected ? (
        <div className="card">
          <div className="row spread">
            <h3>
              {MONSTER_EMOJI[selected.monster_code] || "👾"} تحدٍّ
            </h3>
            {selected.is_final && <span className="tag">التحدي النهائي</span>}
          </div>
          <p className="scenario">{selected.scenario}</p>
          {selected.choices.map((c) => (
            <button key={c.key} className="choice" onClick={() => choose(c)}>
              {c.label}
            </button>
          ))}
          <button className="ghost" onClick={() => setSelected(null)}>
            إلغاء
          </button>
        </div>
      ) : (
        <div className="card">
          <h3>اختر وحشاً لتواجهه</h3>
          <div className="monsters">
            {challenges.map((ch) => (
              <div
                key={ch.id}
                className={`monster ${defeated.has(ch.id) ? "done" : ""}`}
                onClick={() => openChallenge(ch)}
              >
                <div className="emoji">{MONSTER_EMOJI[ch.monster_code] || "👾"}</div>
                <h4>{ch.is_final ? "الوحش النهائي" : "وحش"}</h4>
                <span className="tag">{defeated.has(ch.id) ? "مهزوم ✅" : `${ch.points} نقطة`}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

function Vault({ vault }) {
  const pct = vault.progress_pct || 0;
  return (
    <div className="card vault">
      <div className="muted">🔒 خزنة الكنز</div>
      <div className="amount">
        {vault.amount != null
          ? `${Math.round(vault.unlocked_amount)} / ${Math.round(vault.amount)} Robux`
          : `${pct}%`}
      </div>
      <div className="bar">
        <span style={{ width: `${pct}%` }} />
      </div>
      <div className="muted" style={{ marginTop: 8 }}>
        {vault.status === "completed" ? "مفتوحة بالكامل 🎉" : `مفتوح ${pct}%`}
      </div>
    </div>
  );
}
