import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ConfirmDialog from '../components/ConfirmDialog';

export default function AccountPage() {
  const { user, deleteAccount } = useAuth();
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();

  async function handleDelete() {
    setShowConfirm(false);
    await deleteAccount();
    navigate('/');
  }

  return (
    <div>
      <h1>Konto</h1>
      {user && (
        <p>
          E-Mail: <strong>{user.email}</strong>
        </p>
      )}
      <button className="btn btn-danger" onClick={() => setShowConfirm(true)}>
        Konto löschen
      </button>
      <ConfirmDialog
        open={showConfirm}
        message="Wirklich löschen? Alle deine Kleidungsstücke, Bilder und Outfits werden unwiderruflich entfernt."
        onConfirm={handleDelete}
        onCancel={() => setShowConfirm(false)}
      />
    </div>
  );
}
