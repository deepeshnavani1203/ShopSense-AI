import { useEffect, useState } from 'react'
import { ShoppingBag, Sparkles, Swords, Trash2, Trophy, X } from 'lucide-react'
import { api } from '../services/api'
import { useCart } from '../context/CartContext'

export default function Compare({ selectedCompare, setSelectedCompare }) {
  const { addToCart, setActiveBattleProducts } = useCart()
  const [products, setProducts] = useState([])
  const [bestPick, setBestPick] = useState(null)
  const [loadingBest, setLoadingBest] = useState(false)
  const [activeCategory, setActiveCategory] = useState('all')

  useEffect(() => {
    if (!selectedCompare.length) { setProducts([]); setBestPick(null); return }
    const ids = selectedCompare.map(e => typeof e === 'string' ? e : e.product_id)
    api.compareProducts(ids)
      .then(payload => setProducts(payload.items || []))
      .catch(() => setProducts([]))
  }, [selectedCompare])

  const fetchBestPick = async () => {
    setLoadingBest(true)
    try {
      const ids = selectedCompare.map(e => typeof e === 'string' ? e : e.product_id)
      const result = await api.bestPick(ids)
      setBestPick(result)
    } catch { setBestPick(null) }
    finally { setLoadingBest(false) }
  }

  const removeProduct = (productId) => {
    setSelectedCompare(prev => prev.filter(e => (typeof e === 'string' ? e : e.product_id) !== productId))
    setProducts(prev => prev.filter(p => p.product_id !== productId))
    if (bestPick?.product_id === productId) setBestPick(null)
  }

  // Group by category
  const categories = ['all', ...Array.from(new Set(products.map(p => p.category))).sort()]
  const visibleProducts = activeCategory === 'all' ? products : products.filter(p => p.category === activeCategory)

  if (!selectedCompare.length) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center">
        <div className="rounded-[2rem] border border-dashed border-slate-200 bg-white p-16 shadow-sm">
          <Sparkles className="h-10 w-10 text-violet-300 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-700 mb-2">Nothing to compare yet</h2>
          <p className="text-sm text-slate-400">Go to Discover, search for products, and click <strong>+ Compare</strong> on each one.</p>
          <a href="/discover" className="mt-6 inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 transition">
            Go to Discover →
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Comparison dashboard</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900">Compare products</h1>
          <p className="text-sm text-slate-500 mt-1">{products.length} product{products.length !== 1 ? 's' : ''} selected</p>
        </div>
        <div className="flex gap-3">
          <button type="button" onClick={fetchBestPick} disabled={loadingBest || products.length < 2}
            className="inline-flex items-center gap-2 rounded-full bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-violet-700 transition disabled:opacity-40">
            <Trophy className="h-4 w-4" />
            {loadingBest ? 'Analysing...' : 'Best pick for me'}
          </button>
          <button type="button" onClick={() => { setSelectedCompare([]); setProducts([]); setBestPick(null) }}
            className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 transition">
            <Trash2 className="h-4 w-4" /> Clear all
          </button>
        </div>
      </div>

      {/* Best Pick Banner */}
      {bestPick && (
        <div className="mb-6 rounded-2xl border border-violet-200 bg-gradient-to-r from-violet-50 to-indigo-50 p-5">
          <div className="flex items-start gap-3">
            <Trophy className="h-6 w-6 text-violet-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-violet-500 mb-0.5">AI Best Pick</p>
              <h3 className="text-lg font-bold text-violet-900">{bestPick.name}</h3>
              <p className="text-sm text-violet-700 mt-1">{bestPick.reason}</p>
              {bestPick.confidence && (
                <p className="text-xs text-violet-500 mt-1">Confidence: {(bestPick.confidence * 100).toFixed(0)}%</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Category filter tabs */}
      {categories.length > 2 && (
        <div className="mb-6 flex flex-wrap gap-2">
          {categories.map(cat => (
            <button key={cat} type="button" onClick={() => setActiveCategory(cat)}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                activeCategory === cat
                  ? 'bg-slate-900 text-white'
                  : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              }`}>
              {cat === 'all' ? `All (${products.length})` : `${cat} (${products.filter(p => p.category === cat).length})`}
            </button>
          ))}
        </div>
      )}

      {/* Product grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {visibleProducts.map(product => {
          const entry = selectedCompare.find(e => (typeof e === 'string' ? e : e.product_id) === product.product_id)
          const fitScore = typeof entry?.fit_score === 'number' ? entry.fit_score : null
          const breakdown = entry?.match_summary || null
          const isBest = bestPick?.product_id === product.product_id

          return (
            <article key={product.product_id}
              className={`relative overflow-hidden rounded-2xl border bg-white shadow-sm transition hover:shadow-md ${
                isBest ? 'border-violet-400 ring-2 ring-violet-400' : 'border-slate-200'
              }`}>
              {isBest && (
                <div className="absolute top-0 left-0 right-0 bg-violet-600 py-1 text-center text-[10px] font-bold uppercase tracking-widest text-white z-10">
                  🏆 Best Pick
                </div>
              )}
              {/* Remove button */}
              <button type="button" onClick={() => removeProduct(product.product_id)}
                className="absolute top-2 right-2 z-10 rounded-full bg-white/80 p-1 text-slate-400 hover:text-red-500 shadow">
                <X className="h-3.5 w-3.5" />
              </button>

              <img src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'}
                alt={product.name} className={`h-44 w-full object-cover ${isBest ? 'mt-5' : ''}`} />

              <div className="p-4">
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">{product.category}</span>
                <h2 className="text-base font-bold text-slate-900 leading-tight mt-0.5">{product.name}</h2>
                <p className="text-xs text-slate-500">{product.brand}</p>

                {/* Rating */}
                <div className="mt-2 flex items-center gap-1">
                  {[1,2,3,4,5].map(s => (
                    <span key={s} className={`text-xs ${s <= Math.round(product.rating || 4) ? 'text-amber-400' : 'text-slate-200'}`}>★</span>
                  ))}
                  <span className="text-[10px] text-slate-400 ml-1">{product.rating || '—'}</span>
                </div>

                {/* Key Specs from attributes */}
                {product.attributes && Object.keys(product.attributes).length > 0 && (
                  <div className="mt-3 space-y-1">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">Specs</p>
                    {Object.entries(product.attributes).slice(0, 4).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between rounded-lg bg-slate-50 px-2.5 py-1.5">
                        <span className="text-[11px] text-slate-500 capitalize">{k.replace(/_/g, ' ')}</span>
                        <span className="text-[11px] font-semibold text-slate-800">{String(v)}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Price + Fit */}
                <div className="mt-3 space-y-1">
                  <div className="flex items-center justify-between rounded-lg bg-slate-50 px-2.5 py-1.5">
                    <span className="text-[11px] text-slate-500">Price</span>
                    <span className="text-sm font-black text-slate-900">₹{product.price?.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex items-center justify-between rounded-lg bg-slate-50 px-2.5 py-1.5">
                    <span className="text-[11px] text-slate-500">Fit score</span>
                    <span className="text-sm font-bold text-violet-700">
                      {fitScore != null ? `${(fitScore * 100).toFixed(0)} / 100` : `${Math.round((product.rating || 4) * 18)} / 100`}
                    </span>
                  </div>
                  <div className="flex items-center justify-between rounded-lg bg-slate-50 px-2.5 py-1.5">
                    <span className="text-[11px] text-slate-500">Stock</span>
                    <span className={`text-[11px] font-semibold ${product.stock_status === 'in_stock' ? 'text-emerald-600' : 'text-amber-600'}`}>
                      {product.stock_status === 'in_stock' ? '✓ In Stock' : '⚡ Limited'}
                    </span>
                  </div>
                </div>

                {/* Score breakdown bars */}
                {breakdown && (
                  <div className="mt-3">
                    <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 mb-1">Score breakdown</p>
                    {Object.entries(breakdown).map(([k, v]) => {
                      const pct = typeof v === 'number' ? v : 0
                      return (
                        <div key={k} className="mb-1">
                          <div className="flex justify-between text-[10px] text-slate-400 mb-0.5">
                            <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                            <span>{pct.toFixed(0)}</span>
                          </div>
                          <div className="h-1 rounded-full bg-slate-100">
                            <div className="h-1 rounded-full bg-violet-400" style={{ width: `${Math.min(pct, 100)}%` }} />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}

                {/* Why it stands out */}
                <div className="mt-3 rounded-xl bg-violet-50 p-3">
                  <p className="text-[10px] font-semibold text-violet-500 uppercase mb-1 flex items-center gap-1">
                    <Sparkles className="h-3 w-3" /> Why it stands out
                  </p>
                  <p className="text-xs text-violet-800 line-clamp-3">{product.description}</p>
                </div>

                {/* Compare Card Actions */}
                <div className="mt-4 flex gap-2">
                  <button
                    type="button"
                    onClick={() => addToCart(product, 1)}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl bg-slate-900 py-2.5 text-xs font-bold text-white hover:bg-slate-800 transition"
                  >
                    <ShoppingBag className="h-3.5 w-3.5" /> Add to Cart
                  </button>
                  {products.length >= 2 && (
                    <button
                      type="button"
                      onClick={() => {
                        const other = products.find(p => p.product_id !== product.product_id)
                        if (other) setActiveBattleProducts([product, other])
                      }}
                      className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 text-xs font-bold text-amber-800 hover:bg-amber-100 transition"
                      title="Battle with another contender"
                    >
                      <Swords className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </article>
          )
        })}
      </div>
    </div>
  )
}
