import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Package, Store, Tag, FileText, Download, Play, FilePlus } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Stores from './pages/Stores'
import Categories from './pages/Categories'
import Products from './pages/Products'
import Catalogues from './pages/Catalogues'
import PdfScraper from './pages/PdfScraper'
import Export from './pages/Export'
import Scrapers from './pages/Scrapers'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-gray-800">
                    🇪🇬 Egyptian Grocery Admin
                  </h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <NavLink to="/" icon={<Package />}>Dashboard</NavLink>
                  <NavLink to="/stores" icon={<Store />}>Stores</NavLink>
                  <NavLink to="/categories" icon={<Tag />}>Categories</NavLink>
                  <NavLink to="/products" icon={<Package />}>Products</NavLink>
                  <NavLink to="/catalogues" icon={<FileText />}>Catalogues</NavLink>
                  <NavLink to="/pdf-scraper" icon={<FilePlus />}>PDF Scraper</NavLink>
                  <NavLink to="/export" icon={<Download />}>Export</NavLink>
                  <NavLink to="/scrapers" icon={<Play />}>Scrapers</NavLink>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stores" element={<Stores />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/products" element={<Products />} />
            <Route path="/catalogues" element={<Catalogues />} />
            <Route path="/pdf-scraper" element={<PdfScraper />} />
            <Route path="/export" element={<Export />} />
            <Route path="/scrapers" element={<Scrapers />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

function NavLink({ to, icon, children }: { to: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700"
    >
      <span className="mr-2">{icon}</span>
      {children}
    </Link>
  )
}

export default App
