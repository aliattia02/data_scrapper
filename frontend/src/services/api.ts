import axios from 'axios'
import type { Store, Category, Product, Catalogue, Stats } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Stores
export const getStores = () => api.get<Store[]>('/api/v1/stores')
export const createStore = (data: Partial<Store>) => api.post('/api/v1/stores', data)
export const getStoreBranches = (storeId: string) => 
  api.get(`/api/v1/stores/${storeId}/branches`)

// Categories
export const getCategories = () => api.get<Category[]>('/api/v1/categories')
export const createCategory = (data: Partial<Category>) => 
  api.post('/api/v1/categories', data)

// Products
export const getProducts = (params?: any) => 
  api.get<Product[]>('/api/v1/products', { params })
export const createProduct = (data: Partial<Product>) => 
  api.post('/api/v1/products', data)

// Catalogues
export const getCatalogues = () => api.get<Catalogue[]>('/api/v1/catalogues')
export const createCatalogue = (data: any) => api.post('/api/v1/catalogues', data)
export const uploadCatalogueFile = (catalogueId: number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/api/v1/catalogues/${catalogueId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const processCatalogue = (catalogueId: number) =>
  api.post(`/api/v1/catalogues/${catalogueId}/process`)

// PDF Scraper
export const scrapeCataloguePdf = async (data: {
  url: string
  market_category: string
  market_name: string
  start_date: string
  end_date: string
  latitude?: number
  longitude?: number
}) => api.post('/api/v1/catalogues/scrape-pdf', data)

export const scrapeStoreCatalogues = async (data: {
  store_url: string
  market_category: string
  market_name: string
  latitude?: number
  longitude?: number
}) => api.post('/api/v1/catalogues/scrape-store-catalogues', data)

export const listCatalogues = async (filters?: {
  store?: string
  category?: string
  from_date?: string
  to_date?: string
}) => {
  const params = new URLSearchParams(filters as any)
  return api.get('/api/v1/catalogues/list?' + params.toString())
}

export const renameCatalogue = async (id: number, newName: string) =>
  api.put(`/api/v1/catalogues/${id}/rename`, { new_name: newName })

export const deleteCatalogue = async (id: number) =>
  api.delete(`/api/v1/catalogues/${id}`)

export const getCataloguePdfUrl = (id: number) => 
  `${API_BASE_URL}/api/v1/catalogues/${id}/pdf`

export const getCatalogueThumbnailUrl = (id: number) =>
  `${API_BASE_URL}/api/v1/catalogues/${id}/thumbnail`

// Export
export const exportData = () => api.get('/api/v1/export/app')

// Scrapers
export const runScraper = (store: string) =>
  api.post('/api/v1/scraper/run', { store })

export const scrapeFromUrl = (url: string, store?: string) =>
  api.post('/api/v1/scraper/scrape-url', { url, store })

export const getScrapeJob = (jobId: number) =>
  api.get(`/api/v1/scraper/jobs/${jobId}`)

export const listScrapeJobs = () =>
  api.get('/api/v1/scraper/jobs')

// Upload catalogue
export const uploadCatalogue = (
  files: File[],
  store: string,
  validFrom?: string,
  validUntil?: string
) => {
  const formData = new FormData()
  
  // Append all files
  files.forEach((file) => {
    formData.append('files', file)
  })
  
  // Append store and dates
  formData.append('store', store)
  if (validFrom) {
    formData.append('valid_from', validFrom)
  }
  if (validUntil) {
    formData.append('valid_until', validUntil)
  }
  
  return api.post('/api/v1/scraper/upload-catalogue', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// Stats
export const getStats = () => api.get<Stats>('/stats')
