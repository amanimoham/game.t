// Shared presentational components (no external libraries).

export function Spinner({ label = "جارٍ التحميل..." }) {
  return (
    <div className="loading">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}

export function ErrorBox({ children }) {
  if (!children) return null;
  return <div className="error-box">⚠️ {children}</div>;
}

export function Empty({ icon = "🗺️", children }) {
  return (
    <div className="empty">
      <div className="ic">{icon}</div>
      <div>{children}</div>
    </div>
  );
}

export function Bar({ value, gold = false }) {
  const v = Math.max(0, Math.min(100, value || 0));
  return (
    <div className={`bar ${gold ? "gold" : ""}`}>
      <span style={{ width: `${v}%` }} />
    </div>
  );
}

export function Metric({ value, label, tone }) {
  return (
    <div className="metric">
      <div className={`val ${tone || ""}`}>{value}</div>
      <div className="lbl">{label}</div>
    </div>
  );
}

const REWARD_STATUS = {
  locked: { label: "محفوظة", cls: "badge-saved" },
  in_progress: { label: "الرحلة جارية", cls: "badge-active" },
  completed: { label: "جاهزة للاستلام", cls: "badge-ready" },
  delivered: { label: "تم الاستلام", cls: "badge-ready" },
  cancelled: { label: "ملغاة", cls: "badge-muted" },
};

export function StatusBadge({ status }) {
  const s = REWARD_STATUS[status] || REWARD_STATUS.locked;
  return <span className={`badge ${s.cls}`}>● {s.label}</span>;
}

export function Header({ email, onLogout }) {
  const initial = ((email || "و").trim()[0] || "و").toUpperCase();
  return (
    <div className="app-header">
      <div className="row" style={{ gap: 12 }}>
        <div className="hd-avatar">{initial}</div>
        <div>
          <div className="hd-welcome">مرحباً بك 👋</div>
          <div className="hd-sub">{email || "ولي الأمر"}</div>
        </div>
      </div>
      <div className="row" style={{ gap: 10 }}>
        <span className="sec-badge">🔒 اتصال آمن</span>
        <div className="bell" title="الإشعارات">🔔<i className="bell-dot" /></div>
        <button className="btn-ghost-light" onClick={onLogout}>خروج</button>
      </div>
    </div>
  );
}

export function CircularProgress({ value, size = 132, stroke = 12, color = "var(--green-accent)", track = "rgba(255,255,255,0.14)", children }) {
  const v = Math.max(0, Math.min(100, value || 0));
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - v / 100);
  const half = size / 2;
  return (
    <div className="circular" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={half} cy={half} r={r} fill="none" stroke={track} strokeWidth={stroke} />
        <circle className="ring-fill" cx={half} cy={half} r={r} fill="none" stroke={color} strokeWidth={stroke}
          strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
          transform={`rotate(-90 ${half} ${half})`} />
      </svg>
      <div className="circular-center">{children}</div>
    </div>
  );
}

export function SavingBalanceCard({ current, target }) {
  const has = target > 0;
  const pct = has ? Math.round((100 * current) / target) : 0;
  return (
    <div className="balance-card">
      <div className="balance-info">
        <div className="bl-label">هدف الادخار</div>
        {has ? (
          <>
            <div className="bl-amount">{Math.round(target).toLocaleString("ar-EG")} <small>ريال</small></div>
            <div className="bl-sub">{Math.round(current).toLocaleString("ar-EG")} / {Math.round(target).toLocaleString("ar-EG")} ريال</div>
            <div className="bl-growth">📈 نمو ادخار أبطالك يتقدّم بثبات</div>
          </>
        ) : (
          <>
            <div className="bl-amount">—</div>
            <div className="bl-sub">أضف مكافأة لبدء رحلة الادخار.</div>
          </>
        )}
      </div>
      <CircularProgress value={pct}>
        <div className="ring-pct">{pct}%</div>
        <div className="ring-lbl">مكتمل</div>
      </CircularProgress>
    </div>
  );
}

export function SkillCard({ icon, name, value }) {
  const v = Math.round(value || 0);
  return (
    <div className="skill-card">
      <div className="head">
        <div className="ic">{icon}</div>
        <div className="name">{name}</div>
      </div>
      <Bar value={v} />
      <div className="pct">{v}%</div>
    </div>
  );
}
