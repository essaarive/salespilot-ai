import { Bot } from "lucide-react";
import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api, setToken } from "../api/client";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await api.login(username, password);
      setToken(result.token);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-8 shadow-soft">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-md bg-brand-600 text-white">
            <Bot size={22} />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-950">SalesPilot AI</h1>
            <p className="text-sm text-slate-500">智销助手后台登录</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">用户名</span>
            <input className="field" value={username} onChange={(event) => setUsername(event.target.value)} />
          </label>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">密码</span>
            <input
              className="field"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
          <button className="btn-primary w-full" type="submit" disabled={loading}>
            {loading ? "登录中..." : "登录"}
          </button>
        </form>
      </div>
    </div>
  );
}
