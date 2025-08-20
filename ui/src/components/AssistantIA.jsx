import { useState } from "react";
import { askAI } from "../lib/api";

export default function AssistantIA() {
  const [q, setQ] = useState("");
  const [a, setA] = useState("");
  const [loading, setLoading] = useState(false);

  const onAsk = async () => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await askAI(q);
      setA(res.answer || "");
    } catch (e) {
      setA(`Erreur: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="rounded-xl shadow p-4 bg-white">
      <h2 className="text-xl font-semibold mb-3">🤖 Assistant IA Fiscal</h2>
      <textarea
        rows={3}
        className="w-full border rounded px-3 py-2"
        placeholder="Posez une question… (ex : Résume ce dossier, Corrige cette facture…)"
        value={q}
        onChange={(e)=>setQ(e.target.value)}
      />
      <div className="mt-3 flex justify-end">
        <button className="px-4 py-2 rounded bg-green-600 text-white disabled:opacity-50"
          onClick={onAsk} disabled={loading || !q.trim()}>
          {loading ? "Envoi…" : "Envoyer à l'IA"}
        </button>
      </div>
      {a && <div className="mt-3 border rounded p-3 bg-gray-50 whitespace-pre-wrap">{a}</div>}
    </section>
  );
}
