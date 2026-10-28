import { useMemo, useState } from 'react'
import {
  ArrowRight,
  Award,
  Check,
  Flame,
  Plus,
  Scale,
  Sparkles,
  Swords,
  Trophy,
  X,
  Zap,
} from 'lucide-react'
import { useCart } from '../context/CartContext'

export default function ProductBattleModal() {
  const { activeBattleProducts, setActiveBattleProducts, addToCart } = useCart()
  const [selectedWinner, setSelectedWinner] = useState(null)

  if (!activeBattleProducts || activeBattleProducts.length < 2) return null

  const [prodA, prodB] = activeBattleProducts

  const priceA = Number(prodA.price) || 0
  const priceB = Number(prodB.price) || 0
  const ratingA = Number(prodA.rating) || 4.3
  const ratingB = Number(prodB.rating) || 4.3

  // Comparative AI calculations
  const comparison = useMemo(() => {
    // Value score (cheaper gets more points if rating is similar)
    const valScoreA = Math.min(100, Math.round((50000 / Math.max(priceA, 1000)) * 20 + ratingA * 12))
    const valScoreB = Math.min(100, Math.round((50000 / Math.max(priceB, 1000)) * 20 + ratingB * 12))

    // Performance score (based on price & specs)
    const perfScoreA = Math.min(98, Math.round(priceA > priceB ? 92 : 82 + (ratingA > ratingB ? 6 : 0)))
    const perfScoreB = Math.min(98, Math.round(priceB > priceA ? 92 : 82 + (ratingB > ratingA ? 6 : 0)))

    // Durability & rating
    const satScoreA = Math.min(99, Math.round(ratingA * 20))
    const satScoreB = Math.min(99, Math.round(ratingB * 20))

    const isACheaper = priceA <= priceB
    const winnerProd = ratingA >= ratingB && isACheaper ? prodA : (priceB > priceA * 1.3 ? prodA : prodB)

    let verdictText = ''
    if (priceA !== priceB) {
      const cheaper = isACheaper ? prodA : prodB
      const expensive = isACheaper ? prodB : prodA
      const diff = Math.abs(priceA - priceB)
      verdictText = `${cheaper.name} is the superior Value Champion (saves you ₹${diff.toLocaleString('en-IN')}). Choose ${expensive.name} if you require top-tier premium hardware & higher headroom.`
    } else {
      verdictText = `Both models offer matching price points. ${prodA.name} edges forward in portability, while ${prodB.name} excels in durability.`
    }

    return {
      valScoreA, valScoreB,
      perfScoreA, perfScoreB,
      satScoreA, satScoreB,
      winnerProd,
      verdictText,
    }
  }, [prodA, prodB, priceA, priceB, ratingA, ratingB])

  const handleClaim = (product) => {
    addToCart(product, 1)
    setActiveBattleProducts(null)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md p-4">
      <div className="relative max-h-[94vh] overflow-y-auto max-w-3xl w-full rounded-3xl bg-white p-6 sm:p-8 shadow-2xl border border-slate-100">
        <button
          onClick={() => setActiveBattleProducts(null)}
          className="absolute right-4 top-4 rounded-full bg-slate-100 p-2 text-slate-400 hover:text-slate-800 transition"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Title */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-red-500 to-amber-500 px-4 py-1 text-xs font-black text-white shadow-sm mb-2">
            <Swords className="h-3.5 w-3.5" />
            AI HEAD-TO-HEAD BATTLE ARENA
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Product Showdown</h2>
          <p className="text-xs text-slate-500">Real-time side-by-side specs, value metric battle & AI referee verdict</p>
        </div>

        {/* The Two Battle Contenders */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative">
          {/* VS Badge */}
          <div className="hidden md:flex absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20 h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-white font-black text-xs shadow-xl ring-4 ring-white">
            VS
          </div>

          {/* Product A */}
          <div className="rounded-2xl border-2 border-slate-200 p-4 bg-slate-50/50 flex flex-col justify-between hover:border-violet-400 transition">
            <div>
              <div className="relative mb-3">
                <img
                  src={prodA.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=600&q=80'}
                  alt={prodA.name}
                  className="h-40 w-full rounded-xl object-cover"
                />
                <span className="absolute top-2 left-2 rounded-full bg-slate-900/80 px-2.5 py-0.5 text-[10px] font-bold text-white">
                  Contender A
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-sm leading-snug">{prodA.name}</h3>
              <p className="text-xs text-slate-500">{prodA.brand} • {prodA.subcategory || prodA.category}</p>
              <p className="text-lg font-black text-slate-900 mt-2">₹{priceA.toLocaleString('en-IN')}</p>
            </div>

            <button
              onClick={() => handleClaim(prodA)}
              className="mt-4 w-full rounded-xl bg-slate-900 py-2.5 text-xs font-bold text-white hover:bg-slate-800 transition flex items-center justify-center gap-1.5"
            >
              <Plus className="h-3.5 w-3.5" /> Pick Winner & Add to Cart
            </button>
          </div>

          {/* Product B */}
          <div className="rounded-2xl border-2 border-slate-200 p-4 bg-slate-50/50 flex flex-col justify-between hover:border-violet-400 transition">
            <div>
              <div className="relative mb-3">
                <img
                  src={prodB.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=600&q=80'}
                  alt={prodB.name}
                  className="h-40 w-full rounded-xl object-cover"
                />
                <span className="absolute top-2 left-2 rounded-full bg-slate-900/80 px-2.5 py-0.5 text-[10px] font-bold text-white">
                  Contender B
                </span>
              </div>
              <h3 className="font-bold text-slate-900 text-sm leading-snug">{prodB.name}</h3>
              <p className="text-xs text-slate-500">{prodB.brand} • {prodB.subcategory || prodB.category}</p>
              <p className="text-lg font-black text-slate-900 mt-2">₹{priceB.toLocaleString('en-IN')}</p>
            </div>

            <button
              onClick={() => handleClaim(prodB)}
              className="mt-4 w-full rounded-xl bg-slate-900 py-2.5 text-xs font-bold text-white hover:bg-slate-800 transition flex items-center justify-center gap-1.5"
            >
              <Plus className="h-3.5 w-3.5" /> Pick Winner & Add to Cart
            </button>
          </div>
        </div>

        {/* Spec Comparison Meters */}
        <div className="mt-6 space-y-3 rounded-2xl bg-slate-50 p-4 border border-slate-200/80">
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Head-to-Head Gauges</p>

          {/* Value for Money */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
              <span>{comparison.valScoreA}%</span>
              <span>Value for Money</span>
              <span>{comparison.valScoreB}%</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              <div className="h-2 rounded-l-full bg-slate-200 overflow-hidden flex justify-end">
                <div className="h-full bg-violet-600 rounded-l-full" style={{ width: `${comparison.valScoreA}%` }} />
              </div>
              <div className="h-2 rounded-r-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-r-full" style={{ width: `${comparison.valScoreB}%` }} />
              </div>
            </div>
          </div>

          {/* Performance & Spec Power */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
              <span>{comparison.perfScoreA}%</span>
              <span>Performance / Features</span>
              <span>{comparison.perfScoreB}%</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              <div className="h-2 rounded-l-full bg-slate-200 overflow-hidden flex justify-end">
                <div className="h-full bg-violet-600 rounded-l-full" style={{ width: `${comparison.perfScoreA}%` }} />
              </div>
              <div className="h-2 rounded-r-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-r-full" style={{ width: `${comparison.perfScoreB}%` }} />
              </div>
            </div>
          </div>

          {/* User Satisfaction */}
          <div>
            <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
              <span>{comparison.satScoreA}% ({ratingA}★)</span>
              <span>Customer Satisfaction</span>
              <span>{comparison.satScoreB}% ({ratingB}★)</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              <div className="h-2 rounded-l-full bg-slate-200 overflow-hidden flex justify-end">
                <div className="h-full bg-violet-600 rounded-l-full" style={{ width: `${comparison.satScoreA}%` }} />
              </div>
              <div className="h-2 rounded-r-full bg-slate-200 overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-r-full" style={{ width: `${comparison.satScoreB}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* AI Referee Verdict */}
        <div className="mt-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 p-4">
          <div className="flex items-start gap-3">
            <Trophy className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-amber-700">AI Referee Verdict</p>
              <p className="text-xs font-medium text-amber-950 mt-1 leading-relaxed">
                {comparison.verdictText}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
