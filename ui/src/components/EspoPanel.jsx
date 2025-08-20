import { useEffect, useState } from "react";
import { getDossiers } from "../lib/api";

export default function EspoPanel() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await getDossiers();
        setRows(data.dossiers || []);
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, []);

  return (
    <section className="bg-white shadow rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-3">📚 Dossiers EspoCRM</h3>
      {err && <div className="text-red-600 text-sm mb-2">{err}</div>}
      <ul className="list-disc pl-6">
        {rows.map((d) => (
          <li key={d.id}>{d.titre}</li>
        ))}
        {rows.length === 0 && !err && (
          <li className="text-gray-500 italic">Aucun dossier</li>
        )}
      </ul>
    </section>
  );
}
