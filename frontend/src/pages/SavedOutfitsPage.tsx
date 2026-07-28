import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getOutfits, deleteOutfit, type Outfit } from '../api/outfits';
import ConfirmDialog from '../components/ConfirmDialog';

export default function SavedOutfitsPage() {
  const navigate = useNavigate();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await getOutfits();
        if (!cancelled) setOutfits(data);
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

  const handleDelete = async () => {
    if (deleteTarget === null) return;
    setDeleting(true);
    try {
      await deleteOutfit(deleteTarget);
      setOutfits((prev) => prev.filter((o) => o.id !== deleteTarget));
      setDeleteTarget(null);
      setExpandedId(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setDeleting(false);
    }
  };

  const handleEdit = (outfit: Outfit) => {
    navigate(`/outfit-creator?edit=${outfit.id}`);
  };

  if (loading) {
    return (
      <div className="loading-state">
        <p>Outfits werden geladen...</p>
      </div>
    );
  }

  return (
    <div>
      <h1>Gespeicherte Outfits</h1>

      {error && <p className="error-message">{error}</p>}

      {outfits.length === 0 && !loading ? (
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
          <p>Noch keine Outfits – erstelle dein erstes im Outfit-Creator!</p>
          <button
            className="btn btn-primary"
            onClick={() => navigate('/outfit-creator')}
            style={{ marginTop: 'var(--space-3)' }}
          >
            Zum Outfit-Creator
          </button>
        </div>
      ) : (
        <div className="outfit-grid">
          {outfits.map((outfit) => (
            <div key={outfit.id} className="outfit-card">
              <div
                className="outfit-card-header"
                onClick={() => setExpandedId(expandedId === outfit.id ? null : outfit.id)}
              >
                <div className="outfit-card-preview-imgs">
                  {outfit.items.slice(0, 3).map((item) => (
                    <div key={item.id} className="outfit-card-preview-img">
                      <img
                        src={`/upload/${item.image_path}`}
                        alt={item.name}
                        onError={(e) => {
                          (e.target as HTMLImageElement).src =
                            'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%231A1A1A" width="100" height="100"/><text fill="%23A0988C" x="50" y="55" text-anchor="middle" font-size="12">Kein Bild</text></svg>';
                        }}
                      />
                    </div>
                  ))}
                  {outfit.items.length === 0 && (
                    <div className="outfit-card-preview-img outfit-card-preview-placeholder">
                      <span>?</span>
                    </div>
                  )}
                </div>
                <div className="outfit-card-summary">
                  <h3 className="outfit-card-name">{outfit.name}</h3>
                  <span className="outfit-card-count">
                    {outfit.items.length} {outfit.items.length === 1 ? 'Teil' : 'Teile'}
                  </span>
                </div>
                <span className={`accordion-arrow ${expandedId === outfit.id ? 'open' : ''}`}>
                  &#9662;
                </span>
              </div>

              {expandedId === outfit.id && (
                <div className="outfit-card-detail">
                  <div className="outfit-card-items">
                    {outfit.items.map((item) => (
                      <div key={item.id} className="outfit-detail-item">
                        <img
                          src={`/upload/${item.image_path}`}
                          alt={item.name}
                          onError={(e) => {
                            (e.target as HTMLImageElement).src =
                              'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%231A1A1A" width="100" height="100"/><text fill="%23A0988C" x="50" y="55" text-anchor="middle" font-size="12">Kein Bild</text></svg>';
                          }}
                        />
                        <div className="outfit-detail-item-info">
                          <span>{item.name}</span>
                          <span className="badge">{item.category}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="outfit-card-actions">
                    <button className="btn btn-primary" onClick={() => handleEdit(outfit)}>
                      Bearbeiten
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => setDeleteTarget(outfit.id)}
                    >
                      Löschen
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        message={deleting ? 'Wird gelöscht...' : 'Wirklich löschen?'}
        onConfirm={handleDelete}
        onCancel={() => !deleting && setDeleteTarget(null)}
      />
    </div>
  );
}
