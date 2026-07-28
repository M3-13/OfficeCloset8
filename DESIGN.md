# Design — Project Identity

> This document is project-long-lived. Tokens are not changed without
> the Architect's approval. Developers MUST use these tokens
> instead of improvising their own colors/spacings.

## Style Direction

Dunkler Hollywood-Glamour mit tiefschwarzem Bühnenhintergrund, warmen Goldakzenten und Bordeaux-Rot – edle Serifen-Typografie trifft auf klare Sans-Serif, alles inszeniert wie ein Red-Carpet-Auftritt.

## Colors

- `--color-bg`: **#0A0A0A**
- `--color-bg-elevated`: **#141414**
- `--color-bg-card`: **#1A1A1A**
- `--color-fg`: **#F5F0EB**
- `--color-fg-muted`: **#A0988C**
- `--color-accent`: **#C9A84C**
- `--color-accent-hover`: **#D9B96C**
- `--color-accent-active`: **#B8923C**
- `--color-accent-spotlight`: **radial-gradient(ellipse at center, rgba(201,168,76,0.15) 0%, transparent 70%)**
- `--color-danger`: **#8B1A1A**
- `--color-danger-fg`: **#E8C0C0**
- `--color-success`: **#2D5A27**
- `--color-border`: **#2A2520**
- `--color-border-accent`: **#4A3F2E**
- `--color-overlay`: **rgba(0,0,0,0.7)**

## Typography

- `font_family`: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif
- `heading_font_family`: 'Playfair Display', 'Times New Roman', Georgia, serif
- `heading_weight`: 700
- `body_weight`: 400
- `mono_family`: 'JetBrains Mono', 'Fira Code', monospace

## Spacing Scale

- `--space-0`: 4px
- `--space-1`: 8px
- `--space-2`: 12px
- `--space-3`: 16px
- `--space-4`: 24px
- `--space-5`: 32px
- `--space-6`: 48px
- `--space-7`: 64px

## Border-Radii

- `--radius-sm`: 4px
- `--radius-md`: 8px
- `--radius-lg`: 16px
- `--radius-xl`: 24px
- `--radius-pill`: 999px

## Components

### Button (Primary – Gold)

padding 12px 28px, height min 44px, radius md (8px), bg=accent #C9A84C, fg=#0A0A0A (Schwarz auf Gold), font-weight 600, text-transform uppercase, letter-spacing 0.5px, border none. Hover: bg=#D9B96C (+10% L), transform scale(1.02), shadow 0 4px 20px rgba(201,168,76,0.35). Active: bg=#B8923C (-10% L), scale(0.98). Disabled: opacity 0.4, cursor not-allowed, no hover effects. Focus-visible: outline 2px solid #C9A84C, outline-offset 2px.

### Button (Secondary – Outline)

padding 12px 28px, height min 44px, radius md (8px), bg=transparent, fg=#C9A84C, border 1.5px solid #C9A84C, font-weight 600, uppercase, letter-spacing 0.5px. Hover: bg=rgba(201,168,76,0.08). Active: bg=rgba(201,168,76,0.15). Disabled: opacity 0.4. Identisch zu Primary: Focus-visible outline.

### Button (Danger)

padding 12px 28px, height min 44px, radius md, bg=#8B1A1A (Bordeaux), fg=#E8C0C0, border none, font-weight 600. Hover: bg=#A02020. Active: bg=#701515. Disabled: opacity 0.4.

### Card (Kleidungsstück / Outfit)

bg=#1A1A1A, border 1px solid #2A2520, radius lg (16px), overflow hidden. Image area: aspect-ratio 3/4, object-fit cover. Content: padding 12px 16px. Hover: border-color #4A3F2E, shadow 0 8px 32px rgba(201,168,76,0.1), transform translateY(-2px). Transition 200ms ease-out.

### Input Field

bg=#141414, fg=#F5F0EB, border 1.5px solid #2A2520, radius md (8px), padding 12px 16px, height min 44px, font-size 1rem. Placeholder: #A0988C. Focus: border-color #C9A84C, shadow 0 0 0 3px rgba(201,168,76,0.15). Invalid: border-color #8B1A1A. Disabled: opacity 0.5, bg=#0A0A0A.

