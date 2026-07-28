import type { ClothingItem } from '../api/clothing';

interface ClothingCardProps {
  item: ClothingItem;
  onDelete: (itemId: number) => void;
}

export default function ClothingCard({ item, onDelete }: ClothingCardProps) {
  function handleDelete() {
    if (window.confirm('Wirklich löschen?')) {
      onDelete(item.id);
    }
  }

  return (
    <div
      style={{
        background: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        transition: 'border-color 200ms ease-out, box-shadow 200ms ease-out, transform 200ms ease-out',
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.borderColor = 'var(--color-border-accent)';
        (e.currentTarget as HTMLElement).style.boxShadow = '0 8px 32px rgba(201,168,76,0.1)';
        (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.borderColor = 'var(--color-border)';
        (e.currentTarget as HTMLElement).style.boxShadow = '';
        (e.currentTarget as HTMLElement).style.transform = '';
      }}
    >
      <div
        style={{
          aspectRatio: '3 / 4',
          overflow: 'hidden',
          background: 'var(--color-bg-elevated)',
        }}
      >
        <img
          src={item.image_path}
          alt={item.name}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      </div>
      <div style={{ padding: 'var(--space-2) var(--space-3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-1)' }}>
          <span
            style={{
              fontWeight: 600,
              fontSize: '0.9375rem',
              color: 'var(--color-fg)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              maxWidth: '70%',
            }}
          >
            {item.name}
          </span>
          <span className="badge">{item.category}</span>
        </div>
        <button
          className="btn btn-danger"
          style={{ width: '100%', padding: '8px 16px', minHeight: '36px', fontSize: '0.8125rem' }}
          onClick={handleDelete}
        >
          Löschen
        </button>
      </div>
    </div>
  );
}
