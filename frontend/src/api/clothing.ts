import type { ClothingItem } from './types';

async function api(path: string, options?: RequestInit): Promise<Response> {
  const res = await fetch(`/api/clothing${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Fehler ${res.status}`);
  }
  return res;
}

export type { ClothingItem };

export async function getItems(): Promise<ClothingItem[]> {
  const res = await api('');
  return res.json();
}

export async function createItem(formData: FormData): Promise<ClothingItem> {
  const res = await api('', {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function deleteItem(itemId: number): Promise<void> {
  await api(`/${itemId}`, { method: 'DELETE' });
}
