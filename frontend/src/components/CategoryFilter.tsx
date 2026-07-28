export const CATEGORIES = ['Oberteil', 'Hose', 'Schuhe', 'Accessoire', 'Kleid', 'Jacke'] as const;

interface CategoryFilterProps {
  categories: readonly string[];
  selected: string;
  onChange: (category: string) => void;
}

export default function CategoryFilter({ categories, selected, onChange }: CategoryFilterProps) {
  return (
    <div style={{ display: 'flex', gap: 'var(--space-1)', flexWrap: 'wrap', marginBottom: 'var(--space-4)' }}>
      <button
        className={`badge ${selected === '' ? '' : ''}`}
        style={{
          cursor: 'pointer',
          background: selected === '' ? 'var(--color-accent)' : 'transparent',
          color: selected === '' ? 'var(--color-bg)' : 'var(--color-fg-muted)',
          borderColor: selected === '' ? 'var(--color-accent)' : 'var(--color-border)',
          fontWeight: selected === '' ? 600 : 400,
        }}
        onClick={() => onChange('')}
      >
        Alle
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          className="badge"
          style={{
            cursor: 'pointer',
            background: selected === cat ? 'var(--color-accent)' : 'transparent',
            color: selected === cat ? 'var(--color-bg)' : 'var(--color-fg-muted)',
            borderColor: selected === cat ? 'var(--color-accent)' : 'var(--color-border)',
            fontWeight: selected === cat ? 600 : 400,
          }}
          onClick={() => onChange(cat)}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
