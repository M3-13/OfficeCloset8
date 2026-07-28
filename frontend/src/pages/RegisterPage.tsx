import { type FormEvent, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const EMAIL_REGEX = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

export default function RegisterPage() {
  const { user, loading, register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordRepeat, setPasswordRepeat] = useState('');
  const [errors, setErrors] = useState<string[]>([]);
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

  function validate(): boolean {
    const errs: string[] = [];
    if (!EMAIL_REGEX.test(email)) {
      errs.push('Ungültiges E-Mail-Format');
    }
    if (email.length > 254) {
      errs.push('E-Mail zu lang (max. 254 Zeichen)');
    }
    if (password.length < 8) {
      errs.push('Passwort muss mindestens 8 Zeichen lang sein');
    }
    if (password !== passwordRepeat) {
      errs.push('Passwörter stimmen nicht überein');
    }
    setErrors(errs);
    return errs.length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setErrors([]);
    setSubmitting(true);
    try {
      await register(email, password);
      navigate('/wardrobe');
    } catch (err) {
      setErrors([err instanceof Error ? err.message : 'Registrierung fehlgeschlagen']);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Registrierung</h1>
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
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
              autoComplete="new-password"
              placeholder="Mindestens 8 Zeichen"
            />
          </label>
          <label className="field">
            <span className="field-label">Passwort wiederholen</span>
            <input
              className="input"
              type="password"
              value={passwordRepeat}
              onChange={(e) => setPasswordRepeat(e.target.value)}
              required
              autoComplete="new-password"
              placeholder="Passwort wiederholen"
            />
          </label>
          {errors.length > 0 && (
            <div className="field-errors">
              {errors.map((err, i) => (
                <p key={i} className="field-error">{err}</p>
              ))}
            </div>
          )}
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Wird registriert…' : 'Registrieren'}
          </button>
        </form>
        <p className="auth-switch">
          Bereits registriert? <Link to="/login">Jetzt anmelden</Link>
        </p>
      </div>
    </div>
  );
}
