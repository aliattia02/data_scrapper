import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { FileText, Download, Edit2, Trash2, Loader2 } from 'lucide-react'
import {
  scrapeCataloguePdf,
  scrapeStoreCatalogues,
  listCatalogues,
  renameCatalogue,
  deleteCatalogue,
  getCataloguePdfUrl,
} from '../services/api'

const MARKET_CATEGORIES = [
  'Supermarket',
  'Hypermarket',
  'Grocery',
  'Electronics',
  'Fashion',
  'Home & Garden',
  'Pharmacy',
  'Other',
]

export default function PdfScraper() {
  // Single catalogue form
  const [singleUrl, setSingleUrl] = useState('')
  
  // Multi-catalogue form
  const [storeUrl, setStoreUrl] = useState('')
  
  // Metadata form
  const [marketCategory, setMarketCategory] = useState('Supermarket')
  const [marketName, setMarketName] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  
  // Rename state
  const [renamingId, setRenamingId] = useState<number | null>(null)
  const [newName, setNewName] = useState('')

  // Fetch catalogues
  const { data: catalogues, isLoading, refetch } = useQuery({
    queryKey: ['pdf-catalogues'],
    queryFn: async () => {
      const response = await listCatalogues()
      return response.data
    },
  })

  // Single catalogue scraping
  const scrapeSingleMutation = useMutation({
    mutationFn: () => scrapeCataloguePdf({
      url: singleUrl,
      market_category: marketCategory,
      market_name: marketName,
      start_date: startDate,
      end_date: endDate,
      latitude: latitude ? parseFloat(latitude) : undefined,
      longitude: longitude ? parseFloat(longitude) : undefined,
    }),
    onSuccess: () => {
      alert('Catalogue scraped successfully!')
      setSingleUrl('')
      refetch()
    },
    onError: (error: any) => {
      alert(`Scraping failed: ${error.response?.data?.detail || error.message}`)
    },
  })

  // Multi-catalogue scraping
  const scrapeStoreMutation = useMutation({
    mutationFn: () => scrapeStoreCatalogues({
      store_url: storeUrl,
      market_category: marketCategory,
      market_name: marketName,
      latitude: latitude ? parseFloat(latitude) : undefined,
      longitude: longitude ? parseFloat(longitude) : undefined,
    }),
    onSuccess: (response) => {
      alert(`Successfully scraped ${response.data.total} catalogues!`)
      setStoreUrl('')
      refetch()
    },
    onError: (error: any) => {
      alert(`Scraping failed: ${error.response?.data?.detail || error.message}`)
    },
  })

  // Rename mutation
  const renameMutation = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => 
      renameCatalogue(id, name),
    onSuccess: () => {
      setRenamingId(null)
      setNewName('')
      refetch()
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteCatalogue(id),
    onSuccess: () => {
      refetch()
    },
  })

  const handleScrapeSingle = () => {
    if (!singleUrl || !marketName || !startDate || !endDate) {
      alert('Please fill in URL, market name, and dates')
      return
    }
    scrapeSingleMutation.mutate()
  }

  const handleScrapeStore = () => {
    if (!storeUrl || !marketName) {
      alert('Please fill in store URL and market name')
      return
    }
    scrapeStoreMutation.mutate()
  }

  const handleRename = (id: number) => {
    if (!newName) return
    renameMutation.mutate({ id, name: newName })
  }

  const handleDelete = (id: number, filename: string) => {
    if (confirm(`Delete ${filename}?`)) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <FileText className="w-8 h-8" />
          PDF Catalogue Scraper
        </h1>
        <p className="text-gray-600 mt-2">
          Scrape catalogues and save as PDFs (no OCR processing)
        </p>
      </div>

      {/* Single Catalogue Scraping */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Scrape Single Catalogue</h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={singleUrl}
            onChange={(e) => setSingleUrl(e.target.value)}
            placeholder="Catalogue URL (e.g., https://www.filloffer.com/markets/...)"
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            onClick={handleScrapeSingle}
            disabled={scrapeSingleMutation.isPending}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md disabled:bg-gray-300 flex items-center gap-2"
          >
            {scrapeSingleMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Scraping...
              </>
            ) : (
              'Scrape'
            )}
          </button>
        </div>
      </div>

      {/* Multi-Catalogue Scraping */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Scrape All Catalogues from Store Page</h2>
        <div className="space-y-3">
          <input
            type="text"
            value={storeUrl}
            onChange={(e) => setStoreUrl(e.target.value)}
            placeholder="Store page URL (e.g., https://www.filloffer.com/markets/Metro-Markets)"
            className="w-full border rounded px-3 py-2"
          />
          <p className="text-sm text-gray-500">
            This will find and scrape all catalogue links on the store page
          </p>
          <button
            onClick={handleScrapeStore}
            disabled={scrapeStoreMutation.isPending}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md disabled:bg-gray-300 flex items-center gap-2"
          >
            {scrapeStoreMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Scraping...
              </>
            ) : (
              'Scrape All Catalogues'
            )}
          </button>
        </div>
      </div>

      {/* Metadata Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Catalogue Metadata</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Market Category
            </label>
            <select
              value={marketCategory}
              onChange={(e) => setMarketCategory(e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              {MARKET_CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Market Name *
            </label>
            <input
              type="text"
              value={marketName}
              onChange={(e) => setMarketName(e.target.value)}
              placeholder="e.g., Metro"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date *
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date *
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Latitude
            </label>
            <input
              type="number"
              step="0.0001"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              placeholder="e.g., 30.0444"
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Longitude
            </label>
            <input
              type="number"
              step="0.0001"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              placeholder="e.g., 31.2357"
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Scraped PDFs List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Scraped PDFs</h2>
        
        {isLoading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : catalogues?.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No catalogues yet. Scrape one above!
          </div>
        ) : (
          <div className="space-y-3">
            {catalogues?.map((cat: any) => (
              <div
                key={cat.id}
                className="border rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex items-center gap-3 flex-1">
                  <FileText className="w-6 h-6 text-blue-500" />
                  <div>
                    {renamingId === cat.id ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          placeholder="New filename"
                          className="border rounded px-2 py-1 text-sm"
                          autoFocus
                        />
                        <button
                          onClick={() => handleRename(cat.id)}
                          className="text-green-600 hover:text-green-700 text-sm"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => {
                            setRenamingId(null)
                            setNewName('')
                          }}
                          className="text-gray-600 hover:text-gray-700 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <>
                        <p className="font-medium">
                          {cat.originalFilename || `catalogue_${cat.id}.pdf`}
                        </p>
                        <p className="text-sm text-gray-500">
                          {cat.marketName} • {cat.pageCount} pages
                          {cat.validFrom && cat.validUntil && (
                            <> • {new Date(cat.validFrom).toLocaleDateString()} - {new Date(cat.validUntil).toLocaleDateString()}</>
                          )}
                        </p>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => {
                      setRenamingId(cat.id)
                      setNewName(cat.originalFilename?.replace('.pdf', '') || '')
                    }}
                    className="p-2 text-gray-600 hover:text-blue-600"
                    title="Rename"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  
                  <a
                    href={getCataloguePdfUrl(cat.id)}
                    download
                    className="p-2 text-gray-600 hover:text-green-600"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                  
                  <button
                    onClick={() => handleDelete(cat.id, cat.originalFilename)}
                    className="p-2 text-gray-600 hover:text-red-600"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
