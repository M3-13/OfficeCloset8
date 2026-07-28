import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getItems, type ClothingItem } from '../api/clothing';
import { createOutfit, updateOutfit, getOutfit, type OutfitCreateData } from '../api/outfits';
import OutfitPreview from '../components/OutfitPreview';

export default function OutfitCreatorPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get('edit');

  const [items, setItems] = useState<ClothingItem[]>([]);
  const [selectedByCategory, setSelectedByCategory] = useState<Record<string, number>>({});
  const [name, setName] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const groupedItems = items.reduce(
    (acc, item) => {
      if (!acc[item.category]) acc[item.category] = [];
      acc[item.category].push(item);
      return acc;
    },
    {} as Record<string, ClothingItem[]>,
  );

  const categories = Object.keys(groupedItems).sort();

  const selectedItems = Object.values(selectedByCategory)
    .map((id) => items.find((it) => it.id === id))
    .filter((it): it is ClothingItem => it !== undefined);

  const canSave = name.trim().length > 0 && selectedItems.length > 0 && !saving;

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getItems();
        if (!cancelled) {
          setItems(data);
          const cats = [...new Set(data.map((i) => i.category))];
          const expanded: Record<string, boolean> = {};
          cats.forEach((c) => (expanded[c] = true));
          setExpandedCategories(expanded);
        }
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

  useEffect(() => {
    if (!editId || items.length === 0) return;
    let cancelled = false;
    async function load() {
      try {
        const outfit = await getOutfit(Number(editId));
        if (cancelled) return;
        setName(outfit.name);
        const sel: Record<string, number> = {};
        outfit.items.forEach((it) => {
          sel[it.category] = it.id;
        });
        setSelectedByCategory(sel);
      } catch {
        // outfit not found or not owned
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [editId, items]);

  const toggleCategory = useCallback((cat: string) => {
    setExpandedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }));
  }, []);

  const selectItem = useCallback((category: string, itemId: number) => {
    setSelectedByCategory((prev) => {
      if (prev[category] === itemId) {
        const next = { ...prev };
        delete next[category];
        return next;
      }
      return { ...prev, [category]: itemId };
    });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const data: OutfitCreateData = {
        name: name.trim(),
        item_ids: Object.values(selectedByCategory),
      };
      if (editId) {
        await updateOutfit(Number(editId), data);
      } else {
        await createOutfit(data);
      }
      navigate('/saved-outfits');
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <p>Kleidungsstücke werden geladen...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>{editId ? 'Outfit bearbeiten' : 'Outfit-Creator'}</h1>

      <div className="outfit-name-bar">
        <input
          type="text"
          className="input"
          placeholder="Outfit-Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={100}
        />
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={!canSave}
        >
          {saving ? 'Wird gespeichert...' : 'Outfit speichern'}
        </button>
      </div>

      {error && <p className="error-message">{error}</p>}

      <div className="outfit-creator-layout">
        <div className="outfit-creator-left">
          {categories.length === 0 ? (
            <div className="empty-state">
              <p>Noch keine Kleidungsstücke in der Garderobe.</p>
              <p>Füge welche hinzu, um Outfits zu erstellen.</p>
            </div>
          ) : (
            categories.map((cat) => (
              <div key={cat} className="accordion">
                <button
                  className="accordion-header"
                  onClick={() => toggleCategory(cat)}
                >
                  <span>{cat}</span>
                  <span className={`accordion-arrow ${expandedCategories[cat] ? 'open' : ''}`}>
                    &#9662;
                  </span>
                </button>
                {expandedCategories[cat] && (
                  <div className="accordion-body">
                    <div className="item-grid">
                      {groupedItems[cat].map((item) => (
                        <button
                          key={item.id}
                          className={`item-card ${selectedByCategory[cat] === item.id ? 'selected' : ''}`}
                          onClick={() => selectItem(cat, item.id)}
                        >
                          <div className="item-card-img">
                            <img
                              src={`/upload/${item.image_path}`}
                              alt={item.name}
                              onError={(e) => {
                                (e.target as HTMLImageElement).src =
                                  'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%231A1A1A" width="100" height="100"/><text fill="%23A0988C" x="50" y="55" text-anchor="middle" font-size="12">Kein Bild</text></svg>';
                              }}
                            />
                          </div>
                          <span className="item-card-name">{item.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
        <div className="outfit-creator-right">
          <div className="outfit-stage">
            <h2>Vorschau</h2>
            <OutfitPreview items={selectedItems} />
          </div>
        </div>
      </div>
    </div>
  );
}
