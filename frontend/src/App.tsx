import { Routes, Route } from 'react-router-dom';
import { AuthProvider, RequireAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import WardrobePage from './pages/WardrobePage';
import OutfitCreatorPage from './pages/OutfitCreatorPage';
import SavedOutfitsPage from './pages/SavedOutfitsPage';
import AccountPage from './pages/AccountPage';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/wardrobe" element={<RequireAuth><WardrobePage /></RequireAuth>} />
          <Route path="/outfit-creator" element={<RequireAuth><OutfitCreatorPage /></RequireAuth>} />
          <Route path="/saved-outfits" element={<RequireAuth><SavedOutfitsPage /></RequireAuth>} />
          <Route path="/account" element={<RequireAuth><AccountPage /></RequireAuth>} />
          <Route path="/" element={<LoginPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  );
}
