import { useEffect, useState } from "react";
import { api } from "./api.js";
import { ErrorBox } from "./ui.jsx";
import ParentDashboard from "./ParentDashboard.jsx";
import Game from "./Game.jsx";

export default function App() {
  const [parentToken, setParentToken] = useState(() => localStorage.getItem("parentToken"));
  const [view, setView] = useState("auth"); // auth | parent | game
  const [gameCtx, setGameCtx] = useState(null);

  useEffect(() => {
    if (parentToken && view === "auth") setView("parent");
  }, [parentToken]);

  function onParentAuthed(token) {
    localStorage.setItem("parentToken", token);
    setParentToken(token);
    setView("parent");
  }

  function logout() {
    localStorage.removeItem("parentToken");
    setParentToken(null);
    setGameCtx(null);
    setView("auth");
  }

  if (view === "auth") return <Auth onAuthed={onParentAuthed} />;

  return (
    <div className="app-shell">
      {view === "parent" && (
        <ParentDashboard
          token={parentToken}
          onPlay={(ctx) => {
            setGameCtx(ctx);
            setView("game");
          }}
          onLogout={logout}
        />
      )}
      {view === "game" && gameCtx && <Game ctx={gameCtx} onExit={() => setView("parent")} />}
    </div>
  );
}

function Auth({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const fn = mode === "login" ? api.login : api.register;
      const res = await fn(email, password);
      onAuthed(res.access_token);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <div className="auth-wrap">
        <div className="auth-hero">
          <div className="logo">🛡️</div>
          <h2>بوابة ولي الأمر</h2>
          <p>تابع رحلة طفلك نحو قرارات مالية أذكى</p>
          <div className="points">
            <div>💰 مكافأة محفوظة تُفتح مع التعلّم</div>
            <div>🧠 مهارات: الصبر، ضبط الاندفاع، الادخار</div>
            <div>📊 لوحة متابعة واضحة لتقدّم طفلك</div>
          </div>
        </div>

        <div className="auth-form">
          <div className="auth-tabs">
            <button className={mode === "login" ? "on" : ""} onClick={() => setMode("login")}>
              تسجيل الدخول
            </button>
            <button className={mode === "register" ? "on" : ""} onClick={() => setMode("register")}>
              حساب جديد
            </button>
          </div>

          <form onSubmit={submit}>
            <div className="field">
              <label>البريد الإلكتروني</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@example.com" required />
            </div>
            <div className="field">
              <label>كلمة المرور</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} placeholder="٨ أحرف على الأقل" required />
            </div>
            <ErrorBox>{error}</ErrorBox>
            <button type="submit" className="btn btn-block" disabled={busy}>
              {busy ? "..." : mode === "login" ? "دخول لوحة المتابعة" : "إنشاء حساب"}
            </button>
          </form>
          <p className="hint" style={{ textAlign: "center", marginTop: 16 }}>
            تجربة تعليمية آمنة — بيانات طفلك محمية ولا تُشارك.
          </p>
        </div>
      </div>
    </div>
  );
}
