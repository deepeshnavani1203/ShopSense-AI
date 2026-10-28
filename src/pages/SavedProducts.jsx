import { useEffect, useState } from 'react'
import { Bookmark, Trash2, X } from 'lucide-react'
import { api } from '../services/api'

function ProductModal({ product, onClose }) {
  if (!product) return null
  const attrs = product.attributes || {}
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="relative max-h-[90vh] overflow-y-auto max-w-lg w-full rounded-2xl bg-white p-6 shadow-2xl">
        <button onClick={onClose} className="absolute right-4 top-4 rounded-full bg-slate-100 p-1.5 text-slate-500 hover:bg-slate-200">
          <X className="h-4 w-4" />
        </button>
        <img src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'}
          alt={product.name} className="h-52 w-full rounded-xl object-cover mb-4" />
        <div className="flex items-start justify-between gap-2 mb-2">
          <div>
            <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">{product.category}</span>
            <h2 className="text-xl font-bold text-slate-900">{product.name}</h2>
            <p className="text-sm text-slate-500">{product.brand}</p>
          </div>
          <p className="text-xl font-black text-slate-900 flex-shrink-0">₹{product.price?.toLocaleString('en-IN')}</p>
        </div>
        <p className="text-sm text-slate-600 leading-6">{product.description}</p>

        {Object.keys(attrs).length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">Key Specs</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(attrs).map(([k, v]) => (
                <div key={k} className="rounded-xl bg-slate-50 px-3 py-2">
                  <p className="text-[10px] text-slate-400 capitalize">{k.replace(/_/g, ' ')}</p>
                  <p className="text-sm font-semibold text-slate-800">{String(v)}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {(product.tags || []).length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            {product.tags.map(t => (
              <span key={t} className="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700">{t}</span>
            ))}
          </div>
        )}

        <div className="mt-5 flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2.5">
          <span className="text-sm text-slate-500">Stock</span>
          <span className={`text-sm font-semibold ${product.stock_status === 'in_stock' ? 'text-emerald-600' : 'text-amber-600'}`}>
            {product.stock_status === 'in_stock' ? '✓ In Stock' : '⚡ Limited'}
          </span>
        </div>

        <button onClick={onClose} className="mt-4 w-full rounded-full border border-slate-200 bg-slate-50 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">
          Close
        </button>
      </div>
    </div>
  )
}

export default function SavedProducts() {
  const [savedIds, setSavedIds] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [modalProduct, setModalProduct] = useState(null)

  useEffect(() => {
    api.getSavedProducts()
      .then(d => setSavedIds(d.items || []))
      .catch(() => setSavedIds([]))
      .finally(() => setLoading(false))
  }, [])

  // Fetch full product details for each saved ID
  useEffect(() => {
    if (!savedIds.length) { setProducts([]); return }
    Promise.all(
      savedIds.map(id => api.getProduct(id).catch(() => null))
    ).then(results => setProducts(results.filter(Boolean)))
  }, [savedIds])

  const handleRemove = async (productId) => {
    try {
      await api.removeSavedProduct(productId)
      setSavedIds(prev => prev.filter(id => id !== productId))
      setProducts(prev => prev.filter(p => p.product_id !== productId))
    } catch {}
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <ProductModal product={modalProduct} onClose={() => setModalProduct(null)} />

      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Your shortlist</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900">Saved Products</h1>
          {products.length > 0 && <p className="text-sm text-slate-500 mt-1">{products.length} item{products.length !== 1 ? 's' : ''} saved</p>}
        </div>
        <Bookmark className="h-8 w-8 text-violet-500" />
      </div>

      {loading && (
        <div className="text-center py-16 text-sm text-slate-400">Loading saved products...</div>
      )}

      {!loading && products.length === 0 && (
        <div className="rounded-[2rem] border border-dashed border-slate-200 bg-white p-16 text-center shadow-sm">
          <Bookmark className="h-10 w-10 text-slate-200 mx-auto mb-3" />
          <p className="text-slate-500 font-medium">No saved products yet.</p>
          <p className="text-sm text-slate-400 mt-1">Search for products in Discover and click 💾 Save.</p>
          <a href="/discover" className="mt-5 inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 transition">
            Go to Discover →
          </a>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map(product => (
          <article key={product.product_id} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-md transition">
            <div className="relative">
              <img src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'}
                alt={product.name} className="h-44 w-full object-cover" />
              <button type="button" onClick={() => handleRemove(product.product_id)}
                className="absolute top-2 right-2 rounded-full bg-white/90 p-1.5 text-slate-400 hover:text-red-500 shadow transition">
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="p-4">
              <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-400">{product.category}</span>
              <h3 className="text-base font-bold text-slate-900 leading-tight mt-0.5">{product.name}</h3>
              <p className="text-xs text-slate-500">{product.brand}</p>
              <p className="mt-1 text-lg font-black text-slate-900">₹{product.price?.toLocaleString('en-IN')}</p>

              {/* Key attributes */}
              {product.attributes && Object.keys(product.attributes).length > 0 && (
                <div className="mt-2 space-y-1">
                  {Object.entries(product.attributes).slice(0, 3).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-xs">
                      <span className="text-slate-400 capitalize">{k.replace(/_/g, ' ')}</span>
                      <span className="font-semibold text-slate-700">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-3 flex items-center justify-between gap-2">
                <span className={`text-xs font-semibold ${product.stock_status === 'in_stock' ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {product.stock_status === 'in_stock' ? '✓ In Stock' : '⚡ Limited'}
                </span>
                <button type="button" onClick={() => setModalProduct(product)}
                  className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white hover:bg-slate-700 transition">
                  View details
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
