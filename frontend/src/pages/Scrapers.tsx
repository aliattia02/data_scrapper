import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { runScraper } from '../services/api'
import { Play } from 'lucide-react'

export default function Scrapers() {
  const [logs, setLogs] = useState<string[]>([])

  const scraperMutation = useMutation({
    mutationFn: runScraper,
    onSuccess: (response) => {
      setLogs((prev) => [...prev, `✅ Scraping completed: ${JSON.stringify(response.data)}`])
    },
    onError: (error: any) => {
      setLogs((prev) => [...prev, `❌ Scraping failed: ${error.message}`])
    },
  })

  const handleRunScraper = (store: string) => {
    setLogs((prev) => [...prev, `🚀 Starting ${store} scraper...`])
    scraperMutation.mutate(store)
  }

  return (
    <div className="px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Scrapers</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {['carrefour', 'metro', 'all'].map((store) => (
          <div key={store} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4 capitalize">{store}</h3>
            <button
              onClick={() => handleRunScraper(store)}
              disabled={scraperMutation.isPending}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-md flex items-center justify-center disabled:bg-gray-300"
            >
              <Play className="h-5 w-5 mr-2" />
              Run Scraper
            </button>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Scraping Logs</h2>
        <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500">No logs yet. Run a scraper to see logs here.</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">
                {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
