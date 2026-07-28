interface CategoryFilterProps {
  categories: string[];
  selected: string | null;
  onChange: (category: string | null) => void;
}

export default function CategoryFilter({ categories, selected, onChange }: CategoryFilterProps) {
  return (
    <div className="category-filter">
      <button
        type="button"
        className={`filter-btn ${selected === null ? 'active' : ''}`}
        onClick={() => onChange(null)}
      >
        Alle
      </button>
      {categories.map((cat) => (
        <button
          type="button"
          key={cat}
          className={`filter-btn ${selected === cat ? 'active' : ''}`}
          onClick={() => onChange(cat)}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
