"use client"

import { useEffect, useMemo, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

export default function ProductsPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [url, setUrl] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [products, setProducts] = useState<any[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editForm, setEditForm] = useState<any>({ name: "", category: "", profit: "", keywords: "" })
  const [loadingList, setLoadingList] = useState(false)
  const [selections, setSelections] = useState<Record<number, string[]>>({})

  const storageKey = useMemo(() => user ? `productSelections_v1:${user.id}` : "productSelections_v1:anon", [user])

  const loadSelections = (prods: any[]) => {
    try {
      const raw = typeof window !== 'undefined' ? window.localStorage.getItem(storageKey) : null
      const parsed: Record<number, string[]> = raw ? JSON.parse(raw) : {}
      const clone: Record<number, string[]> = { ...parsed }
      for (const p of prods) {
        if (clone[p.id] === undefined) {
          const kws = (p.keywords || "").split(',').map((k:string)=>k.trim()).filter(Boolean)
          clone[p.id] = kws
        }
      }
      setSelections(clone)
      if (typeof window !== 'undefined') window.localStorage.setItem(storageKey, JSON.stringify(clone))
    } catch (e) {
      // ignore
    }
  }

  const persistSelections = (next: Record<number, string[]>) => {
    setSelections(next)
    try { if (typeof window !== 'undefined') window.localStorage.setItem(storageKey, JSON.stringify(next)) } catch {}
  }

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  const loadProducts = async () => {
    if (!user) return
    try {
      setLoadingList(true)
      const res = await fetch(`http://localhost:5000/api/auth/products?user_id=${user.id}`)
      if (!res.ok) throw new Error("Failed to load products")
      const data = await res.json()
      const prods = data.products || []
      setProducts(prods)
      loadSelections(prods)
    } catch (e) {
      console.error(e)
      alert("Failed to load products")
    } finally {
      setLoadingList(false)
    }
  }

  useEffect(() => {
    loadProducts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return
    if (!url.trim()) {
      alert("Please paste a product URL")
      return
    }
    setIsSubmitting(true)
    try {
      const res = await fetch("http://localhost:5000/api/auth/products/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id, url })
      })
      if (!res.ok) throw new Error("Failed to ingest product")
      const data = await res.json()
      setUrl("")
      // Prepend new product
      setProducts(prev => [data.product, ...prev])
      alert("Product added!")
    } catch (e) {
      console.error(e)
      alert("Failed to add product")
    } finally {
      setIsSubmitting(false)
    }
  }

  const startEdit = (p: any) => {
    setEditingId(p.id)
    setEditForm({
      name: p.name || "",
      category: p.category || "",
      profit: typeof p.profit === 'number' ? String(p.profit) : "",
      keywords: p.keywords || "",
    })
  }

  const saveEdit = async (id: number) => {
    try {
      const res = await fetch("http://localhost:5000/api/auth/products/" + id, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: editForm.name,
          category: editForm.category,
          profit: editForm.profit ? parseFloat(editForm.profit) : null,
          keywords: editForm.keywords,
        })
      })
      if (!res.ok) throw new Error("Failed to update product")
      const data = await res.json()
      setProducts(prev => prev.map(p => p.id === id ? data.product : p))
      // If keywords changed, reset default selection for this product
      try {
        const kws = (data.product.keywords || "").split(',').map((k:string)=>k.trim()).filter(Boolean)
        const next = { ...selections, [id]: kws }
        persistSelections(next)
      } catch {}
      setEditingId(null)
    } catch (e) {
      console.error(e)
      alert("Failed to save product")
    }
  }

  if (isLoading || !user) {
    return <div className="p-6">Loading...</div>
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-2xl font-bold">Products</h1>
        <p className="text-sm text-muted-foreground">Add a product by pasting its URL. We'll extract name, category and keywords.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex gap-2">
          <input
            type="url"
            placeholder="https://example.com/your-product"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 bg-primary text-primary-foreground rounded disabled:opacity-50"
          >
            {isSubmitting ? "Adding..." : "Add Product"}
          </button>
        </div>
      </form>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Your Products</h2>
          <button onClick={loadProducts} className="text-sm underline disabled:opacity-50" disabled={loadingList}>
            {loadingList ? "Refreshing..." : "Refresh"}
          </button>
        </div>
        {products.length === 0 ? (
          <div className="text-sm text-muted-foreground">No products yet.</div>
        ) : (
          <div className="grid gap-3">
            {products.map((p) => (
              <div key={p.id} className="border rounded p-3 space-y-2">
                {editingId === p.id ? (
                  <div className="space-y-2">
                    <input className="w-full border rounded px-2 py-1" placeholder="Name" value={editForm.name} onChange={(e)=>setEditForm({...editForm, name: e.target.value})} />
                    <input className="w-full border rounded px-2 py-1" placeholder="Category" value={editForm.category} onChange={(e)=>setEditForm({...editForm, category: e.target.value})} />
                    <input className="w-full border rounded px-2 py-1" placeholder="Profit (USD)" value={editForm.profit} onChange={(e)=>setEditForm({...editForm, profit: e.target.value})} />
                    <textarea className="w-full border rounded px-2 py-1" placeholder="Keywords (comma-separated)" value={editForm.keywords} onChange={(e)=>setEditForm({...editForm, keywords: e.target.value})} />
                    <div className="flex gap-2">
                      <button onClick={()=>saveEdit(p.id)} className="px-3 py-1 bg-primary text-primary-foreground rounded">Save</button>
                      <button onClick={()=>setEditingId(null)} className="px-3 py-1 border rounded">Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <div className="font-medium">{p.name || "(Unnamed product)"}</div>
                      {typeof p.profit === 'number' && (
                        <div className="text-sm">Profit: ${p.profit.toFixed(2)}</div>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">{p.category || ""}</div>
                    <a href={p.url} target="_blank" rel="noreferrer" className="text-xs text-blue-600 underline mt-1 inline-block">View product</a>
                    {/* Keyword selection checkboxes */}
                    <div className="mt-2">
                      <div className="text-xs text-muted-foreground mb-1">Select keywords to use for this product:</div>
                      <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto border rounded-md p-3">
                        {(p.keywords ? p.keywords.split(',').map((k: string)=>k.trim()).filter(Boolean) : []).map((k: string, idx: number) => {
                          const checked = (selections[p.id] || []).includes(k)
                          return (
                            <div key={idx} className="flex items-center space-x-2">
                              <Checkbox
                                id={`prod-${p.id}-kw-${idx}`}
                                checked={checked}
                                onCheckedChange={(val) => {
                                  const isChecked = Boolean(val)
                                  const current = selections[p.id] || []
                                  const nextForProduct = isChecked ? Array.from(new Set([...current, k])) : current.filter(x => x !== k)
                                  persistSelections({ ...selections, [p.id]: nextForProduct })
                                }}
                              />
                              <Label htmlFor={`prod-${p.id}-kw-${idx}`} className="flex-1 text-sm cursor-pointer">{k}</Label>
                            </div>
                          )
                        })}
                        {(!p.keywords || p.keywords.trim() === "") && (
                          <div className="text-xs text-muted-foreground">No keywords. Edit the product to add some.</div>
                        )}
                      </div>
                    </div>
                    <div>
                      <button onClick={()=>startEdit(p)} className="text-xs underline">Edit</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}


