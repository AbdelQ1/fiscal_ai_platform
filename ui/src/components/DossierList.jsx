import { useEffect, useState } from "react";
import { getDossiers } from "../lib/api";

export default function DossierList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  useEffect(() => {
    getDossiers().then(res => {
      setItems(res.items || []);
    }).catch(e => setErr(e.message)).finally(() => setLoading(false));
  }, []);

  return (
    <section className="rounded-xl shadow p-4 bg-white">
      <h2 className="text-xl font-semibold mb-3">📁 Dossiers Fiscaux</h2>
      {loading && <p className="text-sm text-gray-500">Chargement…</p>}
      {err && <p className="text-sm text-red-600">{err}</p>}
      <ul className="space-y-2">
        {items.map((d) => (
          <li key={d.id} className="border rounded px-3 py-2 flex items-center justify-between">
            <span>{d.title}</span>
            <span className={`text-xs px-2 py-1 rounded ${
              d.status === "complete" ? "bg-green-100 text-green-700"
              : d.status === "pending" ? "bg-yellow-100 text-yellow-700"
              : "bg-blue-100 text-blue-700"
            }`}>{d.status}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
