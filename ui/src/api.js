// src/api.js
import { getToken, updateToken } from './auth/keycloak.js';

const API_BASE = 'http://localhost:8080'; // <-- adapte selon ton backend

// Wrapper fetch avec Auth Keycloak
async function fetchWithAuth(endpoint, options = {}) {
  try {
    // 🔄 Met à jour le token si besoin (30 sec avant expiration)
    await updateToken(30);

    const token = getToken();
    if (!token) throw new Error('Token manquant — utilisateur non connecté.');

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Erreur API ${endpoint} : ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.error(`❌ fetchWithAuth(${endpoint})`, err);
    throw err;
  }
}

// --- Fonctions API ---
export async function ping() {
  return fetchWithAuth('/ui/ping');
}

export async function listFiles() {
  return fetchWithAuth('/files/list');
}

export async function listDossiers() {
  return fetchWithAuth('/espocrm/dossiers');
}

export default {
  ping,
  listFiles,
  listDossiers,
};
