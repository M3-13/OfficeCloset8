import { useState, useEffect, useRef } from 'react';
import { getItems, createItem, deleteItem, type ClothingItem } from '../api/clothing';
import ConfirmDialog from '../components/ConfirmDialog';

const VALID_CATEGORIES = [
  'Oberteile',
  'Hosen',
  'Kleider',
  'Röcke',
  'Schuhe',
  'Accessoires',
  'Jacken',
  'Mäntel',
  'Pullover',
];

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [newName, setNewName] = useState('');
  const [newCategory, setNewCategory] = useState(VALID_CATEGORIES[0]);
  const [newFile, setNewFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getItems();
        if (!cancelled) setItems(data);
      } catch (e) {
        if (!cancelled) setError((e as Error).message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const categories = [...new Set(items.map((i) => i.category))].sort();

  const filteredItems = activeCategory
    ? items.filter((i) => i.category === activeCategory)
    : items;

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFile || !newName.trim()) return;

    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('name', newName.trim());
      formData.append('category', newCategory);
      formData.append('image', newFile);

      const created = await createItem(formData);
      setItems((prev) => [created, ...prev]);
      setNewName('');
      setNewFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (deleteTarget === null) return;
    setDeleting(true);
    try {
      await deleteItem(deleteTarget);
      setItems((prev) => prev.filter((i) => i.id !== deleteTarget));
      setDeleteTarget(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setDeleting(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setNewFile(file);
  };

  if (loading) {
    return (
      <div className="loading-state">
        <p>Garderobe wird geladen...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Meine Garderobe</h1>

      {error && <p className="error-message">{error}</p>}

      <div className="upload-section">
        <h2 className="section-heading">Neues Kleidungsstück</h2>
        <form className="upload-form" onSubmit={handleUpload}>
          <label className="field">
            <span className="field-label">Name</span>
            <input
              className="input"
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="z. B. Schwarze Jeans"
              maxLength={100}
              required
            />
          </label>
          <label className="field">
            <span className="field-label">Kategorie</span>
            <select
              className="input category-select"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
            >
              {VALID_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span className="field-label">Bild</span>
            <div className="file-input-wrapper">
              <input
                ref={fileInputRef}
                className="input file-input"
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleFileChange}
                required
              />
              <span className="file-input-note">
                JPG, PNG, GIF oder WebP — max. 5 MB
              </span>
            </div>
          </label>
          <button
            className="btn btn-primary"
            type="submit"
            disabled={uploading || !newFile || !newName.trim()}
          >
            {uploading ? 'Wird hochgeladen...' : 'Hochladen'}
          </button>
        </form>
      </div>

      <div className="wardrobe-section">
        <h2 className="section-heading">
          Garderobe
          {items.length > 0 && (
            <span className="section-count">{items.length}</span>
          )}
        </h2>

        {categories.length > 1 && (
          <div className="filter-bar">
            <button
              className={`filter-tag ${activeCategory === null ? 'active' : ''}`}
              onClick={() => setActiveCategory(null)}
            >
              Alle
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                className={`filter-tag ${activeCategory === cat ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        {filteredItems.length === 0 ? (
          <div className="empty-state">
            <svg
              width="48"
              height="48"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M16 8L14 22L16 28M32 8L34 22L32 28M24 6V16M14 22H34M16 28V40H32V28M24 40V16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p>
              {activeCategory
                ? `Keine Kleidungsstücke in der Kategorie „${activeCategory}“`
                : 'Noch keine Kleidungsstücke — lade dein erstes hoch!'}
            </p>
          </div>
        ) : (
          <div className="gallery-grid">
            {filteredItems.map((item) => (
              <div key={item.id} className="gallery-card">
                <button
                  className="gallery-card-delete"
                  onClick={() => setDeleteTarget(item.id)}
                  aria-label="Löschen"
                >
                  &#x2715;
                </button>
                <div className="gallery-card-img">
                  <img
                    src={`/upload/${item.image_path}`}
                    alt={item.name}
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%231A1A1A" width="100" height="100"/><text fill="%23A0988C" x="50" y="55" text-anchor="middle" font-size="12">Kein Bild</text></svg>';
                    }}
                  />
                </div>
                <div className="gallery-card-body">
                  <span className="gallery-card-name">{item.name}</span>
                  <span className="badge">{item.category}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ConfirmDialog
        open={deleteTarget !== null}
        message="Dieses Kleidungsstück wirklich löschen? Es wird aus allen Outfits entfernt."
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
