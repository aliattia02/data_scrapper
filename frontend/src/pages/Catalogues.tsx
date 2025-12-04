import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { getCatalogues, uploadCatalogueFile, processCatalogue } from '../services/api'
import type { Catalogue } from '../types'

export default function Catalogues() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedCatalogue, setSelectedCatalogue] = useState<number | null>(null)

  const { data: catalogues, isLoading, refetch } = useQuery({
    queryKey: ['catalogues'],
    queryFn: async () => {
      const response = await getCatalogues()
      return response.data
    },
  })

  const uploadMutation = useMutation({
    mutationFn: ({ catalogueId, file }: { catalogueId: number; file: File }) =>
      uploadCatalogueFile(catalogueId, file),
    onSuccess: () => {
      refetch()
      setSelectedFile(null)
      alert('File uploaded successfully!')
    },
  })

  const processMutation = useMutation({
    mutationFn: (catalogueId: number) => processCatalogue(catalogueId),
    onSuccess: () => {
      refetch()
      alert('Catalogue processed successfully!')
    },
  })

  const handleUpload = () => {
    if (selectedFile && selectedCatalogue) {
      uploadMutation.mutate({ catalogueId: selectedCatalogue, file: selectedFile })
    }
  }

  if (isLoading) {
    return <div className="text-center py-12">Loading catalogues...</div>
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Catalogues</h1>
        <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md">
          Create Catalogue
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Upload Catalogue File</h2>
        <div className="flex items-center space-x-4">
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="flex-1"
          />
          <select
            value={selectedCatalogue || ''}
            onChange={(e) => setSelectedCatalogue(Number(e.target.value))}
            className="border rounded px-3 py-2"
          >
            <option value="">Select Catalogue</option>
            {catalogues?.map((cat: Catalogue) => (
              <option key={cat.id} value={cat.id}>
                {cat.titleEn || `Catalogue ${cat.id}`}
              </option>
            ))}
          </select>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || !selectedCatalogue}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md disabled:bg-gray-300"
          >
            Upload
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {catalogues?.map((catalogue: Catalogue) => (
          <div key={catalogue.id} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">{catalogue.titleEn || `Catalogue ${catalogue.id}`}</h3>
            <p className="text-sm text-gray-600 mb-4">{catalogue.titleAr}</p>
            <div className="space-y-2 text-sm text-gray-600">
              <p>Status: <span className="font-semibold">{catalogue.status}</span></p>
              <p>Pages: {catalogue.pageCount}</p>
              <p>Offers: {catalogue.offerCount}</p>
              <p>OCR: {catalogue.ocrProcessed ? 'Yes' : 'No'}</p>
            </div>
            {catalogue.status === 'uploaded' && !catalogue.ocrProcessed && (
              <button
                onClick={() => processMutation.mutate(catalogue.id)}
                className="mt-4 w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm"
              >
                Process with OCR
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