### Modal / Dialog

bg=#141414, border 1px solid #2A2520, radius xl (24px), padding 32px, max-width 520px. Overlay: bg=rgba(0,0,0,0.7), backdrop-filter blur(4px). Shadow: 0 24px 80px rgba(0,0,0,0.6). Spotlight accent: subtle radial gradient at top center fading into bg.

### Nav / Header

bg=#0A0A0A (mit 85% Deckkraft + backdrop-blur 12px, sticky), height 64px, border-bottom 1px solid #2A2520. Logo/Titel in Playfair Display, fg=#C9A84C, 24px. Nav-Links: Inter, 14px, fg=#A0988C, hover=#F5F0EB. Aktiver Link: fg=#C9A84C, decorative underline (2px gold, 40% Breite, zentriert). Mobile: Hamburger-Menü mit goldener Icon-Farbe.

### Tag / Badge (Kategorie)

bg=transparent, fg=#A0988C, border 1px solid #2A2520, radius pill, padding 4px 12px, font-size 12px, text-transform uppercase, letter-spacing 0.3px. Hover (wenn klickbar): border-color #C9A84C, fg=#C9A84C.

### Outfit Stage (Bühnenfläche)

bg=#0A0A0A (oder bg-elevated), border 2px dashed #2A2520, radius lg (16px), min-height 400px, padding 24px, zentriert. Spotlights: zwei radiale Gold-Gradienten (accent-spotlight Token) von oben links und oben rechts einstrahlend. Leerer Zustand: zentrierter Placeholder-Text in fg-muted, Icon (Kleiderbügel-Silhouette) 48px in #2A2520. Mit Inhalt: Items als positionierte Cards, Drag-Handle sichtbar.

### Gallery Grid

CSS Grid: grid-template-columns repeat(auto-fill, minmax(220px, 1fr)), gap 24px. Bei Mobile (<768px): minmax(160px, 1fr), gap 16px. Filter-Bar oberhalb: horizontale Tags, scrollbar auf Mobile.

### Toast / Notification

bg=#1A1A1A, border-left 3px solid (success=#2D5A27, error=#8B1A1A, info=#C9A84C), radius md, padding 16px 20px, shadow 0 8px 32px rgba(0,0,0,0.5). Animation: slide-in von oben rechts, fade-out nach 4s. Max-width 380px.

## Layout Principles

- Container max-width 1200px, auto-margins, padding horizontal 24px (mobile 16px).
- Breakpoints: Mobile < 640px, Tablet 640–1024px, Desktop > 1024px.
- Seitenhintergrund durchgehend #0A0A0A, kein weißer Außenbereich.
- Spotlight-Akzente: Dezente radiale Gold-Gradienten auf hero-nahen Flächen (Login-Seite, Outfit-Creator-Bühne, leere States) – nie aufdringlich, immer subtil.
- Typografische Hierarchie: H1 = Playfair Display 2.5rem (mobile 1.75rem), H2 = Playfair 1.75rem, H3 = Inter 600 1.25rem, Body = Inter 400 1rem. Gold-Farbe reserviert für H1, Akzent-Elemente und aktive States.
- Abstände zwischen Sektionen: 48px (mobile 32px). Innerhalb von Cards: 12–16px.
- Hover-Effekte durchgängig mit 200–250ms ease-out, leichte Scale-Transformationen (max 1.02–1.05) für ein fließendes, luxuriöses Gefühl.
- Bild-Galerie: Sanfte Hover-Effekte, Bilder mit leichtem Border-Radius (8px Innen, 16px Card). Keine harten Kanten.
- Formulare: Labels oberhalb des Inputs, Abstand 8px. Fehlermeldungen direkt unter dem Feld in #E8C0C0 (Danger-FG).
- Mobile: Navigation als Bottom-Bar (Höhe 56px) mit 4–5 Icons + Labels, aktives Icon in Gold.
