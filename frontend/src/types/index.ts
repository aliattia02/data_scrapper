export interface Store {
  id: string
  nameAr: string
  nameEn: string
  logoUrl?: string
  website?: string
  active: boolean
  branchCount: number
}

export interface Branch {
  id: number
  storeId: string
  nameAr: string
  nameEn?: string
  addressAr?: string
  addressEn?: string
  city?: string
  governorate?: string
  phone?: string
  active: boolean
}

export interface Category {
  id: string
  nameAr: string
  nameEn: string
  icon?: string
  sortOrder: number
  active: boolean
}

export interface Product {
  id: number
  storeProductId: string
  store: string
  nameAr: string
  nameEn?: string
  brand?: string
  categoryAr?: string
  categoryEn?: string
  price: number
  originalPrice?: number
  discountPercentage?: number
  currency: string
  size?: string
  inStock: boolean
  imageUrl?: string
  url?: string
  source: string
  scrapedAt?: string
}

export interface Catalogue {
  id: number
  storeId: string
  titleAr?: string
  titleEn?: string
  validFrom?: string
  validUntil?: string
  status: string
  ocrProcessed: boolean
  fileType?: string
  pageCount: number
  offerCount: number
  createdAt?: string
  processedAt?: string
}

export interface Stats {
  total_products: number
  total_stores: number
  total_categories: number
  average_price: number
  products_on_sale: number
  last_updated: string
}
