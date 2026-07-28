interface User {
  id: number;
  email: string;
}

const BASE = '/api/auth';

async function handleResponse<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    const data = await resp.json().catch(() => ({}));
    throw new Error(data.detail || `Request failed: ${resp.status}`);
  }
  return resp.json();
}

export async function register(email: string, password: string): Promise<User> {
  const resp = await fetch(`${BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include',
  });
  return handleResponse<User>(resp);
}

export async function login(email: string, password: string): Promise<User> {
  const resp = await fetch(`${BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include',
  });
  return handleResponse<User>(resp);
}

export async function logout(): Promise<{ message: string }> {
  const resp = await fetch(`${BASE}/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  return handleResponse<{ message: string }>(resp);
}

export async function getMe(): Promise<User | null> {
  const resp = await fetch(`${BASE}/me`, {
    credentials: 'include',
  });
  if (resp.status === 401) {
    return null;
  }
  return handleResponse<User>(resp);
}

export async function deleteAccount(): Promise<{ message: string }> {
  const resp = await fetch(`${BASE}/account`, {
    method: 'DELETE',
    credentials: 'include',
  });
  return handleResponse<{ message: string }>(resp);
}


