export interface ClothingItem {
  id: number;
  name: string;
  category: string;
  image_path: string;
  image_url: string;
  user_id: number;
}

export async function getItems(category?: string): Promise<ClothingItem[]> {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  const query = params.toString();
  const resp = await fetch(`/api/clothing${query ? '?' + query : ''}`, {
    credentials: 'include',
  });
  if (!resp.ok) throw new Error('Fehler beim Laden der Kleidungsstücke');
  return resp.json();
}

export async function createItem(formData: FormData): Promise<ClothingItem> {
  const resp = await fetch('/api/clothing', {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Unbekannter Fehler' }));
    throw new Error(err.detail || 'Fehler beim Anlegen');
  }
  return resp.json();
}

export async function deleteItem(itemId: number): Promise<void> {
  const resp = await fetch(`/api/clothing/${itemId}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!resp.ok) throw new Error('Fehler beim Löschen');
}
