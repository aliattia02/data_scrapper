import { useQuery } from '@tanstack/react-query'
import { getStats, getProducts, getStores } from '../services/api'
import { Package, Store, Tag, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await getStats()
      return response.data
    },
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<Package className="h-8 w-8 text-blue-500" />}
          title="Total Products"
          value={stats?.total_products || 0}
          color="blue"
        />
        <StatCard
          icon={<Store className="h-8 w-8 text-green-500" />}
          title="Total Stores"
          value={stats?.total_stores || 0}
          color="green"
        />
        <StatCard
          icon={<Tag className="h-8 w-8 text-purple-500" />}
          title="Categories"
          value={stats?.total_categories || 0}
          color="purple"
        />
        <StatCard
          icon={<TrendingUp className="h-8 w-8 text-red-500" />}
          title="Products on Sale"
          value={stats?.products_on_sale || 0}
          color="red"
        />
      </div>

      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
        <div className="space-y-2">
          <p className="text-gray-600">
            Average Price: <span className="font-semibold">{stats?.average_price?.toFixed(2)} EGP</span>
          </p>
          <p className="text-gray-600">
            Last Updated: <span className="font-semibold">
              {stats?.last_updated ? new Date(stats.last_updated).toLocaleString() : 'N/A'}
            </span>
          </p>
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, title, value, color }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 bg-${color}-100 rounded-md p-3`}>
          {icon}
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-3xl font-semibold text-gray-900">{value}</dd>
          </dl>
        </div>
      </div>
    </div>
  )
}
