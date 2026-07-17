import { useState } from "react";
import { api } from "./api.js";
import { Bar, ErrorBox } from "./ui.jsx";

const METHODS = [
  { key: "card", icon: "💳", label: "بطاقة بنكية" },
  { key: "wallet", icon: "📱", label: "محفظة رقمية" },
  { key: "open_banking", icon: "🏦", label: "الربط المصرفي المفتوح" },
];

export function PaymentSummaryCard({ total }) {
  return (
    <div className="pay-total">
      <div className="n">{Number(total || 0).toLocaleString("ar-EG")}</div>
      <div className="l">المبلغ الإجمالي (ريال)</div>
    </div>
  );
}

export function PaymentMethodSelector({ value, onChange }) {
  return (
    <>
      <label>طريقة الدفع</label>
      <div className="method-grid">
        {METHODS.map((m) => (
          <div key={m.key} className={`method ${value === m.key ? "on" : ""}`} onClick={() => onChange(m.key)}>
            <div className="mi">{m.icon}</div>
            <div className="ml">{m.label}</div>
          </div>
        ))}
      </div>
      <div className="hint">🔒 دفع تجريبي — لا يتم سحب مبلغ حقيقي ولا إدخال بيانات بطاقة.</div>
    </>
  );
}

export function SavingAllocationCard({ total, pct, onPct }) {
  const saving = Math.round((total * pct) / 100);
  const reward = total - saving;
  return (
    <div className="card tight" style={{ background: "var(--surface-2)" }}>
      <div className="row spread">
        <span style={{ fontWeight: 700 }}>نسبة الادخار</span>
        <span style={{ fontWeight: 800, color: "var(--gold-2)" }}>{pct}%</span>
      </div>
      <input type="range" min="0" max="90" step="5" value={pct} onChange={(e) => onPct(Number(e.target.value))} />
      <div className="split-grid">
        <div className="split-box save"><div className="n">{saving}</div><div className="l">للادخار (ريال)</div></div>
        <div className="split-box reward"><div className="n">{reward}</div><div className="l">للمكافأة (Robux)</div></div>
      </div>
    </div>
  );
}

export function GoalProgressCard({ saving, total }) {
  const pct = total > 0 ? Math.round((saving / total) * 100) : 0;
  return (
    <div className="card tight">
      <div className="section-title"><span className="dot">🎯</span><h3>هدف الادخار</h3></div>
      <div className="row spread" style={{ marginBottom: 6 }}>
        <span style={{ fontWeight: 800 }}>{saving} / {total} ريال</span>
        <span className="muted">{pct}% مخصّص</span>
      </div>
      <Bar value={pct} gold />
    </div>
  );
}

export function TransactionConfirmation({ reward, saving, onDone }) {
  return (
    <div className="card celebrate">
      <div className="big">✅</div>
      <h2>تمت العملية بنجاح</h2>
      <div style={{ maxWidth: 340, margin: "16px auto 0", textAlign: "right" }}>
        <div className="summary-line"><span className="k">المكافأة</span><span className="v">{reward} Robux</span></div>
        {saving > 0 && <div className="summary-line"><span className="k">مبلغ الادخار</span><span className="v">{saving} ريال</span></div>}
        <div className="summary-line"><span className="k">حالة الهدف</span><span className="v" style={{ color: "var(--accent)" }}>قيد التنفيذ</span></div>
      </div>
      <button className="btn" style={{ marginTop: 20 }} onClick={onDone}>تم</button>
    </div>
  );
}

