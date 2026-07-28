import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import WardrobePage from "./pages/WardrobePage";
import OutfitCreatorPage from "./pages/OutfitCreatorPage";
import SavedOutfitsPage from "./pages/SavedOutfitsPage";
import AccountPage from "./pages/AccountPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<WardrobePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/wardrobe" element={<WardrobePage />} />
        <Route path="/create" element={<OutfitCreatorPage />} />
        <Route path="/outfits" element={<SavedOutfitsPage />} />
        <Route path="/account" element={<AccountPage />} />
      </Route>
    </Routes>
  );
}
