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
