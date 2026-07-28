import { useState, useRef } from 'react';
import { createItem } from '../api/clothing';

const CATEGORIES = ['Oberteil', 'Hose', 'Schuhe', 'Accessoire', 'Kleid', 'Jacke'];
const MAX_SIZE = 5 * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

interface AddClothingFormProps {
  onCreated: () => void;
  onCancel: () => void;
}

export default function AddClothingForm({ onCreated, onCancel }: AddClothingFormProps) {
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setError(null);

    if (!file) {
      setImage(null);
      setPreview(null);
      return;
    }

    if (!ALLOWED_TYPES.includes(file.type)) {
      setError('Nur JPEG, PNG und WebP sind erlaubt');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    if (file.size > MAX_SIZE) {
      setError('Bild darf maximal 5 MB groß sein');
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setImage(file);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Name darf nicht leer sein');
      return;
    }

    if (name.length > 100) {
      setError('Name darf maximal 100 Zeichen lang sein');
      return;
    }

    if (!category) {
      setError('Bitte eine Kategorie auswählen');
      return;
    }

    if (!image) {
      setError('Bitte ein Bild auswählen');
      return;
    }

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('name', name.trim());
      formData.append('category', category);
      formData.append('image', image);
      await createItem(formData);
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Fehler beim Anlegen');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="add-clothing-form">
      <h2>Neues Kleidungsstück</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          className="input"
          maxLength={100}
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="z. B. Schwarzes Abendkleid"
        />

        <label htmlFor="category">Kategorie</label>
        <select
          id="category"
          className="input"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">-- Kategorie wählen --</option>
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>

        <label htmlFor="image">Bild</label>
        <input
          id="image"
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleImageChange}
        />
        {preview && (
          <div className="image-preview">
            <img src={preview} alt="Vorschau" />
          </div>
        )}

        {error && <p className="form-error">{error}</p>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Speichere...' : 'Speichern'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Abbrechen
          </button>
        </div>
      </form>
    </div>
  );
}
