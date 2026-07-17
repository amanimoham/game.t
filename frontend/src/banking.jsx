import { useEffect, useState } from "react";
import { api } from "./api.js";
import { Bar, ErrorBox, Spinner } from "./ui.jsx";

// ---------- Open Banking status pill ----------
export function OpenBankingStatus({ status }) {
  const connected = status?.connected;
  return (
    <div className="row spread" style={{ marginBottom: 4 }}>
      <span className={`badge ${connected ? "badge-ready" : "badge-muted"}`}>
        ● {connected ? "مُتصل" : "غير مُتصل"}
      </span>
      {connected && status.last_synced_at && (
        <span className="muted" style={{ fontSize: 12.5 }}>
          آخر تحديث: {new Date(status.last_synced_at).toLocaleString("ar")}
        </span>
      )}
    </div>
  );
}

// ---------- Connect card ----------
export function BankConnectionCard({ status, onConnect, onDisconnect, busy }) {
  const banks = status?.supported_banks || [];
  const [bank, setBank] = useState(banks[0] || "");
  useEffect(() => {
    if (!bank && banks.length) setBank(banks[0]);
  }, [banks]);

  if (status?.connected) {
    return (
      <div className="card tight">
        <OpenBankingStatus status={status} />
        <div className="row spread" style={{ marginTop: 8 }}>
          <div>
            <div style={{ fontWeight: 800 }}>{status.bank_name}</div>
            <div className="muted" style={{ fontSize: 12.5 }}>رابط تجريبي آمن (بيانات محاكاة)</div>
          </div>
          <button className="btn-ghost btn-sm" onClick={onDisconnect} disabled={busy}>
            إلغاء الربط
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card tight">
      <p style={{ marginTop: 0, fontWeight: 700 }}>اربط حسابك البنكي لمتابعة أهداف الادخار</p>
      <p className="muted" style={{ fontSize: 13, marginTop: -6 }}>
        ربط آمن بموافقتك — لا نطلب كلمة مرور البنك ولا نخزّن أي بيانات حساسة.
      </p>
      <div className="row" style={{ alignItems: "flex-end" }}>
        <div className="field">
          <label>اختر المصرف</label>
          <select value={bank} onChange={(e) => setBank(e.target.value)}>
            {banks.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
        <button className="btn" onClick={() => onConnect(bank)} disabled={busy || !bank}>
          {busy ? "..." : "منح الإذن والربط"}
        </button>
      </div>
      <div className="hint">🔒 تجريبي — يُنشئ اتصالاً بمحاكاة بيانات، دون بنك حقيقي.</div>
    </div>
  );
}

// ---------- Transaction insights ----------
export function TransactionInsights({ insights }) {
  if (!insights) return null;
  return (
    <div className="card">
      <div className="section-title"><span className="dot">📊</span><h3>تحليل المصروفات (تقديري)</h3></div>
      {insights.categories.map((c) => (
        <div key={c.key} style={{ marginBottom: 12 }}>
          <div className="row spread" style={{ marginBottom: 4 }}>
            <span style={{ fontSize: 13.5, fontWeight: 600 }}>{c.label}</span>
            <span className="muted" style={{ fontSize: 12.5 }}>{c.amount} • {c.pct}%</span>
          </div>
          <Bar value={c.pct} />
        </div>
      ))}
      <div className="hint">بيانات محاكاة لأغراض تعليمية — لا تُعرض تفاصيل بنكية حساسة.</div>
    </div>
  );
}

// ---------- AI educational recommendations ----------
export function FinancialEducationRecommendations({ recommendations }) {
  if (!recommendations?.length) return null;
  return (
    <div className="card">
      <div className="section-title"><span className="dot">🤖</span><h3>توصيات تعليمية ذكية</h3></div>
      {recommendations.map((r, i) => (
        <div key={i} className="encourage" style={{ marginBottom: 10 }}>💡 {r}</div>
      ))}
    </div>
  );
}

// ---------- Saving goal tracker ----------
export function SavingGoalTracker({ token, children, goals, onCreated }) {
  const [title, setTitle] = useState("مكافأة 500 Robux");
  const [amount, setAmount] = useState("500");
  const [childId, setChildId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function create() {
    setError(""); setBusy(true);
    try {
      const payload = { title, target_amount: amount };
      if (childId) payload.child_id = childId;
      await api.createGoal(token, payload);
      onCreated();
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  return (
    <div className="card">
      <div className="section-title"><span className="dot">🎯</span><h3>أهداف الادخار</h3></div>
      {goals.map((g) => (
        <div key={g.id} style={{ marginBottom: 14 }}>
          <div className="row spread" style={{ marginBottom: 4 }}>
            <span style={{ fontWeight: 700 }}>{g.title}</span>
            <span className="muted" style={{ fontSize: 12.5 }}>
              {Math.round(g.current_amount)} / {Math.round(g.target_amount)} {g.currency === "robux" ? "Robux" : g.currency}
            </span>
          </div>
          <Bar value={g.progress_pct} gold />
          <div className="row spread" style={{ marginTop: 4 }}>
            <span className="muted" style={{ fontSize: 12 }}>متبقٍّ: {Math.round(g.remaining_amount)}</span>
            {g.days_remaining != null && <span className="muted" style={{ fontSize: 12 }}>خلال {g.days_remaining} يوم</span>}
          </div>
        </div>
      ))}
      {goals.length === 0 && <p className="muted" style={{ fontSize: 13 }}>لا توجد أهداف بعد — أنشئ هدفاً لطفلك.</p>}

      <hr className="divider" />
      <div className="row" style={{ alignItems: "flex-end" }}>
        <div className="field"><label>عنوان الهدف</label><input value={title} onChange={(e) => setTitle(e.target.value)} /></div>
        <div className="field" style={{ maxWidth: 140 }}><label>المبلغ المستهدف</label><input value={amount} onChange={(e) => setAmount(e.target.value)} inputMode="numeric" /></div>
        <div className="field" style={{ maxWidth: 160 }}>
          <label>مرتبط بالبطل (اختياري)</label>
          <select value={childId} onChange={(e) => setChildId(e.target.value)}>
            <option value="">— بدون —</option>
            {children.map((c) => <option key={c.id} value={c.id}>{c.nickname}</option>)}
          </select>
        </div>
        <button className="btn-gold" onClick={create} disabled={busy}>{busy ? "..." : "إنشاء هدف"}</button>
      </div>
      <ErrorBox>{error}</ErrorBox>
    </div>
  );
}

// ---------- Privacy ----------
export function PrivacySection() {
  const items = [
    "البيانات تُستخدم فقط لتحسين التجربة التعليمية.",
    "لا يتم تخزين معلومات الحساب البنكي الحساسة.",
    "يمكن إلغاء الربط في أي وقت.",
  ];
  return (
    <div className="card">
      <div className="section-title"><span className="dot">🔐</span><h3>خصوصية البيانات</h3></div>
      {items.map((t, i) => (
        <div key={i} className="row" style={{ gap: 8, marginBottom: 8 }}>
          <span style={{ color: "var(--success)" }}>✓</span>
          <span style={{ fontSize: 14 }}>{t}</span>
        </div>
      ))}
    </div>
  );
}

// ---------- Composed section ----------
export default function SmartBankingSection({ token, childrenList }) {
  const [status, setStatus] = useState(null);
  const [insights, setInsights] = useState(null);
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      const st = await api.bankStatus(token);
      setStatus(st);
      const gs = await api.listGoals(token);
      setGoals(gs);
      if (st.connected) {
        setInsights(await api.bankInsights(token));
      } else {
        setInsights(null);
      }
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function connect(bank) {
    setBusy(true); setError("");
    try { await api.bankConnect(token, bank); await load(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function disconnect() {
    setBusy(true); setError("");
    try { await api.bankDisconnect(token); await load(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  return (
    <div className="card">
      <div className="section-title"><span className="dot">🏦</span><h2>الربط المالي الذكي</h2></div>
      <p className="muted" style={{ marginTop: -8, fontSize: 13 }}>
        ربط بنكي آمن (تجريبي) لفهم أهداف الادخار والسلوك المالي — يدعم مفهوم الخدمات المصرفية المفتوحة.
      </p>
      <ErrorBox>{error}</ErrorBox>
      {loading ? (
        <Spinner />
      ) : (
        <>
          <BankConnectionCard status={status} onConnect={connect} onDisconnect={disconnect} busy={busy} />
          <div style={{ height: 12 }} />
          <SavingGoalTracker token={token} children={childrenList} goals={goals} onCreated={load} />
          {status?.connected && (
            <>
              <TransactionInsights insights={insights} />
              <FinancialEducationRecommendations recommendations={insights?.recommendations} />
            </>
          )}
          <PrivacySection />
        </>
      )}
    </div>
  );
}
