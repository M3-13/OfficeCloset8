export interface ClothingItem {
  id: number;
  name: string;
  category: string;
  image_path: string;
  user_id: number;
}

export interface Outfit {
  id: number;
  name: string;
  user_id: number;
  items: ClothingItem[];
}

export interface OutfitCreateData {
  name: string;
  item_ids: number[];
}

async function api(path: string, options?: RequestInit): Promise<Response> {
  const res = await fetch(`/api/outfits${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Fehler ${res.status}`);
  }
  return res;
}

export async function getOutfits(): Promise<Outfit[]> {
  const res = await api('');
  return res.json();
}

export async function getOutfit(id: number): Promise<Outfit> {
  const res = await api(`/${id}`);
  return res.json();
}

export async function createOutfit(data: OutfitCreateData): Promise<Outfit> {
  const res = await api('', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function updateOutfit(id: number, data: OutfitCreateData): Promise<Outfit> {
  const res = await api(`/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteOutfit(id: number): Promise<void> {
  await api(`/${id}`, { method: 'DELETE' });
}
