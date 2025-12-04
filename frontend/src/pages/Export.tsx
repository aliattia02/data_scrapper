import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { exportData } from '../services/api'
import { Download } from 'lucide-react'

export default function Export() {
  const [isExporting, setIsExporting] = useState(false)

  const exportMutation = useMutation({
    mutationFn: exportData,
    onSuccess: (response) => {
      const blob = new Blob([JSON.stringify(response.data, null, 2)], {
        type: 'application/json',
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `export-${new Date().toISOString()}.json`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      setIsExporting(false)
      alert('Data exported successfully!')
    },
    onError: () => {
      setIsExporting(false)
      alert('Export failed!')
    },
  })

  const handleExport = () => {
    setIsExporting(true)
    exportMutation.mutate()
  }

  return (
    <div className="px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Export Data</h1>

      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow p-8">
          <div className="text-center">
            <Download className="h-16 w-16 text-blue-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold mb-4">Export for Mobile App</h2>
            <p className="text-gray-600 mb-6">
              Download all products, stores, and categories in JSON format
              for the OfferCatalog mobile app.
            </p>
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-3 rounded-md text-lg disabled:bg-gray-300"
            >
              {isExporting ? 'Exporting...' : 'Export Now'}
            </button>
          </div>
        </div>

        <div className="mt-8 bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Export Format</h3>
          <pre className="bg-white p-4 rounded border text-sm overflow-x-auto">
{`{
  "metadata": {
    "exported_at": "2024-12-04T12:00:00Z",
    "total_products": 150,
    "version": "1.0.0"
  },
  "products": [...]
}`}
          </pre>
        </div>
      </div>
    </div>
  )
}
