import type { ClothingItem } from '../api/outfits';

interface OutfitPreviewProps {
  items: ClothingItem[];
}

export default function OutfitPreview({ items }: OutfitPreviewProps) {
  if (items.length === 0) {
    return (
      <div className="outfit-preview-empty">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M16 8L14 22L16 28M32 8L34 22L32 28M24 6V16M14 22H34M16 28V40H32V28M24 40V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        <p>Wähle Kleidungsstücke aus, um dein Outfit zu sehen</p>
      </div>
    );
  }

  return (
    <div className="outfit-preview-list">
      {items.map((item) => (
        <div key={item.id} className="outfit-preview-item">
          <div className="outfit-preview-thumb">
            <img
              src={item.image_path}
              alt={item.name}
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%231A1A1A" width="100" height="100"/><text fill="%23A0988C" x="50" y="55" text-anchor="middle" font-size="12">Kein Bild</text></svg>';
              }}
            />
          </div>
          <div className="outfit-preview-info">
            <span className="outfit-preview-name">{item.name}</span>
            <span className="outfit-preview-category">{item.category}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
