import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { FileText, Download, Eye, MapPin, Filter } from 'lucide-react'
import { listCatalogues, getCataloguePdfUrl, getCatalogueThumbnailUrl } from '../services/api'
import type { Catalogue } from '../types'

export default function Catalogues() {
  const [filterStore, setFilterStore] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [searchText, setSearchText] = useState('')

  const { data: catalogues, isLoading } = useQuery({
    queryKey: ['catalogues-list', filterStore, filterCategory],
    queryFn: async () => {
      const response = await listCatalogues({
        store: filterStore || undefined,
        category: filterCategory || undefined,
      })
      return response.data
    },
  })

  // Filter by search text
  const filteredCatalogues = catalogues?.filter((cat: Catalogue) => {
    if (!searchText) return true
    const search = searchText.toLowerCase()
    return (
      cat.marketName?.toLowerCase().includes(search) ||
      cat.titleEn?.toLowerCase().includes(search) ||
      cat.titleAr?.toLowerCase().includes(search)
    )
  })

  // Get unique stores and categories for filters
  const uniqueStores = [...new Set(catalogues?.map((c: Catalogue) => c.marketName).filter(Boolean))] as string[]
  const uniqueCategories = [...new Set(catalogues?.map((c: Catalogue) => c.marketCategory).filter(Boolean))] as string[]

  if (isLoading) {
    return <div className="text-center py-12">Loading catalogues...</div>
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <FileText className="w-8 h-8" />
          Catalogues
        </h1>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-5 h-5 text-gray-600" />
          <h2 className="font-semibold">Filters</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Store
            </label>
            <select
              value={filterStore}
              onChange={(e) => setFilterStore(e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">All Stores</option>
              {uniqueStores.map((store) => (
                <option key={store} value={store}>
                  {store}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">All Categories</option>
              {uniqueCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Search by store or title..."
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Catalogues Grid */}
      {filteredCatalogues?.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No catalogues found
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredCatalogues?.map((catalogue: Catalogue) => (
            <div key={catalogue.id} className="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition-shadow">
              {/* Thumbnail */}
              <div className="aspect-[3/4] bg-gray-100 relative">
                {catalogue.thumbnailPath ? (
                  <img
                    src={getCatalogueThumbnailUrl(catalogue.id)}
                    alt={catalogue.marketName || 'Catalogue'}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <FileText className="w-16 h-16 text-gray-300" />
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-1">
                  {catalogue.marketName || 'Catalogue'}
                </h3>
                
                {catalogue.marketCategory && (
                  <p className="text-sm text-gray-600 mb-2">
                    {catalogue.marketCategory}
                  </p>
                )}

                {catalogue.validFrom && catalogue.validUntil && (
                  <p className="text-sm text-gray-600 mb-2">
                    {new Date(catalogue.validFrom).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {' '}
                    {new Date(catalogue.validUntil).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </p>
                )}

                {(catalogue.latitude && catalogue.longitude) && (
                  <div className="flex items-center gap-1 text-sm text-gray-600 mb-3">
                    <MapPin className="w-4 h-4" />
                    <span>
                      {catalogue.latitude.toFixed(4)}, {catalogue.longitude.toFixed(4)}
                    </span>
                  </div>
                )}

                <div className="text-sm text-gray-500 mb-3">
                  {catalogue.pageCount} pages
                  {catalogue.fileSize && (
                    <> • {(catalogue.fileSize / 1024).toFixed(0)} KB</>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <a
                    href={getCataloguePdfUrl(catalogue.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-1 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded text-sm"
                  >
                    <Eye className="w-4 h-4" />
                    View
                  </a>
                  
                  <a
                    href={getCataloguePdfUrl(catalogue.id)}
                    download
                    className="flex-1 flex items-center justify-center gap-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
