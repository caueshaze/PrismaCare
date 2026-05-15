// Desenvolvimento local:
//   Simulador iOS       → http://localhost:8000
//   Emulador Android    → http://10.0.2.2:8000
//   Dispositivo físico  → http://<IP_DA_MAQUINA>:8000
// Produção (APK):
//   const BASE = 'https://seudominio.com';
const BASE = 'https://prismacare-api.caueti.com';

let _token: string | null = null;

export function setToken(t: string | null) {
  _token = t;
}

export async function api<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (_token) headers['Authorization'] = `Bearer ${_token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Erro ${res.status}`);
  }
  return res.json();
}

export async function loginRequest(username: string, password: string) {
  const body = new URLSearchParams({ username, password, grant_type: 'password' });
  const res = await fetch(`${BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail ?? 'Login falhou');
  return res.json() as Promise<{ access_token: string }>;
}
