"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { formatCompactNumber } from "@/lib/utils"
// Keyword selection managed on Products page; this page reads selections only

type Product = {
  id: number
  url: string
  name?: string | null
  category?: string | null
  profit?: number | null
  keywords?: string | null
}

export default function InfluencersPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  // Products + selection state
  const [products, setProducts] = useState<Product[]>([])
  const [loadingProducts, setLoadingProducts] = useState(false)
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null)
  const selectedProduct = useMemo(() => products.find(p => p.id === selectedProductId) || null, [products, selectedProductId])

  // Editing/selection moved to Products page

  // Search state
  const [loading, setLoading] = useState(false)
  // Results by product id
  const [resultsByProduct, setResultsByProduct] = useState<Record<number, { results: any[]; averages: any }>>({})
  const resultsStorageKey = useMemo(() => user ? `influencerResults_v1:${user.id}` : 'influencerResults_v1:anon', [user])

  // Clear any stale cached results on mount/user change
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(resultsStorageKey)
      }
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resultsStorageKey])

  useEffect(() => {
    if (!isLoading && !user) router.push("/login")
  }, [user, isLoading, router])

  const loadProducts = async () => {
    if (!user) return
    setLoadingProducts(true)
    try {
      const res = await fetch(`http://localhost:5000/api/auth/products?user_id=${user.id}`)
      if (!res.ok) throw new Error("Failed to load products")
      const data = await res.json()
      const list: Product[] = data.products || []
      setProducts(list)
      if (list.length > 0 && selectedProductId === null) {
        setSelectedProductId(list[0].id)
      }
    } catch (e) {
      console.error(e)
      alert("Failed to load products")
    } finally {
      setLoadingProducts(false)
    }
  }

  useEffect(() => {
    loadProducts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  // No local selection/editing here

  // Not editing on this page

  const search = async () => {
    if (products.length === 0) {
      alert("No products to search")
      return
    }
    setLoading(true)
    try {
      // Load keyword selections saved on the Products page
      let storedSelections: Record<number, string[]> = {}
      try {
        const key = user ? `productSelections_v1:${user.id}` : 'productSelections_v1:anon'
        const raw = typeof window !== 'undefined' ? window.localStorage.getItem(key) : null
        storedSelections = raw ? JSON.parse(raw) : {}
      } catch {}

      const tasks = products.map(async (p) => {
        // Use saved selections if present; otherwise fall back to all product keywords
        const baseKeywords = (p.keywords || "").split(',').map(k => k.trim()).filter(Boolean)
        const selectedForProduct = (storedSelections[p.id] && Array.isArray(storedSelections[p.id]) ? storedSelections[p.id] : baseKeywords)
        const unique = Array.from(new Set(selectedForProduct)).filter(Boolean)
        if (unique.length === 0) {
          return { id: p.id, data: { influencers: [], averages: { avg_views: 0, avg_score: 0 } } }
        }
        const res = await fetch('http://localhost:5000/api/auth/search-influencers', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ keywords: unique, user_id: user?.id, product_id: p.id })
        })
        if (!res.ok) throw new Error('Search failed')
        const data = await res.json()
        return { id: p.id, data }
      })
      const outputs = await Promise.all(tasks)
      const map: Record<number, { results: any[]; averages: any }> = {}
      for (const o of outputs) {
        map[o.id] = { results: o.data.influencers || [], averages: o.data.averages || { avg_views: 0, avg_score: 0 } }
      }
      setResultsByProduct(map)
      // Do not persist results to localStorage to avoid stale data after DB resets
    } catch (e) {
      console.error(e)
      alert('Search failed')
    } finally {
      setLoading(false)
    }
  }

  if (isLoading || !user) return <div className="p-6">Loading...</div>

  return (
    <div className="p-4 md:p-6">
      {/* Header with centered Find Influencers */}
      <div className="flex items-center justify-center mb-4">
        <button onClick={search} disabled={loading} className="px-4 py-2 bg-primary text-primary-foreground rounded disabled:opacity-50">
          {loading ? 'Finding influencers…' : 'Find Influencers'}
        </button>
      </div>

      <div className="flex items-center justify-center">
        <button onClick={loadProducts} className="text-xs underline disabled:opacity-50" disabled={loadingProducts}>{loadingProducts ? 'Refreshing…' : 'Refresh products'}</button>
      </div>
      {/* Results per product (below the two-column layout) */}
      {Object.keys(resultsByProduct).length > 0 && (
        <div className="mt-6 space-y-6">
          {products.map(p => {
            const entry = resultsByProduct[p.id]
            if (!entry) return null
            return (
              <div key={p.id} className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold">Results for: {p.name || '(Unnamed product)'}</h3>
                  <div className="text-xs text-muted-foreground">{(entry.averages?.avg_score ?? 0).toFixed ? (entry.averages.avg_score as number).toFixed(1) : entry.averages?.avg_score}</div>
                </div>
                <div className="grid grid-cols-2 gap-4 p-4 bg-muted rounded-lg">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{formatCompactNumber(entry.averages?.avg_views || 0)}</div>
                    <div className="text-sm text-muted-foreground">Avg Views</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{(entry.averages?.avg_score as any)?.toFixed ? (entry.averages?.avg_score as any).toFixed(1) : entry.averages?.avg_score || 0}</div>
                    <div className="text-sm text-muted-foreground">Avg Score</div>
                  </div>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {entry.results.map((inf: any, i: number) => (
                    <div key={i} className="border rounded p-3">
                      <div className="flex items-center justify-between">
                        <a href={inf.url || '#'} target="_blank" rel="noreferrer" className="font-medium hover:underline">{inf.title}</a>
                        <div className="text-xs text-muted-foreground">{inf.country || 'Unknown,Country'}</div>
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">👥 {formatCompactNumber(inf.subs)} · 👁️ {formatCompactNumber(inf.avg_recent_views)} · ⭐ {inf.score}</div>
                      {inf.recent_videos && inf.recent_videos.length>0 && (
                        <div className="mt-2 text-xs">
                          Recent: {inf.recent_videos.slice(0,2).map((v:any)=>v.title).join(' · ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}


