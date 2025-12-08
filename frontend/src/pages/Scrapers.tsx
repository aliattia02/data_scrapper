import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { runScraper, scrapeFromUrl } from '../services/api'
import { Play, FileDown, AlertCircle, Link as LinkIcon } from 'lucide-react'

export default function Scrapers() {
  const [logs, setLogs] = useState<string[]>([])
  const [catalogueUrl, setCatalogueUrl] = useState('')
  const [urlStore, setUrlStore] = useState('kazyon')

  const scraperMutation = useMutation({
    mutationFn: runScraper,
    onSuccess: (response) => {
      const results = response.data.results || []
      const summary = results.map((r: any) => 
        `${r.store}: ${r.products} products`
      ).join(', ')
      setLogs((prev) => [...prev, `✅ Scraping completed: ${summary}`])
    },
    onError: (error: any) => {
      const errorMsg = error.response?.data?.detail || error.message
      setLogs((prev) => [...prev, `❌ Scraping failed: ${errorMsg}`])
    },
  })

  const urlScraperMutation = useMutation({
    mutationFn: ({ url, store }: { url: string; store?: string }) => 
      scrapeFromUrl(url, store),
    onSuccess: (response) => {
      const result = response.data
      setLogs((prev) => [
        ...prev, 
        `✅ URL scraping completed!`,
        `  📦 Products found: ${result.products_found}`,
        `  📄 Pages processed: ${result.pages_processed}`,
        `  💾 PDF saved: ${result.pdf_path}`
      ])
      setCatalogueUrl('') // Clear the input
    },
    onError: (error: any) => {
      const errorMsg = error.response?.data?.detail || error.message
      setLogs((prev) => [...prev, `❌ URL scraping failed: ${errorMsg}`])
    },
  })

  const handleRunScraper = (store: string) => {
    setLogs((prev) => [...prev, `🚀 Starting ${store} scraper...`])
    scraperMutation.mutate(store)
  }

  const handleScrapeUrl = () => {
    if (!catalogueUrl.trim()) {
      setLogs((prev) => [...prev, `⚠️ Please enter a URL`])
      return
    }
    
    setLogs((prev) => [...prev, `🚀 Starting URL scraper for: ${catalogueUrl}`])
    urlScraperMutation.mutate({ url: catalogueUrl, store: urlStore })
  }

  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Scrapers</h1>
        <p className="text-gray-600">
          Scrape products from Egyptian grocery stores using Filloffer.com
        </p>
      </div>

      {/* Info Alert */}
      <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
        <AlertCircle className="h-5 w-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-blue-800">
          <p className="font-semibold mb-1">How it works:</p>
          <ol className="list-decimal list-inside space-y-1">
            <li>Enter a specific catalogue URL or use quick scrapers below</li>
            <li>Scraper downloads all catalogue page images</li>
            <li>Combines images into a PDF file</li>
            <li>Extracts text with enhanced OCR (Arabic + English)</li>
            <li>Parses product names and prices with validation</li>
            <li>Saves to database</li>
          </ol>
          <p className="mt-2 text-xs text-blue-600">
            Make sure Tesseract OCR and Poppler are installed!
          </p>
        </div>
      </div>

      {/* URL Scraper Section */}
      <div className="mb-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <LinkIcon className="h-5 w-5 mr-2 text-blue-600" />
          Scrape Specific Catalogue URL
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Enter a filloffer.com catalogue URL to scrape a specific catalogue
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Catalogue URL
            </label>
            <input
              type="url"
              value={catalogueUrl}
              onChange={(e) => setCatalogueUrl(e.target.value)}
              placeholder="https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-starting-from-4-december-8-december/pdf"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-1 text-xs text-gray-500">
              Example URLs:
            </p>
            <ul className="mt-1 text-xs text-gray-500 space-y-1">
              <li>• https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-starting-from-4-december-8-december/pdf</li>
              <li>• https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-Weekend-starting-from-2-december-to-8-december/pdf</li>
            </ul>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Store (optional - auto-detected from URL)
            </label>
            <select
              value={urlStore}
              onChange={(e) => setUrlStore(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="kazyon">Kazyon</option>
              <option value="carrefour">Carrefour</option>
              <option value="metro">Metro</option>
              <option value="lulu">Lulu</option>
            </select>
          </div>
          
          <button
            onClick={handleScrapeUrl}
            disabled={urlScraperMutation.isPending || !catalogueUrl.trim()}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md flex items-center justify-center disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <LinkIcon className="h-5 w-5 mr-2" />
            {urlScraperMutation.isPending ? 'Scraping URL...' : 'Scrape URL'}
          </button>
        </div>
      </div>

      {/* Scraper Cards */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Quick Scrapers</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { id: 'kazyon', name: 'Kazyon', emoji: '🛒', color: 'bg-blue-500 hover:bg-blue-600' },
            { id: 'carrefour', name: 'Carrefour', emoji: '🏪', color: 'bg-red-500 hover:bg-red-600' },
            { id: 'metro', name: 'Metro', emoji: '🏬', color: 'bg-orange-500 hover:bg-orange-600' },
            { id: 'all', name: 'All Stores', emoji: '🌟', color: 'bg-green-500 hover:bg-green-600' },
          ].map((store) => (
            <div key={store.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="text-center mb-4">
                <span className="text-4xl">{store.emoji}</span>
                <h3 className="text-xl font-semibold mt-2">{store.name}</h3>
              </div>
              <button
                onClick={() => handleRunScraper(store.id)}
                disabled={scraperMutation.isPending}
                className={`w-full ${store.color} text-white px-4 py-3 rounded-md flex items-center justify-center disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors`}
              >
                <Play className="h-5 w-5 mr-2" />
                {scraperMutation.isPending ? 'Running...' : 'Run Scraper'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <a
          href="https://www.filloffer.com/markets/Kazyon-Market"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow flex items-center"
        >
          <FileDown className="h-8 w-8 text-blue-500 mr-3" />
          <div>
            <h4 className="font-semibold text-gray-900">Kazyon on Filloffer</h4>
            <p className="text-sm text-gray-600">View source catalogues</p>
          </div>
        </a>
        
        <a
          href="https://www.filloffer.com/egypt"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow flex items-center"
        >
          <FileDown className="h-8 w-8 text-green-500 mr-3" />
          <div>
            <h4 className="font-semibold text-gray-900">All Egypt Offers</h4>
            <p className="text-sm text-gray-600">Browse all stores</p>
          </div>
        </a>

        <a
          href="http://localhost:8000/docs#/scraper/run_scraper_api_v1_scraper_run_post"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow flex items-center"
        >
          <FileDown className="h-8 w-8 text-purple-500 mr-3" />
          <div>
            <h4 className="font-semibold text-gray-900">API Docs</h4>
            <p className="text-sm text-gray-600">Test API directly</p>
          </div>
        </a>
      </div>

      {/* Logs Panel */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Scraping Logs</h2>
          <button
            onClick={clearLogs}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Clear Logs
          </button>
        </div>
        <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500">No logs yet. Run a scraper to see logs here.</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-600">[{new Date().toLocaleTimeString()}]</span> {log}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Troubleshooting */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-semibold text-yellow-900 mb-2">⚠️ Troubleshooting</h3>
        <div className="text-sm text-yellow-800 space-y-1">
          <p><strong>No products found?</strong> Check if PDFs are downloading to <code>data/flyers/</code></p>
          <p><strong>OCR not working?</strong> Verify Tesseract is installed: <code>tesseract --list-langs</code></p>
          <p><strong>PDF conversion fails?</strong> Check Poppler installation: <code>pdftoppm -v</code></p>
          <p><strong>Module errors?</strong> Install dependencies: <code>pip install pdf2image pytesseract pillow</code></p>
        </div>
      </div>
    </div>
  )
}