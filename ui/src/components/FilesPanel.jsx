import { useEffect, useState } from "react";
import { listFiles, uploadFile } from "../lib/api";

export default function FilesPanel() {
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function refresh() {
    setErr("");
    try {
      const data = await listFiles();
      setFiles(data.files || []);
    } catch (e) {
      setErr(e.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onPick(e) {
    const f = e.target.files?.[0];
    if (!f) return;
    setBusy(true);
    setErr("");
    try {
      await uploadFile(f);
      await refresh();
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  return (
    <section className="bg-white shadow rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-3">📁 Fichiers</h3>

      <div className="mb-3 flex items-center gap-3">
        <input
          type="file"
          onChange={onPick}
          disabled={busy}
          className="block"
        />
        {busy && <span className="text-sm text-gray-500">Upload…</span>}
      </div>

      {err && <div className="text-red-600 text-sm mb-2">{err}</div>}

      <ul className="list-disc pl-6">
        {files.map((f) => (
          <li key={f.name}>
            {f.name} <span className="text-gray-500">({f.size} o)</span>
          </li>
        ))}
        {files.length === 0 && (
          <li className="text-gray-500 italic">Aucun fichier</li>
        )}
      </ul>
    </section>
  );
}
