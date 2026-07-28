export interface ClothingItem {
  id: number;
  name: string;
  category: string;
  image_path: string;
  user_id: number;
}

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

export async function getItems(): Promise<ClothingItem[]> {
  const res = await api('');
  return res.json();
}

export async function createItem(_formData: FormData): Promise<never> {
  throw 'not implemented';
}

export async function deleteItem(_itemId: number): Promise<never> {
  throw 'not implemented';
}
