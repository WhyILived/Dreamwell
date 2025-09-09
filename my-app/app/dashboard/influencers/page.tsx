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
      console.log('DEBUG: Loaded products:', list)
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

      // Process products in parallel with a 2s stagger between starts to avoid API rate limits
      const outputs = await Promise.all(
        products.map((p, idx) =>
          new Promise<{ id: number; data: any }>((resolve) => {
            setTimeout(async () => {
              // Use saved selections if present; otherwise fall back to all product keywords
              const baseKeywords = (p.keywords || "").split(',').map(k => k.trim()).filter(Boolean)
              const selectedForProduct = (storedSelections[p.id] && Array.isArray(storedSelections[p.id]) ? storedSelections[p.id] : baseKeywords)
              const unique = Array.from(new Set(selectedForProduct)).filter(Boolean)
              console.log(`DEBUG: [P${p.id}] Base keywords:`, baseKeywords, 'Selected:', selectedForProduct, 'Unique:', unique)
              console.log(`DEBUG: [P${p.id}] will search for keywords:`, unique)

              if (unique.length === 0) {
                console.log(`DEBUG: [P${p.id}] has no keywords, returning empty result`)
                resolve({ id: p.id, data: { influencers: [], averages: { avg_views: 0, avg_score: 0 } } })
                return
              }

              try {
                console.log(`DEBUG: [P${p.id}] Searching (stagger idx ${idx})`)
                const res = await fetch('http://localhost:5000/api/auth/search-influencers', {
                  method: 'POST', headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ keywords: unique, user_id: user?.id, product_id: p.id })
                })
                if (!res.ok) throw new Error('Search failed')
                const data = await res.json()
                resolve({ id: p.id, data })
              } catch (error) {
                console.error(`DEBUG: [P${p.id}] Error searching:`, error)
                resolve({ id: p.id, data: { influencers: [], averages: { avg_views: 0, avg_score: 0 } } })
              }
            }, idx * 2000) // 2s between each product start
          })
        )
      )
      const map: Record<number, { results: any[]; averages: any }> = {}
      console.log('DEBUG: Search outputs:', outputs)
      for (const o of outputs) {
        const influencers = o.data.influencers || []
        console.log(`DEBUG: Product ${o.id} has ${influencers.length} influencers`)
        // Sort influencers by score (highest first)
        const sortedInfluencers = influencers.sort((a: any, b: any) => {
          const scoreA = typeof a.score === 'number' ? a.score : 0
          const scoreB = typeof b.score === 'number' ? b.score : 0
          return scoreB - scoreA
        })
        map[o.id] = { results: sortedInfluencers, averages: o.data.averages || { avg_views: 0, avg_score: 0 } }
      }
      console.log('DEBUG: Final results map:', map)
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

      {/* Results per product (below the two-column layout) */}
      {Object.keys(resultsByProduct).length > 0 && (
        <div className="mt-6 space-y-6">
          {products.map(p => {
            const entry = resultsByProduct[p.id]
            console.log(`DEBUG: Rendering product ${p.id} (${p.name}), has entry:`, !!entry)
            if (!entry || !entry.results || entry.results.length === 0) {
              console.log(`DEBUG: Product ${p.id} has no results, showing empty state`)
              return (
                <div key={p.id} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-semibold">Results for: {p.name || '(Unnamed product)'}</h3>
                    <div className="text-xs text-muted-foreground">No results</div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg text-center text-muted-foreground">
                    No influencers found for this product
                  </div>
                </div>
              )
            }
            return (
              <div key={p.id} className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold">Results for: {p.name || '(Unnamed product)'}</h3>
                </div>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {entry.results.map((inf: any, i: number) => (
                    <div key={i} className="border rounded p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold text-primary">#{i + 1}</span>
                          <a href={inf.channel_id ? `https://www.youtube.com/channel/${inf.channel_id}` : (inf.url || '#')} target="_blank" rel="noreferrer" className="font-medium hover:underline">{inf.title}</a>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="text-sm font-bold text-green-600">{typeof inf.score === 'number' ? inf.score.toFixed(1) : inf.score}</div>
                          <div className="text-xs text-muted-foreground">{inf.country || 'Unknown'}</div>
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">👥 {formatCompactNumber(inf.subs)} · 👁️ {formatCompactNumber(inf.avg_recent_views)}</div>
                      {inf.score_components && (
                        <div className="mt-2 text-xs text-muted-foreground">
                          <div className="flex flex-wrap gap-1">
                            <span>Values: {inf.score_components.values}</span>
                            <span>|</span>
                            <span>Cultural: {inf.score_components.cultural}</span>
                            <span>|</span>
                            <span>CPM: {inf.score_components.cpm}</span>
                            <span>|</span>
                            <span>RPM: {inf.score_components.rpm}</span>
                            <span>|</span>
                            <span>Engagement: {inf.score_components.views_to_subs}</span>
                          </div>
                          {inf.reasoning && Object.keys(inf.reasoning).length > 0 && (
                            <div className="mt-2 p-2 bg-muted/50 rounded text-xs">
                              <div className="font-medium mb-1">AI Analysis:</div>
                              {['values', 'cultural', 'cpm', 'rpm', 'engagement'].map((key) => (
                                inf.reasoning[key] && (
                                  <div key={key} className="mb-1">
                                    <span className="font-medium">
                                      {key === 'cpm' ? 'CPM' : key === 'rpm' ? 'RPM' : key.charAt(0).toUpperCase() + key.slice(1)}:
                                    </span> {String(inf.reasoning[key])}
                                  </div>
                                )
                              ))}
                            </div>
                          )}
                        </div>
                      )}
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


