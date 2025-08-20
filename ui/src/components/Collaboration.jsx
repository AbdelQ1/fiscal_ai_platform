import { useState } from "react";

export default function Collaboration() {
  const [msg, setMsg] = useState("");
  return (
    <section className="rounded-xl shadow p-4 bg-white">
      <h2 className="text-xl font-semibold mb-3">💬 Collaboration</h2>
      <div className="bg-gray-50 border rounded p-3 space-y-2 max-h-40 overflow-y-auto">
        <p><b>Fatima :</b> Le document TVA est incomplet.</p>
        <p><b>Jean :</b> J’ai relancé le client par mail.</p>
      </div>
      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2"
          placeholder="Écrire un message…"
          value={msg}
          onChange={(e)=>setMsg(e.target.value)}
        />
        <button className="px-4 py-2 rounded bg-blue-600 text-white">Envoyer</button>
      </div>
    </section>
  );
}
