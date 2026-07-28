import type { ClothingItem } from '../api/clothing';

interface ClothingCardProps {
  item: ClothingItem;
  onDelete: (id: number) => void;
}

export default function ClothingCard({ item, onDelete }: ClothingCardProps) {
  return (
    <div className="clothing-card">
      <div className="card-image">
        <img src={item.image_url} alt={item.name} loading="lazy" />
      </div>
      <div className="card-body">
        <h3 className="card-name">{item.name}</h3>
        <span className="badge">{item.category}</span>
        <button
          type="button"
          className="btn btn-danger card-delete-btn"
          onClick={() => {
            if (window.confirm('Wirklich löschen?')) {
              onDelete(item.id);
            }
          }}
        >
          Löschen
        </button>
      </div>
    </div>
  );
}
