import { useState, useRef } from 'react';
import type { ClothingItem } from '../api/clothing';
import * as clothingApi from '../api/clothing';
import { CATEGORIES } from './CategoryFilter';

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

interface AddClothingFormProps {
  onCreated: (item: ClothingItem) => void;
  onCancel: () => void;
}

export default function AddClothingForm({ onCreated, onCancel }: AddClothingFormProps) {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  function validate(): string[] {
    const errs: string[] = [];

    const trimmedName = name.trim();
    if (!trimmedName) {
      errs.push('Name darf nicht leer sein');
    } else if (trimmedName.length > 100) {
      errs.push('Name darf maximal 100 Zeichen lang sein');
    }

    if (!category) {
      errs.push('Bitte eine Kategorie auswählen');
    } else if (!CATEGORIES.includes(category as (typeof CATEGORIES)[number])) {
      errs.push('Ungültige Kategorie');
    }

    if (!imageFile) {
      errs.push('Bitte ein Bild auswählen');
    } else if (imageFile.size > MAX_FILE_SIZE) {
      errs.push('Bild darf maximal 5 MB groß sein');
    } else if (!ALLOWED_TYPES.includes(imageFile.type)) {
      errs.push('Nur JPEG, PNG und WebP sind erlaubt');
    }

    return errs;
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setImageFile(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrors([]);

    const validationErrors = validate();
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('name', name.trim());
      formData.append('category', category);
      formData.append('image', imageFile!);

      const item = await clothingApi.createItem(formData);
      onCreated(item);
      setName('');
      setCategory('');
      setImageFile(null);
      setPreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setErrors([err instanceof Error ? err.message : 'Fehler beim Erstellen']);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      style={{
        background: 'var(--color-bg-card)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-4)',
        marginBottom: 'var(--space-4)',
      }}
    >
      <h2 style={{ marginBottom: 'var(--space-4)' }}>Neues Kleidungsstück</h2>

      {errors.length > 0 && (
        <div className="error-message">
          {errors.map((err, i) => (
            <div key={i}>{err}</div>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
        <div className="field">
          <label className="field-label" htmlFor="clothing-name">
            Name
          </label>
          <input
            id="clothing-name"
            className="input"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="z.B. Blaue Jeans"
            maxLength={100}
          />
        </div>

        <div className="field">
          <label className="field-label" htmlFor="clothing-category">
            Kategorie
          </label>
          <select
            id="clothing-category"
            className="input"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{ appearance: 'auto' }}
          >
            <option value="">-- Kategorie wählen --</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label className="field-label" htmlFor="clothing-image">
            Bild
          </label>
          <input
            ref={fileInputRef}
            id="clothing-image"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
            style={{
              color: 'var(--color-fg-muted)',
              fontSize: '0.875rem',
            }}
          />
        </div>

        {preview && (
          <div
            style={{
              aspectRatio: '3 / 4',
              maxWidth: '200px',
              overflow: 'hidden',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)',
            }}
          >
            <img
              src={preview}
              alt="Vorschau"
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>
        )}

        <div style={{ display: 'flex', gap: 'var(--space-2)', justifyContent: 'flex-end' }}>
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Abbrechen
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Speichern...' : 'Speichern'}
          </button>
        </div>
      </form>
    </div>
  );
}
