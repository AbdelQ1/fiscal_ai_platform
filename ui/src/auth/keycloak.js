// Méthode A (recommandée) :
// - initKeycloak() : initialise une seule fois (check-sso + PKCE)
// - updateToken(minSeconds) : rafraîchit juste avant chaque appel API
// - getToken() : lit le token en mémoire au moment du besoin
// - login(), logout(), isAuthenticated(), getUsername()

import Keycloak from "keycloak-js";

let kc = null;
let initPromise = null;

function getConfig() {
  // Possibilité de surcharger via Vite :
  // VITE_KEYCLOAK_URL, VITE_KEYCLOAK_REALM, VITE_KEYCLOAK_CLIENT_ID
  const url =
    import.meta.env.VITE_KEYCLOAK_URL ?? "http://localhost:8081";
  const realm =
    import.meta.env.VITE_KEYCLOAK_REALM ?? "fiscal-local";
  const clientId =
    import.meta.env.VITE_KEYCLOAK_CLIENT_ID ?? "fiscal-ui";
  return { url, realm, clientId };
}

export async function initKeycloak() {
  if (initPromise) return initPromise;

  const { url, realm, clientId } = getConfig();
  kc = new Keycloak({ url, realm, clientId });

  initPromise = kc
    .init({
      onLoad: "check-sso",
      pkceMethod: "S256",
      silentCheckSsoRedirectUri:
        window.location.origin + "/silent-check-sso.html",
      // Pour Vite: éviter le polling iframe (déconseillé en dev):
      checkLoginIframe: false,
    })
    .catch((err) => {
      console.error("[KC] init error:", err);
      // on continue ; la SPA pourra proposer le login manuel
      return false;
    });

  const ok = await initPromise;
  console.log("[KC] init =>", ok ? "authenticated?" : "no session");
  return ok;
}

export function isAuthenticated() {
  return Boolean(kc?.authenticated);
}

export function getUsername() {
  return kc?.tokenParsed?.preferred_username ?? null;
}

export function getToken() {
  return kc?.token ?? null;
}

export async function updateToken(minSeconds = 30) {
  if (!kc) await initKeycloak();
  // Si non authentifié, inutile d'essayer de refresh
  if (!kc?.authenticated) return null;
  try {
    const refreshed = await kc.updateToken(minSeconds);
    if (refreshed) {
      // optionnel : console.log("[KC] token refreshed");
    }
    return kc.token;
  } catch (e) {
    // Refresh impossible (refresh token expiré p.ex.) -> forcer un login
    await kc.login();
    return null; // on ne revient normalement pas ici (redirection)
  }
}

export async function login() {
  if (!kc) await initKeycloak();
  return kc.login();
}

export async function logout() {
  if (!kc) return;
  const { url } = getConfig();
  // redirige vers la page d’accueil après logout
  return kc.logout({ redirectUri: window.location.origin });
}
