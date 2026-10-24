import { useEffect, useState } from 'react'
import { ArrowRightLeft, CircleDollarSign, Sparkles } from 'lucide-react'
import { api } from '../services/api'

export default function Compare({ selectedCompare }) {
  const [products, setProducts] = useState([])

  useEffect(() => {
    if (!selectedCompare.length) {
      setProducts([])
      return
    }

    api
      .compareProducts(selectedCompare)
      .then((payload) => setProducts(payload.items || []))
      .catch(() => setProducts([]))
  }, [selectedCompare])

  if (!products.length) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-center text-slate-500">
        Select up to three products from the discovery workspace to compare them side by side.
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Comparison dashboard</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-900">Compare the strongest options</h1>
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        {products.map((product) => (
          <article key={product.product_id} className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm">
            <img src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'} alt={product.name} className="h-52 w-full object-cover" />
            <div className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{product.category}</p>
                  <h2 className="mt-2 text-xl font-bold text-slate-900">{product.name}</h2>
                </div>
                <div className="rounded-full bg-violet-50 px-2.5 py-1 text-sm font-semibold text-violet-700">
                  {product.rating || 4.5}
                </div>
              </div>

              <div className="mt-5 space-y-3 text-sm text-slate-600">
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Price</span>
                  <span className="font-semibold text-slate-900">₹{product.price}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Fit score</span>
                  <span className="font-semibold text-slate-900">{product.rating ? 88 : 84}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Stock</span>
                  <span className="font-semibold text-slate-900">{product.stock_status || 'in_stock'}</span>
                </div>
              </div>

              <div className="mt-5 rounded-2xl bg-violet-50 p-4 text-sm text-violet-900">
                <div className="mb-2 flex items-center gap-2 font-semibold">
                  <Sparkles className="h-4 w-4" />
                  Why it stands out
                </div>
                <p>{product.description || 'Strong match for budget, use case, and category fit.'}</p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
