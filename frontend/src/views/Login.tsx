import { Landmark } from "lucide-react";
import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("finance@finflow.in");
  const [password, setPassword] = useState("ChangeMe12345!");
  const [message, setMessage] = useState("");
  function submit(event: FormEvent) {
    event.preventDefault();
    if (!email || !password) {
      setMessage("Enter your email and password.");
      return;
    }
    localStorage.setItem("finflow_token", "demo-token");
    localStorage.setItem("finflow_user", email);
    navigate("/dashboard");
  }

  return (
    <div className="grid min-h-screen place-items-center bg-ink px-4 text-slate-100">
      <form onSubmit={submit} className="w-full max-w-md rounded-md border border-white/10 bg-panel p-6 shadow-glow">
        <Landmark className="mb-5 h-9 w-9 text-mint" />
        <h1 className="text-2xl font-semibold">FinFlow AI</h1>
        <p className="mt-2 text-sm text-slate-400">Sign in to the India finance operations workspace.</p>
        <div className="mt-6 space-y-3">
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
          <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" type="password" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
          <input placeholder="2FA code" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
        </div>
        {message && <div className="mt-3 rounded-md border border-amber/30 bg-amber/10 px-3 py-2 text-sm text-amber">{message}</div>}
        <button className="mt-5 w-full rounded-md bg-mint px-4 py-2 font-semibold text-ink">Sign in</button>
        <Link to="/register" className="mt-4 block text-center text-sm text-cyan">Create an enterprise account</Link>
      </form>
    </div>
  );
}
