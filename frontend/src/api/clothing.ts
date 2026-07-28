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

export async function getItems(category?: string): Promise<ClothingItem[]> {
  const query = category ? `?category=${encodeURIComponent(category)}` : '';
  const res = await api(query);
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
  await api(`/${itemId}`, {
    method: 'DELETE',
  });
}
