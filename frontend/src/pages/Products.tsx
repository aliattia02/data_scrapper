import { useQuery } from '@tanstack/react-query'
import { getProducts } from '../services/api'
import type { Product } from '../types'

export default function Products() {
  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await getProducts({ limit: 50 })
      return response.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading products...</div>
  }

  return (
    <div className="px-4 py-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Products</h1>
        <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md">
          Add Product
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products?.map((product: Product) => (
          <div key={product.id} className="bg-white rounded-lg shadow p-6">
            {product.imageUrl && (
              <img src={product.imageUrl} alt={product.nameEn || product.nameAr} 
                className="w-full h-48 object-cover rounded mb-4" />
            )}
            <h3 className="text-lg font-semibold mb-2">{product.nameEn || product.nameAr}</h3>
            <p className="text-sm text-gray-600 mb-2">{product.nameAr}</p>
            <div className="flex items-center justify-between mt-4">
              <div>
                <p className="text-2xl font-bold text-blue-600">{product.price} {product.currency}</p>
                {product.originalPrice && (
                  <p className="text-sm text-gray-500 line-through">{product.originalPrice} {product.currency}</p>
                )}
              </div>
              {product.discountPercentage && (
                <span className="bg-red-100 text-red-800 text-xs font-semibold px-2 py-1 rounded">
                  -{product.discountPercentage}%
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Store: {product.store} | Category: {product.categoryEn}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
