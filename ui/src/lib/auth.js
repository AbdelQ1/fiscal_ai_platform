import keycloak from "../auth/keycloak";

/** Retourne un token valide (rafraîchit si nécessaire). */
export async function getAccessToken() {
  // isTokenExpired(true) = expire dans < 30s
  if (keycloak.isTokenExpired(30)) {
    try {
      await keycloak.updateToken(60);
    } catch {
      await keycloak.login({ redirectUri: window.location.origin });
      return null;
    }
  }
  return keycloak.token;
}
