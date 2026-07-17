// Thin API client for the FastAPI backend. Tokens are passed per-call.
const BASE = "/api/v1";

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = (data && data.detail) || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

export const api = {
  // auth
  register: (email, password) =>
    request("/auth/register", { method: "POST", body: { email, password } }),
  login: (email, password) =>
    request("/auth/login", { method: "POST", body: { email, password } }),
  childLogin: (token, child_id, pin) =>
    request("/auth/child-login", { method: "POST", token, body: { child_id, pin } }),
  me: (token) => request("/auth/me", { token }),

  // children (parent)
  createChild: (token, nickname, age_group) =>
    request("/children", { method: "POST", token, body: { nickname, age_group } }),
  listChildren: (token) => request("/children", { token }),
  setPin: (token, child_id, pin) =>
    request(`/children/${child_id}/pin`, { method: "PUT", token, body: { pin } }),

  // rewards (parent)
  createReward: (token, child_id, amount) =>
    request("/rewards", {
      method: "POST",
      token,
      body: { child_id, amount, reward_type: "robux" },
    }),
  getReward: (token, reward_id) => request(`/rewards/${reward_id}`, { token }),

  // game (child)
  levels: (token) => request("/game/levels", { token }),
  startSession: (token) => request("/game/sessions", { method: "POST", token }),
  submitDecision: (token, session_id, challenge_id, choice_key, reaction_time_ms) =>
    request(`/game/sessions/${session_id}/decisions`, {
      method: "POST",
      token,
      body: { challenge_id, choice_key, reaction_time_ms },
    }),
  progress: (token) => request("/game/progress", { token }),

  // dashboard (parent)
  insights: (token, child_id) => request(`/dashboard/children/${child_id}`, { token }),
  timeline: (token, child_id) => request(`/dashboard/children/${child_id}/timeline`, { token }),

  // open banking (parent, simulated)
  bankStatus: (token) => request("/banking/status", { token }),
  bankConnect: (token, bank_name) =>
    request("/banking/connect", { method: "POST", token, body: { bank_name } }),
  bankDisconnect: (token) => request("/banking/disconnect", { method: "POST", token }),
  bankInsights: (token) => request("/banking/insights", { token }),
  listGoals: (token) => request("/banking/goals", { token }),
  createGoal: (token, payload) =>
    request("/banking/goals", { method: "POST", token, body: payload }),
};
