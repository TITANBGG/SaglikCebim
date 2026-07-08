# SaglikCebim Figma Blueprint

Bu belge, mevcut React arayuzunu bozmadan daha premium ve modern bir Figma mockup'u uretmek icin hazirlandi. Tasarim dili: klinik, guven veren, hafif futuristic ama abartisiz.

## 1) Tasarim Yonelimi

- Tema: koyu lacivert arka plan, cammsi kartlar, turkuaz vurgu.
- Hedef his: profesyonel saglik paneli, veri yogun ama sakin.
- Ana dil: dashboard-first, yan menulu, kart tabanli, cok bos alanli degil ama nefes aliyor.

## 2) Renk Sistemi

### Ana Renkler

- `Background`: `#08111f`
- `Surface / Sidebar`: `#0f1b2f`
- `Card`: `#13233d`
- `Card Hover`: `#18304f`
- `Border Soft`: `rgba(149, 184, 224, 0.18)`
- `Border Strong`: `rgba(34, 211, 238, 0.32)`

### Accent

- `Cyan`: `#2dd4ff`
- `Cyan Bright`: `#67f2ff`
- `Blue`: `#4f7cff`
- `Indigo`: `#6875f5`

### Semantic

- `Success`: `#22c55e`
- `Warning`: `#f59e0b`
- `Danger`: `#ef4444`
- `Info`: `#38bdf8`

### Text

- `Primary`: `#f4f7fb`
- `Secondary`: `#b8c5d6`
- `Tertiary`: `#7f93ad`
- `Inverse`: `#08111f`

## 3) Typography

Font tercihi: `Inter` veya `Manrope`.

### Scale

- `Display`: 28 / 34, weight 700
- `H1`: 22 / 28, weight 700
- `H2`: 18 / 24, weight 650
- `Body`: 14 / 20, weight 400
- `Body Strong`: 14 / 20, weight 600
- `Caption`: 12 / 16, weight 500
- `Micro`: 11 / 14, weight 500

## 4) Spacing / Radius / Shadow

### Spacing Grid

- `4`
- `8`
- `12`
- `16`
- `24`
- `32`

### Radius

- `Card`: 18
- `Button`: 12
- `Input`: 12
- `Chip`: 999

### Shadow

- `Soft`: `0 10px 30px rgba(2, 8, 23, 0.24)`
- `Lift`: `0 20px 50px rgba(2, 8, 23, 0.34)`
- `Glow`: `0 0 0 1px rgba(45, 212, 255, 0.28), 0 0 32px rgba(45, 212, 255, 0.12)`

## 5) Layout Frames

### Frame A - Dashboard Desktop

- Size: `1440 x 1024`
- Grid: `12 columns`, margin `32`, gutter `24`
- Left sidebar: `250px` fixed
- Main content: fluid

#### Sections

1. Sidebar
2. Top header
3. KPI cards row
4. Main content grid: `Reports List` + `Trend Chart`
5. Optional bottom rail for insights / quick actions

### Frame B - Dashboard Mobile

- Size: `390 x 844`
- Grid: `4 columns`
- Sidebar becomes bottom nav or compact top nav
- KPI cards stack vertically 2x2 or 1 column
- Chart moves below summary cards

### Frame C - PDF Analiz

- Size: `1440 x 1024`
- Left: upload / drag-drop area
- Right: extracted reports table and status chips
- Bottom: validation notes + suggestions

### Frame D - Radyoloji

- Size: `1440 x 1024`
- Left: image upload + preview
- Right: findings panel + probability rows + clinical notes

## 6) Component Library

### Buttons

- Primary: cyan gradient, strong contrast, 12px radius
- Secondary: transparent dark surface, cyan border
- Ghost: only text + icon, no heavy fill

### Cards

- Metric card: icon, label, large value, subtle badge line
- Panel card: heading, subheading, content area
- Report row card: file icon, title, status, date

### Chips / Badges

- Status chip: success / warning / danger / info
- Nav active chip: cyan glow + surface lift

### Inputs

- Search: rounded, icon left, soft border
- Select: dark surface, caret icon right
- File upload: dashed border, drag state glow

## 7) Dashboard Content Blueprint

### Top Bar

- Left: date
- Main: page title `Saglik Analiz Paneli`
- Subtitle: `PDF tahliller, grafikler ve radyoloji sonuclari tek ekranda.`
- Right: `Sistem aktif` chip or `Canli veri` chip

### KPI Row

Card 1: `Analiz edilen PDF`

Card 2: `Anormal bulgu`

Card 3: `Normal sonuc`

Card 4: `X-ray analizi`

### Main Grid

- Left panel: `Analiz edilen raporlar`
- Right panel: `Trend grafikleri`

### Report Rows

- `e-Nabiz Kan Tahlili.pdf` - `Analiz edildi`
- `Check-up Sonuclari.pdf` - `PDF parse edildi`
- `Radyoloji X-Ray.png` - `Goruntu incelendi`

## 8) Visual Notes For Figma

- Use 1 subtle background gradient only; avoid loud neon fills.
- Keep borders 1px and low opacity.
- Make the primary CTA clearly cyan, but do not saturate all surfaces.
- Give charts extra whitespace and a tiny legend row.
- Use one icon style set across all components.
- Use the same card padding rhythm everywhere: `20-24px`.

## 9) Suggested Figma Pages

1. `Design System`
2. `Components`
3. `Dashboard`
4. `PDF Analiz`
5. `Radyoloji`
6. `Mobile`

## 10) Handoff Mapping To Current Routes

- `/dashboard` -> dashboard master frame
- `/upload` -> PDF analiz frame
- `/trends` -> trend focus frame
- `/radiology` -> radyoloji frame
- `/articles` -> content/article card layout

## 11) First Figma Build Order

1. Colors and text styles
2. Buttons, chips, cards
3. Sidebar and top bar
4. Dashboard desktop frame
5. PDF Analiz frame
6. Radyoloji frame
7. Mobile variants

## 12) Recommendation

Bu proje icin en guclu ilk ekran `Dashboard` olacak. Figma'da once onu bitirip sonra `PDF Analiz` ve `Radyoloji` frame'lerine gecmek en dogru siralama.