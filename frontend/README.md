# Egyptian Grocery Admin Dashboard

React + TypeScript admin dashboard for managing Egyptian supermarket data.

## Features

- 📊 **Dashboard**: Overview of statistics
- 🏪 **Stores**: Manage stores and branches
- 🏷️ **Categories**: CRUD for product categories (Arabic + English)
- 📦 **Products**: Browse and manage products
- 📄 **Catalogues**: Upload PDFs/images, OCR processing
- 📤 **Export**: Download data for mobile app
- 🤖 **Scrapers**: Trigger and monitor scrapers

## Tech Stack

- **Framework**: Vite + React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack React Query
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Icons**: Lucide React

## Quick Start

### Prerequisites

```bash
node >= 18
npm >= 9
```

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Build
docker build -t grocery-admin-frontend .

# Run
docker run -p 3000:3000 grocery-admin-frontend
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── pages/          # Page components
│   ├── Dashboard.tsx
│   ├── Stores.tsx
│   ├── Categories.tsx
│   ├── Products.tsx
│   ├── Catalogues.tsx
│   ├── Export.tsx
│   └── Scrapers.tsx
├── services/       # API services
│   └── api.ts
├── types/          # TypeScript types
│   └── index.ts
├── App.tsx         # Main app component
├── main.tsx        # Entry point
└── index.css       # Global styles
```

## API Integration

The dashboard connects to the FastAPI backend at `http://localhost:8000` by default.

### Key Endpoints Used

- `GET /api/v1/stores` - List stores
- `GET /api/v1/categories` - List categories
- `GET /api/v1/products` - List products
- `GET /api/v1/catalogues` - List catalogues
- `POST /api/v1/catalogues/{id}/upload` - Upload catalogue files
- `POST /api/v1/catalogues/{id}/process` - Process with OCR
- `POST /api/v1/scraper/run` - Run scrapers
- `GET /api/v1/export/app` - Export data

## License

MIT
