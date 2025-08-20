import React, { useEffect, useMemo, useState } from "react";
import {
  initKeycloak,
  isAuthenticated,
  login,
  logout,
  getToken,
  getUsername,
} from "@/auth/keycloak";
import { apiPing, listDossiers, listFiles } from "@/lib/api";
import { Badge, Button, Card, Page } from "@/components/ui";

export default function App() {
  const [ready, setReady] = useState(false);
  const [auth, setAuth] = useState(false);
  const [ping, setPing] = useState("…");
  const [files, setFiles] = useState([]);
  const [dossiers, setDossiers] = useState([]);

  // Init Keycloak au montage
  useEffect(() => {
    (async () => {
      await initKeycloak();
      setAuth(isAuthenticated());
      setReady(true);
    })();
  }, []);

  // Ping backend
  useEffect(() => {
    (async () => {
      const p = await apiPing();
      setPing(p);
    })();
  }, []);

  const username = useMemo(() => getUsername(), [auth]);

  async function handleLogin() {
    await login();
  }
  async function handleLogout() {
    await logout();
  }

  async function handleCopyToken() {
    const t = getToken();
    if (!t) return;
    await navigator.clipboard.writeText(t);
    alert("Token copié dans le presse‑papiers.");
  }

  async function testFiles() {
    try {
      const data = await listFiles();
      setFiles(data);
    } catch (e) {
      console.error(e);
      setFiles([]);
    }
  }

  async function testDossiers() {
    try {
      const data = await listDossiers();
      setDossiers(data);
    } catch (e) {
      console.error(e);
      setDossiers([]);
    }
  }

  return (
    <Page>
      <header style={{ marginBottom: 18 }}>
        <h1 style={{ fontSize: 36, margin: 0, fontWeight: 800 }}>
          Plateforme Fiscale Locale
        </h1>
        <div style={{ marginTop: 8 }}>
          API /ui/ping :{" "}
          <Badge tone={ping === "ok" ? "ok" : "failed"}>{ping}</Badge>
        </div>
      </header>

      <div style={{ display: "grid", gap: 16 }}>
        {/* Bienvenue */}
        <Card
          title="Bienvenue"
          right={
            ready && (
              <>
                {auth ? (
                  <Button variant="secondary" onClick={handleLogout}>
                    Se déconnecter
                  </Button>
                ) : (
                  <Button onClick={handleLogin}>Se connecter</Button>
                )}
              </>
            )
          }
        >
          {!ready ? (
            <div>Chargement…</div>
          ) : auth ? (
            <>
              <div style={{ marginBottom: 10 }}>
                Connecté en tant que <b>{username ?? "utilisateur"}</b>.
              </div>
              <Button variant="secondary" onClick={handleCopyToken}>
                Copier mon token
              </Button>
            </>
          ) : (
            <div>Vous n’êtes pas authentifié.</div>
          )}
        </Card>

        {/* Fichiers */}
        <Card
          title="Fichiers"
          right={
            <Button variant="secondary" onClick={testFiles}>
              Tester /files/list
            </Button>
          }
        >
          {files.length === 0 ? (
            <div>Aucun fichier</div>
          ) : (
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {files.map((f, i) => (
                <li key={i}>
                  {f.name ?? f.title ?? "—"}{" "}
                  {typeof f.size === "number" && `— ${f.size} octets`}{" "}
                  {f.uploaded_at && `— ${f.uploaded_at}`}
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* EspoCRM */}
        <Card
          title="Dossiers EspoCRM"
          right={
            <Button variant="secondary" onClick={testDossiers}>
              Tester /espocrm/dossiers
            </Button>
          }
        >
          {dossiers.length === 0 ? (
            <div>Aucun dossier</div>
          ) : (
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {dossiers.map((d, i) => (
                <li key={i}>
                  <b>{d.id ?? "—"}</b> — {d.title ?? "—"}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </Page>
  );
}
