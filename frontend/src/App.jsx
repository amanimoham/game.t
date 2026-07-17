import { useEffect, useState } from "react";
import { api } from "./api.js";
import ParentDashboard from "./ParentDashboard.jsx";
import Game from "./Game.jsx";

export default function App() {
  const [parentToken, setParentToken] = useState(() => localStorage.getItem("parentToken"));
  const [view, setView] = useState("auth"); // auth | parent | game
  const [gameCtx, setGameCtx] = useState(null); // { childToken, child, reward }

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

  return (
    <div className="app">
      <div className="brand">
        <h1>🛡️ محاربة المغريات</h1>
        <p>لعبة تعليمية ترفع وعي الأطفال بالادخار</p>
      </div>

      {view === "auth" && <Auth onAuthed={onParentAuthed} />}

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

      {view === "game" && gameCtx && (
        <Game ctx={gameCtx} onExit={() => setView("parent")} />
      )}
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
    <div className="card" style={{ maxWidth: 420, margin: "0 auto" }}>
      <div className="row spread" style={{ marginBottom: 16 }}>
        <button className={mode === "login" ? "" : "ghost"} onClick={() => setMode("login")}>
          دخول الأب
        </button>
        <button className={mode === "register" ? "" : "ghost"} onClick={() => setMode("register")}>
          حساب جديد
        </button>
      </div>
      <form onSubmit={submit}>
        <div className="field">
          <label>البريد الإلكتروني</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className="field">
          <label>كلمة المرور (٨ أحرف على الأقل)</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={busy} style={{ width: "100%" }}>
          {busy ? "..." : mode === "login" ? "تسجيل الدخول" : "إنشاء الحساب"}
        </button>
      </form>
    </div>
  );
}
