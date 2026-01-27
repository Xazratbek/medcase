# 🏥 MedCase Pro Frontend

MedCase Pro tibbiy ta'lim platformasining React frontend qismi.

## 🛠 Texnologiyalar

- **React 18** - UI kutubxonasi
- **Vite** - Build vositasi
- **Tailwind CSS** - Styling
- **Framer Motion** - Animatsiyalar
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - HTTP so'rovlar
- **Recharts** - Grafiklar
- **React Hot Toast** - Bildirishnomalar

## 📁 Loyiha strukturasi

```
frontend/
├── public/              # Statik fayllar
├── src/
│   ├── components/      # Qayta ishlatiladigan komponentlar
│   │   ├── layout/      # Layout komponentlari
│   │   ├── ui/          # UI komponentlari
│   │   └── common/      # Umumiy komponentlar
│   ├── pages/           # Sahifa komponentlari
│   │   ├── auth/        # Autentifikatsiya sahifalari
│   │   └── ...          # Boshqa sahifalar
│   ├── store/           # Zustand store'lari
│   ├── hooks/           # Custom React hook'lar
│   ├── utils/           # Yordamchi funksiyalar
│   │   └── api.js       # API client
│   ├── assets/          # Rasmlar, ikonkalar
│   ├── App.jsx          # Asosiy komponent
│   ├── main.jsx         # Entry point
│   └── index.css        # Global stillar
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 🚀 O'rnatish

```bash
# Bog'liqliklarni o'rnatish
npm install

# Development server
npm run dev

# Production build
npm run build

# Build preview
npm run preview
```

## 🔧 Muhit o'zgaruvchilari

`.env` faylini yarating:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 📱 Sahifalar

| Sahifa | Yo'l | Tavsif |
|--------|------|--------|
| Landing | `/` | Bosh sahifa |
| Kirish | `/kirish` | Tizimga kirish |
| Ro'yxatdan o'tish | `/royxatdan-otish` | Yangi hisob |
| Dashboard | `/boshqaruv` | Boshqaruv paneli |
| Kategoriyalar | `/kategoriyalar` | Kategoriyalar ro'yxati |
| Holatlar | `/holatlar` | Klinik holatlar |
| Holat yechish | `/holat/:id/yechish` | Holatni yechish |
| Rivojlanish | `/rivojlanish` | Statistika va grafik |
| Reyting | `/reyting` | Reyting jadvali |
| Yutuqlar | `/yutuqlar` | Nishonlar |
| Profil | `/profil` | Foydalanuvchi profili |
| Sozlamalar | `/sozlamalar` | Hisob sozlamalari |
| Xatcholar | `/xatcholar` | Saqlangan holatlar |

## 🎨 Dizayn tizimi

### Ranglar

- **Primary (Med)**: `#14b89c` - Asosiy rang
- **Ocean**: `#0a1628` - Fon ranglari
- **Coral**: `#f43f5e` - Accent
- **Gold**: `#fbbf24` - Yutuqlar uchun

### Fontlar

- **Display**: Clash Display - Sarlavhalar
- **Body**: Satoshi - Asosiy matn
- **Mono**: JetBrains Mono - Kod

### Komponentlar

- `glass-card` - Shaffof kartalar
- `btn-primary` - Asosiy tugmalar
- `btn-secondary` - Ikkilamchi tugmalar
- `input-field` - Input maydonlari
- `badge-*` - Belgilar

## 📦 Build

```bash
# Production build
npm run build

# Build fayllarni tekshirish
npm run preview
```

Build fayllari `dist/` papkasida hosil bo'ladi.

## 🔗 Backend bilan integratsiya

Backend API `http://localhost:8000` da ishlashi kerak.
Vite dev server avtomatik ravishda `/api` so'rovlarini backendga proxy qiladi.

---

© 2024 MedCase Pro