export default function AddRewardFlow({ token, children, onDone }) {
  const [childId, setChildId] = useState(children[0]?.id || "");
  const [total, setTotal] = useState(500);
  const [method, setMethod] = useState("card");
  const [savingOn, setSavingOn] = useState(false);
  const [pct, setPct] = useState(20);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const saving = savingOn ? Math.round((total * pct) / 100) : 0;
  const reward = total - saving;

  async function confirm() {
    setError("");
    if (!childId) { setError("اختر البطل أولاً"); return; }
    if (reward <= 0) { setError("يجب أن يبقى جزء للمكافأة"); return; }
    setBusy(true);
    try {
      await api.createReward(token, childId, String(reward));
      if (saving > 0) {
        const name = children.find((c) => c.id === childId)?.nickname || "";
        await api.createGoal(token, { title: `ادخار — ${name}`, target_amount: String(saving), child_id: childId });
      }
      setResult({ reward, saving });
      onDone && onDone();
    } catch (e) { setError(e.message); } finally { setBusy(false); }
  }

  if (children.length === 0) {
    return (
      <div className="card">
        <div className="section-title"><span className="dot">➕</span><h2>إضافة مكافأة جديدة</h2></div>
        <p className="muted">أضف بطلاً أولاً لتتمكن من شراء مكافأة.</p>
      </div>
    );
  }

  if (result) {
    return (
      <div className="card">
        <div className="section-title"><span className="dot">➕</span><h2>إضافة مكافأة جديدة</h2></div>
        <TransactionConfirmation reward={result.reward} saving={result.saving} onDone={() => setResult(null)} />
      </div>
    );
  }

  return (
    <div className="card">
      <div className="section-title"><span className="dot">➕</span><h2>إضافة مكافأة جديدة</h2></div>

      <div className="grid-2" style={{ alignItems: "start" }}>
        <div>
          <PaymentSummaryCard total={total} />
          <div className="row" style={{ marginTop: 14, alignItems: "flex-end" }}>
            <div className="field" style={{ maxWidth: 150 }}>
              <label>المبلغ (ريال)</label>
              <input value={total} onChange={(e) => setTotal(Math.max(0, Number(e.target.value) || 0))} inputMode="numeric" />
            </div>
            <div className="field">
              <label>البطل</label>
              <select value={childId} onChange={(e) => setChildId(e.target.value)}>
                {children.map((c) => <option key={c.id} value={c.id}>{c.nickname}</option>)}
              </select>
            </div>
          </div>
          <PaymentMethodSelector value={method} onChange={setMethod} />
        </div>

        <div>
          <div className="row spread">
            <span style={{ fontWeight: 700 }}>هل ترغب بتخصيص جزء للادخار؟</span>
            <div className="toggle-group">
              <button className={savingOn ? "on" : ""} onClick={() => setSavingOn(true)}>نعم</button>
              <button className={!savingOn ? "on" : ""} onClick={() => setSavingOn(false)}>لا</button>
            </div>
          </div>

          {savingOn ? (
            <div style={{ marginTop: 12 }}>
              <SavingAllocationCard total={total} pct={pct} onPct={setPct} />
              <GoalProgressCard saving={saving} total={total} />
            </div>
          ) : (
            <div className="card tight" style={{ marginTop: 12, background: "var(--surface-2)" }}>
              <div className="summary-line"><span className="k">للمكافأة</span><span className="v" style={{ color: "var(--primary-d)" }}>{reward} Robux</span></div>
              <p className="hint" style={{ marginTop: 8 }}>كامل المبلغ سيذهب لمكافأة الطفل. يمكنك تخصيص جزء للادخار.</p>
            </div>
          )}

          <div className="card tight" style={{ marginTop: 12 }}>
            <div className="summary-line"><span className="k">إجمالي الدفع</span><span className="v">{total} ريال</span></div>
            {saving > 0 && <div className="summary-line"><span className="k">للادخار</span><span className="v" style={{ color: "var(--gold-2)" }}>{saving} ريال</span></div>}
            <div className="summary-line"><span className="k">للمكافأة</span><span className="v" style={{ color: "var(--primary-d)" }}>{reward} Robux</span></div>
          </div>

          <ErrorBox>{error}</ErrorBox>
          <button className="btn btn-block" style={{ marginTop: 12 }} onClick={confirm} disabled={busy}>
            {busy ? "..." : `ادفع ${total} ريال وأنشئ المكافأة`}
          </button>
        </div>
      </div>
    </div>
  );
}
