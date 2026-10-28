import { useEffect, useState } from 'react'
import {
  ArrowRight,
  CheckCircle2,
  Gift,
  Minus,
  Plus,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Trash2,
  Truck,
  X,
  Zap,
} from 'lucide-react'
import { OFFER_MILESTONES, useCart } from '../context/CartContext'
import { api } from '../services/api'

export default function SmartCartDrawer() {
  const {
    items,
    removeFromCart,
    updateQuantity,
    subtotal,
    offerProgress,
    isCartOpen,
    setIsCartOpen,
    addToCart,
    setIsRazorpayOpen,
  } = useCart()

  const [allProducts, setAllProducts] = useState([])
  const [fillerItems, setFillerItems] = useState([])

  // Load products to compute smart fillers
  useEffect(() => {
    api.getProducts()
      .then(res => setAllProducts(res.items || []))
      .catch(() => setAllProducts([]))
  }, [])

  // Calculate smart filler items that fill the remaining offer gap
  useEffect(() => {
    if (!allProducts.length) return
    const gap = offerProgress.remainingToNext

    // Existing product ids in cart
    const cartIds = new Set(items.map(i => i.product_id))

    let candidates = []
    if (gap > 0) {
      // Find items priced between gap * 0.4 and gap * 1.3
      const minPrice = Math.max(299, gap * 0.45)
      const maxPrice = Math.max(gap * 1.25, 999)

      candidates = allProducts.filter(p => {
        if (cartIds.has(p.product_id)) return false
        const price = Number(p.price) || 0
        return price >= minPrice && price <= maxPrice
      })

      // Sort by best rating / proximity to gap
      candidates.sort((a, b) => {
        const diffA = Math.abs((Number(a.price) || 0) - gap)
        const diffB = Math.abs((Number(b.price) || 0) - gap)
        return diffA - diffB
      })
    } else {
      // If all milestones unlocked, show popular add-ons (< ₹1500)
      candidates = allProducts.filter(p => !cartIds.has(p.product_id) && p.price < 1500)
    }

    setFillerItems(candidates.slice(0, 4))
  }, [allProducts, offerProgress.remainingToNext, items])

  if (!isCartOpen) return null

  const {
    nextMilestone,
    remainingToNext,
    progressPercent,
    discountAmount,
    deliveryFee,
    freeDelivery,
    freeGift,
    grandTotal,
  } = offerProgress

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity"
        onClick={() => setIsCartOpen(false)}
      />

      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between bg-slate-50/80">
            <div className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-600 text-white shadow-sm">
                <ShoppingBag className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Smart Cart</h2>
                <p className="text-xs text-slate-500">{items.length} item{items.length !== 1 ? 's' : ''} added</p>
              </div>
            </div>
            <button
              onClick={() => setIsCartOpen(false)}
              className="rounded-full p-2 text-slate-400 hover:bg-slate-200/60 hover:text-slate-700 transition"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Offer Threshold Progress Bar */}
          <div className="bg-gradient-to-r from-violet-50 via-indigo-50 to-purple-50 p-4 border-b border-violet-100">
            {nextMilestone ? (
              <div>
                <div className="flex items-center justify-between text-xs font-semibold mb-1.5">
                  <span className="flex items-center gap-1.5 text-violet-800">
                    <Zap className="h-3.5 w-3.5 fill-violet-600 text-violet-600 animate-pulse" />
                    Add ₹{remainingToNext.toLocaleString('en-IN')} more for:
                  </span>
                  <span className="text-violet-900 font-bold">{nextMilestone.title}</span>
                </div>
                {/* Progress bar track */}
                <div className="h-2 w-full rounded-full bg-violet-200/70 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 transition-all duration-500 ease-out"
                    style={{ width: `${progressPercent}%` }}
                  />
                </div>
                <div className="mt-2 flex justify-between text-[11px] text-slate-500">
                  <span>Current: ₹{subtotal.toLocaleString('en-IN')}</span>
                  <span>Goal: ₹{nextMilestone.threshold.toLocaleString('en-IN')}</span>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-emerald-800 text-xs font-semibold">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                <span>🎉 Maximum VIP Offer Unlocked! Flat ₹1,500 OFF + Free Delivery!</span>
              </div>
            )}

            {/* Unlocked perks tags */}
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              {freeDelivery && (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-800">
                  <Truck className="h-3 w-3" /> Free Express Delivery
                </span>
              )}
              {discountAmount > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-violet-100 px-2.5 py-0.5 text-[10px] font-semibold text-violet-800">
                  <Sparkles className="h-3 w-3" /> -₹{discountAmount.toLocaleString('en-IN')} Saved
                </span>
              )}
              {freeGift && (
                <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-[10px] font-semibold text-amber-800">
                  <Gift className="h-3 w-3" /> Free Tech Cleaning Kit Unlocked
                </span>
              )}
            </div>
          </div>

          {/* Cart Body */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {items.length === 0 ? (
              <div className="py-16 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100 text-slate-400 mb-3">
                  <ShoppingBag className="h-8 w-8" />
                </div>
                <p className="text-base font-bold text-slate-700">Your cart is empty</p>
                <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                  Explore recommendations and tap &quot;Add to Cart&quot; to build your smart order.
                </p>
              </div>
            ) : (
              items.map(item => (
                <div
                  key={item.product_id}
                  className="flex gap-3 rounded-2xl border border-slate-200/80 p-3 bg-white hover:border-slate-300 transition"
                >
                  <img
                    src={item.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=300&q=80'}
                    alt={item.name}
                    className="h-18 w-18 rounded-xl object-cover flex-shrink-0 bg-slate-100"
                  />
                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div>
                      <div className="flex items-start justify-between gap-1">
                        <h4 className="text-xs font-bold text-slate-900 leading-snug line-clamp-1">{item.name}</h4>
                        <button
                          onClick={() => removeFromCart(item.product_id)}
                          className="text-slate-400 hover:text-red-500 p-0.5 transition"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                      <p className="text-[11px] text-slate-400 capitalize">{item.category}</p>
                    </div>

                    <div className="flex items-center justify-between mt-2">
                      <p className="text-xs font-black text-slate-900">
                        ₹{(item.price * item.quantity).toLocaleString('en-IN')}
                      </p>

                      <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-2 py-0.5">
                        <button
                          onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                          className="text-slate-500 hover:text-slate-900"
                        >
                          <Minus className="h-3 w-3" />
                        </button>
                        <span className="text-xs font-bold text-slate-800">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                          className="text-slate-500 hover:text-slate-900"
                        >
                          <Plus className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}

            {/* Smart Filler Section: "Add to unlock offer" */}
            {remainingToNext > 0 && fillerItems.length > 0 && items.length > 0 && (
              <div className="mt-5 rounded-2xl border border-dashed border-violet-300 bg-gradient-to-b from-violet-50/50 to-white p-3.5">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-bold text-violet-900 flex items-center gap-1.5">
                    <Sparkles className="h-3.5 w-3.5 text-violet-600" />
                    Add one of these to unlock the offer:
                  </p>
                  <span className="text-[10px] text-violet-600 font-medium">Smart Fillers</span>
                </div>

                <div className="space-y-2">
                  {fillerItems.map(filler => (
                    <div
                      key={filler.product_id}
                      className="flex items-center justify-between gap-2 rounded-xl bg-white p-2 border border-slate-100 shadow-sm"
                    >
                      <img
                        src={filler.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=200&q=80'}
                        alt={filler.name}
                        className="h-10 w-10 rounded-lg object-cover flex-shrink-0"
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-semibold text-slate-800 truncate">{filler.name}</p>
                        <p className="text-[11px] font-bold text-violet-700">₹{Number(filler.price).toLocaleString('en-IN')}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => addToCart(filler, 1)}
                        className="flex-shrink-0 inline-flex items-center gap-1 rounded-lg bg-violet-600 px-2.5 py-1 text-xs font-semibold text-white hover:bg-violet-700 transition"
                      >
                        <Plus className="h-3 w-3" /> Add
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer Bill & Checkout */}
          {items.length > 0 && (
            <div className="border-t border-slate-200 bg-white p-5 shadow-lg space-y-3">
              <div className="space-y-1.5 text-xs text-slate-600">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-semibold text-slate-900">₹{subtotal.toLocaleString('en-IN')}</span>
                </div>
                {discountAmount > 0 && (
                  <div className="flex justify-between text-emerald-600 font-semibold">
                    <span>Offer Discount</span>
                    <span>-₹{discountAmount.toLocaleString('en-IN')}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>Express Delivery</span>
                  <span className={deliveryFee === 0 ? 'text-emerald-600 font-semibold' : 'text-slate-900'}>
                    {deliveryFee === 0 ? 'FREE' : `₹${deliveryFee}`}
                  </span>
                </div>
                {freeGift && (
                  <div className="flex justify-between text-amber-600 font-semibold">
                    <span>VIP Gift</span>
                    <span>Cleaning Kit (₹499 Free)</span>
                  </div>
                )}
                <div className="border-t border-slate-100 pt-2 flex justify-between text-sm font-black text-slate-900">
                  <span>Total Amount</span>
                  <span>₹{grandTotal.toLocaleString('en-IN')}</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  setIsCartOpen(false)
                  setIsRazorpayOpen(true)
                }}
                className="w-full flex items-center justify-center gap-2 rounded-2xl bg-slate-900 py-3.5 text-sm font-bold text-white hover:bg-slate-800 transition shadow-md hover:shadow-lg"
              >
                <span>Proceed to Pay ₹{grandTotal.toLocaleString('en-IN')}</span>
                <ArrowRight className="h-4 w-4" />
              </button>

              <div className="flex items-center justify-center gap-1 text-[11px] text-slate-400">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                <span>Razorpay Test Sandbox • 100% Secure Simulated Checkout</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
