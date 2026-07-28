import { type FormEvent, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      navigate('/wardrobe');
    }
  }, [user, loading, navigate]);

  if (loading) {
    return (
      <div className="loading-state">
        <p>Wird geladen...</p>
      </div>
    );
  }

  if (user) {
    return null;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      navigate('/wardrobe');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login fehlgeschlagen');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Anmelden</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <label className="field">
            <span className="field-label">E-Mail</span>
            <input
              className="input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="deine@email.de"
            />
          </label>
          <label className="field">
            <span className="field-label">Passwort</span>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="••••••••"
            />
          </label>
          {error && <p className="field-error">{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Wird angemeldet…' : 'Anmelden'}
          </button>
        </form>
        <p className="auth-switch">
          Noch kein Konto? <Link to="/register">Jetzt registrieren</Link>
        </p>
      </div>
    </div>
  );
}
