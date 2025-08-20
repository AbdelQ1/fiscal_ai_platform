import { useEffect, useState } from "react";
import { uploadFile, listUploads } from "../lib/api";

export default function DocumentCollect() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");
  const [items, setItems] = useState([]);

  const refresh = () => listUploads().then(r => setItems(r.items||[])).catch(()=>{});
  useEffect(() => { refresh(); }, []);

  const onUpload = async () => {
    if (!file) return;
    setMsg("Upload en cours…");
    try {
      const res = await uploadFile(file);
      setMsg(`OK : ${res.filename}`);
      setFile(null);
      refresh();
    } catch (e) {
      setMsg(`Erreur : ${e.message}`);
    }
  };

  return (
    <section className="rounded-xl shadow p-4 bg-white">
      <h2 className="text-xl font-semibold mb-3">📄 Collecte de Documents</h2>
      <div className="flex gap-2">
        <input type="file" className="w-full border rounded px-3 py-2"
               onChange={(e)=>setFile(e.target.files?.[0] || null)} />
        <button className="px-4 py-2 rounded bg-blue-600 text-white"
                onClick={onUpload} disabled={!file}>
          Uploader
        </button>
      </div>
      <p className="text-sm text-gray-500 mt-2">Formats : PDF, DOCX, PNG, JPG — max 50MB</p>
      {msg && <p className="text-sm mt-2">{msg}</p>}

      <h3 className="mt-4 font-medium">Fichiers importés</h3>
      <ul className="text-sm text-gray-700 list-disc pl-5">
        {items.map(f => (
          <li key={f}>
            <a className="text-blue-600 hover:underline" href={`${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/files/download/${encodeURIComponent(f)}`} target="_blank" rel="noreferrer">
              {f}
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
