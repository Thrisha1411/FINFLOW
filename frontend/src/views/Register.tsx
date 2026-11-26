import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("Finance Manager");
  const [email, setEmail] = useState("finance@finflow.in");
  const [org, setOrg] = useState("Bharat Retail Pvt Ltd");
  const [password, setPassword] = useState("ChangeMe12345!");
  function submit(event: FormEvent) {
    event.preventDefault();
    localStorage.setItem("finflow_token", "demo-token");
    localStorage.setItem("finflow_user", email);
    localStorage.setItem("finflow_org", org);
    localStorage.setItem("finflow_name", name);
    navigate("/dashboard");
  }

  return (
    <div className="grid min-h-screen place-items-center bg-ink px-4 text-slate-100">
      <form onSubmit={submit} className="w-full max-w-md rounded-md border border-white/10 bg-panel p-6 shadow-glow">
        <h1 className="text-2xl font-semibold">Create workspace</h1>
        <p className="mt-2 text-sm text-slate-400">Set up a demo workspace with INR reports and India-ready workflows.</p>
        <div className="mt-6 space-y-3">
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Full name" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
          <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Work email" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
          <input value={org} onChange={(event) => setOrg(event.target.value)} placeholder="Organization" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
          <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" type="password" className="w-full rounded-md border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-mint" />
        </div>
        <button className="mt-5 w-full rounded-md bg-mint px-4 py-2 font-semibold text-ink">Register</button>
        <Link to="/login" className="mt-4 block text-center text-sm text-cyan">Back to sign in</Link>
      </form>
    </div>
  );
}
