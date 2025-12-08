import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { runScraper } from '../services/api'
import { Play, FileDown, AlertCircle } from 'lucide-react'

export default function Scrapers() {
  const [logs, setLogs] = useState<string[]>([])

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

  const handleRunScraper = (store: string) => {
    setLogs((prev) => [...prev, `🚀 Starting ${store} scraper...`])
    scraperMutation.mutate(store)
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
            <li>Scraper finds latest catalogues on Filloffer.com</li>
            <li>Downloads PDF files</li>
            <li>Converts to images and extracts text with OCR (Arabic + English)</li>
            <li>Parses product names and prices</li>
            <li>Saves to database</li>
          </ol>
          <p className="mt-2 text-xs text-blue-600">
            Make sure Tesseract OCR and Poppler are installed!
          </p>
        </div>
      </div>

      {/* Scraper Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { id: 'kazyon', name: 'Kazyon', emoji: '🛒', color: 'blue' },
          { id: 'carrefour', name: 'Carrefour', emoji: '🏪', color: 'red' },
          { id: 'metro', name: 'Metro', emoji: '🏬', color: 'orange' },
          { id: 'all', name: 'All Stores', emoji: '🌟', color: 'green' },
        ].map((store) => (
          <div key={store.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
            <div className="text-center mb-4">
              <span className="text-4xl">{store.emoji}</span>
              <h3 className="text-xl font-semibold mt-2">{store.name}</h3>
            </div>
            <button
              onClick={() => handleRunScraper(store.id)}
              disabled={scraperMutation.isPending}
              className={`w-full bg-${store.color}-500 hover:bg-${store.color}-600 text-white px-4 py-3 rounded-md flex items-center justify-center disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors`}
              style={{
                backgroundColor: scraperMutation.isPending ? '#d1d5db' : undefined
              }}
            >
              <Play className="h-5 w-5 mr-2" />
              {scraperMutation.isPending ? 'Running...' : 'Run Scraper'}
            </button>
          </div>
        ))}
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