import { useState, useEffect, useCallback } from 'react';
import type { ClothingItem } from '../api/clothing';
import * as clothingApi from '../api/clothing';
import CategoryFilter, { CATEGORIES } from '../components/CategoryFilter';
import ClothingCard from '../components/ClothingCard';
import AddClothingForm from '../components/AddClothingForm';

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await clothingApi.getItems(selectedCategory || undefined);
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Laden');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  async function handleCreated(item: ClothingItem) {
    setItems((prev) => [item, ...prev]);
    setShowAddForm(false);
  }

  async function handleDelete(itemId: number) {
    try {
      await clothingApi.deleteItem(itemId);
      setItems((prev) => prev.filter((it) => it.id !== itemId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Löschen');
    }
  }

  return (
    <div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 'var(--space-3)',
          marginBottom: 'var(--space-4)',
        }}
      >
        <h1>Meine Garderobe</h1>
        {!showAddForm && (
          <button className="btn btn-primary" onClick={() => setShowAddForm(true)}>
            Neues Kleidungsstück
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {showAddForm && (
        <AddClothingForm
          onCreated={handleCreated}
          onCancel={() => setShowAddForm(false)}
        />
      )}

      <CategoryFilter
        categories={CATEGORIES}
        selected={selectedCategory}
        onChange={setSelectedCategory}
      />

      {loading && <div className="loading-state">Lade Garderobe...</div>}

      {!loading && items.length === 0 && !error && (
        <div className="empty-state">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 6L14 24M32 6L34 24M14 24L18 42H30L34 24M14 24H34M16 6H32M16 6C14 4 10 4 8 8M32 6C34 4 38 4 40 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <p>Noch keine Kleidungsstücke vorhanden</p>
          <p style={{ fontSize: '0.875rem' }}>Füge dein erstes Kleidungsstück hinzu</p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
            gap: 'var(--space-4)',
          }}
        >
          {items.map((item) => (
            <ClothingCard key={item.id} item={item} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}
