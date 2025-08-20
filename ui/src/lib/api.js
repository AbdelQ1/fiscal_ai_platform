// Client API centralisé utilisant la méthode A
// -> refresh "just-in-time" + ajout de l'Authorization uniquement dans ce fichier

import { updateToken, getToken } from "@/auth/keycloak";

const API_BASE =
  import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function apiFetch(path, init = {}) {
  // Rafraîchir si besoin (30s par défaut)
  await updateToken(30);

  const token = getToken();
  const headers = new Headers(init.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);

  headers.set("Accept", "application/json");

  const res = await fetch(API_BASE + path, {
    ...init,
    headers,
    // Si tu veux envoyer des cookies côté API (peu probable ici) :
    // credentials: "include",
  });

  // Gestion d'erreurs standardisée
  if (!res.ok) {
    // Essai simple : lever une erreur avec contexte
    const text = await res.text().catch(() => "");
    const err = new Error(
      `API ${path} -> ${res.status} ${res.statusText} ${text}`
    );
    err.status = res.status;
    throw err;
  }

  // Tente JSON, sinon renvoie du texte
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return res.json();
  return res.text();
}

// ---- Exemples d'endpoints utilisés par l'UI ----

export async function apiPing() {
  // GET /ui/ping — côté backend peut répondre {status:"ok"} ou "ok"
  try {
    const data = await apiFetch("/ui/ping");
    if (typeof data === "string") return data;
    return data?.status ?? "ok";
  } catch {
    return "failed";
  }
}

export async function listFiles() {
  // GET /files/list -> { files: [...] }
  const data = await apiFetch("/files/list");
  return Array.isArray(data?.files) ? data.files : [];
}

export async function listDossiers() {
  // GET /espocrm/dossiers -> { dossiers: [...] }
  const data = await apiFetch("/espocrm/dossiers");
  return Array.isArray(data?.dossiers) ? data.dossiers : [];
}
