import { useQuery } from '@tanstack/react-query'
import { getStores } from '../services/api'
import type { Store } from '../types'

export default function Stores() {
  const { data: stores, isLoading } = useQuery({
    queryKey: ['stores'],
    queryFn: async () => {
      const response = await getStores()
      return response.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading stores...</div>
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Stores</h1>
        <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md">
          Add Store
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stores?.map((store: Store) => (
          <div key={store.id} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-2">{store.nameEn}</h3>
            <p className="text-gray-600 mb-4">{store.nameAr}</p>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">{store.branchCount} branches</span>
              <span className={`px-2 py-1 rounded text-xs ${
                store.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              }`}>
                {store.active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
