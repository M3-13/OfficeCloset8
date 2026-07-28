import { useState, useEffect, useCallback } from 'react';
import type { ClothingItem } from '../api/clothing';
import { getItems, deleteItem } from '../api/clothing';
import CategoryFilter from '../components/CategoryFilter';
import ClothingCard from '../components/ClothingCard';
import AddClothingForm from '../components/AddClothingForm';

const CATEGORIES = ['Oberteil', 'Hose', 'Schuhe', 'Accessoire', 'Kleid', 'Jacke'];

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadItems = useCallback(async () => {
    setError(null);
    try {
      const data = await getItems(selectedCategory ?? undefined);
      setItems(data);
    } catch {
      setError('Fehler beim Laden der Garderobe');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    setLoading(true);
    loadItems();
  }, [loadItems]);

  const handleCategoryChange = (category: string | null) => {
    setSelectedCategory(category);
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteItem(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch {
      setError('Fehler beim Löschen');
    }
  };

  const handleCreated = () => {
    setShowAddForm(false);
    setLoading(true);
    loadItems();
  };

  return (
    <div className="wardrobe-page">
      <div className="wardrobe-header">
        <h1>Meine Garderobe</h1>
        {!showAddForm && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => setShowAddForm(true)}
          >
            + Neues Kleidungsstück
          </button>
        )}
      </div>

      {showAddForm && (
        <AddClothingForm onCreated={handleCreated} onCancel={() => setShowAddForm(false)} />
      )}

      <CategoryFilter
        categories={CATEGORIES}
        selected={selectedCategory}
        onChange={handleCategoryChange}
      />

      {error && <p className="form-error">{error}</p>}
      {loading && <p className="loading-text">Lade Garderobe...</p>}

      {!loading && items.length === 0 && (
        <div className="empty-state">
          <p className="empty-text">
            {selectedCategory
              ? `Keine Kleidungsstücke in der Kategorie "${selectedCategory}" gefunden.`
              : 'Noch keine Kleidungsstücke. Lege dein erstes an!'}
          </p>
        </div>
      )}

      <div className="gallery-grid">
        {items.map((item) => (
          <ClothingCard key={item.id} item={item} onDelete={handleDelete} />
        ))}
      </div>
    </div>
  );
}
