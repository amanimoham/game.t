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
