import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowRight,
  ArrowUpRight,
  Check,
  MessageSquareText,
  Plus,
  Save,
  Search,
  ShoppingBag,
  Sparkles,
  Star,
  Swords,
  TrendingUp,
  X,
  Zap,
} from 'lucide-react'
import { useCart } from '../context/CartContext'
import { api } from '../services/api'

const categoriesList = [
  { id: 'all', label: 'All Items', prompt: 'Show me top recommendations across all categories.' },
  { id: 'electronics', label: '💻 Electronics', prompt: 'Best laptops and electronics under ₹60,000.' },
  { id: 'footwear', label: '👟 Footwear', prompt: 'Men and women running shoes and sneakers under ₹3,500.' },
  { id: 'fashion', label: '👗 Fashion', prompt: 'Trending casual overshirts, tees, and jackets.' },
  { id: 'home-kitchen', label: '🍳 Kitchen', prompt: 'Best kitchen appliances and cookware under ₹5,000.' },
  { id: 'fitness', label: '🏋️ Fitness', prompt: 'Home gym and fitness workout gear under ₹3,000.' },
  { id: 'outdoor', label: '⛺ Outdoor', prompt: 'Hiking backpacks and camping gear under ₹5,000.' },
  { id: 'books', label: '📚 Books', prompt: 'Top self-improvement and productivity books.' },
  { id: 'wallets', label: '👜 Wallets & Bags', prompt: 'Slim RFID leather wallets and travel organizers.' },
]

const starterPrompts = [
  { label: '💻 Laptop for college under ₹50k', text: 'Lightweight laptop for college, budget ₹50,000.' },
  { label: '👟 Running shoes under ₹3,000', text: "Men's running shoes under ₹3,000." },
  { label: '🎁 Gift for hiking dad with bad knees', text: 'Gift for my dad who enjoys hiking but has bad knees, budget ₹5,000.' },
  { label: '👜 Slim RFID travel wallet', text: 'Slim RFID-blocking wallet for travel under ₹1,500.' },
  { label: '🏋️ Home gym starter kit under ₹3,000', text: 'Home gym equipment for beginners under ₹3,000.' },
  { label: '📚 Best productivity book', text: 'Best self-improvement or productivity book to read.' },
  { label: '🎧 Noise cancelling headphones', text: 'Wireless noise-cancelling headphones under ₹10,000.' },
  { label: '🍳 Smart kitchen appliance under ₹5,000', text: 'Best kitchen appliance for an apartment under ₹5,000.' },
]

// ── helpers ──────────────────────────────────────────────────────────────────
const STORAGE_KEY = 'shopsense-discover-state'

function loadState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return null
}

function saveState(state) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {}
}

// ── Product Detail Modal ──────────────────────────────────────────────────────
function ProductModal({ product, onClose, onAddToCart, onCompare, onSave }) {
  if (!product) return null
  const attrs = product.attributes || {}
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative max-h-[90vh] overflow-y-auto max-w-lg w-full rounded-3xl bg-white p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full bg-slate-100 p-2 text-slate-400 hover:text-slate-800 transition"
        >
          <X className="h-4 w-4" />
        </button>
        <img
          src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'}
          alt={product.name}
          className="h-56 w-full rounded-2xl object-cover mb-4"
        />
        <div className="flex items-start justify-between gap-2 mb-1">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-violet-600 bg-violet-50 px-2 py-0.5 rounded-full">
              {product.category}
            </span>
            <h2 className="text-xl font-bold text-slate-900 leading-tight mt-1">{product.name}</h2>
            <p className="text-xs text-slate-500">{product.brand} • {product.subcategory || ''}</p>
          </div>
          <p className="text-xl font-black text-slate-900 flex-shrink-0">₹{Number(product.price)?.toLocaleString('en-IN')}</p>
        </div>

        {/* Description */}
        <p className="mt-3 text-xs text-slate-600 leading-relaxed">{product.description || product.explanation}</p>

        {/* Key Specs */}
        {Object.keys(attrs).length > 0 && (
          <div className="mt-4">
            <p className="text-xs font-bold uppercase tracking-wide text-slate-400 mb-2">Key Specifications</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(attrs).map(([k, v]) => (
                <div key={k} className="rounded-xl bg-slate-50 px-3 py-2 border border-slate-100">
                  <p className="text-[10px] text-slate-400 capitalize">{k.replace(/_/g, ' ')}</p>
                  <p className="text-xs font-semibold text-slate-800">{String(v)}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {(product.tags || []).length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            {product.tags.map(t => (
              <span key={t} className="rounded-full bg-violet-50 px-2.5 py-1 text-[11px] font-medium text-violet-700">
                #{t}
              </span>
            ))}
          </div>
        )}

        {/* AI explanation */}
        {product.explanation && (
          <div className="mt-4 rounded-xl bg-violet-50/80 border border-violet-100 p-3">
            <p className="text-xs font-bold text-violet-700 mb-1 flex items-center gap-1">
              <Sparkles className="h-3 w-3" /> Why ShopSense recommends this
            </p>
            <p className="text-xs text-violet-900 leading-normal">{product.explanation}</p>
          </div>
        )}

        {/* Actions */}
        <div className="mt-5 flex gap-2">
          <button
            onClick={() => {
              onAddToCart(product)
              onClose()
            }}
            className="flex-1 rounded-2xl bg-slate-900 py-3 text-xs font-bold text-white hover:bg-slate-800 transition flex items-center justify-center gap-1.5"
          >
            <ShoppingBag className="h-4 w-4" /> Add to Cart
          </button>
          <button
            onClick={() => {
              onCompare(product.product_id)
              onClose()
            }}
            className="rounded-2xl border border-violet-200 bg-violet-50 px-4 py-3 text-xs font-semibold text-violet-700 hover:bg-violet-100 transition"
          >
            + Compare
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Why NOT Modal ──────────────────────────────────────────────────────────────
function WhyNotModal({ data, onClose }) {
  if (!data) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative max-w-md w-full rounded-3xl bg-white p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full bg-slate-100 p-1.5 text-slate-400 hover:text-slate-800 transition"
        >
          <X className="h-4 w-4" />
        </button>
        <span className="rounded-full bg-red-50 px-3 py-1 text-[10px] font-bold text-red-600 uppercase tracking-wider">
          Tradeoff Analysis
        </span>
        <h2 className="text-lg font-bold text-slate-900 mt-2 mb-1">Why not {data.name}?</h2>
        <p className="text-xs text-slate-600 mb-4 leading-relaxed">{data.message}</p>

        {data.hard_constraint_failures?.length > 0 && (
          <div className="mb-3 rounded-2xl bg-red-50/70 p-3 border border-red-100">
            <p className="text-[11px] font-bold text-red-700 uppercase tracking-wide mb-1.5">Unmet Constraints</p>
            <ul className="list-disc pl-4 space-y-1 text-xs text-red-800">
              {data.hard_constraint_failures.map(f => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </div>
        )}

        {data.feature_gaps?.length > 0 && (
          <div className="mb-3 rounded-2xl bg-amber-50/70 p-3 border border-amber-100">
            <p className="text-[11px] font-bold text-amber-700 uppercase tracking-wide mb-1.5">Feature Gaps</p>
            <ul className="list-disc pl-4 space-y-1 text-xs text-amber-800">
              {data.feature_gaps.map(f => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3.5 py-2 text-xs mt-3">
          <span className="text-slate-500 font-medium">Estimated Match Fit</span>
          <span className="font-bold text-slate-900">{data.matched_score ? `${(data.matched_score * 100).toFixed(0)}%` : '—'}</span>
        </div>

        <button
          onClick={onClose}
          className="mt-4 w-full rounded-2xl bg-slate-900 py-2.5 text-xs font-bold text-white hover:bg-slate-800 transition"
        >
          Got it
        </button>
      </div>
    </div>
  )
}

// ── Main Discover Page ─────────────────────────────────────────────────────────
export default function Discover({ userId, selectedCompare, setSelectedCompare, savedProducts, setSavedProducts }) {
  const { addToCart, setActiveBattleProducts } = useCart()

  const saved = loadState()
  const [sessionId, setSessionId] = useState(saved?.sessionId || null)
  const [messages, setMessages] = useState(
    saved?.messages || [{ role: 'assistant', content: 'Hi! Tell me what you are looking to buy or choose a category below.' }]
  )
  const [input, setInput] = useState('')
  const [results, setResults] = useState(saved?.results || [])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [meta, setMeta] = useState(saved?.meta || {})
  const [clarificationQ, setClarificationQ] = useState(saved?.clarificationQ || '')
  const [clarificationInput, setClarificationInput] = useState('')
  const [modalProduct, setModalProduct] = useState(null)
  const [whyModal, setWhyModal] = useState(null)
  const [battleSelection, setBattleSelection] = useState([])
  const chatEndRef = useRef(null)

  // Persist state to sessionStorage whenever it changes
  useEffect(() => {
    saveState({ sessionId, messages, results, meta, clarificationQ })
  }, [sessionId, messages, results, meta, clarificationQ])

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Initial load if no results present
  useEffect(() => {
    if (results.length === 0 && !loading && !saved?.results?.length) {
      handlePrompt("Men's running shoes under ₹3,000.")
    }
  }, [])

  const handlePrompt = async (text) => {
    setInput(text)
    await handleSubmit(text)
  }

  const handleSubmit = async (messageOverride) => {
    const message = (messageOverride ?? input).trim()
    if (!message || loading) return
    setLoading(true)
    setError('')
    setMessages(prev => [...prev, { role: 'user', content: message }])
    try {
      const payload = { user_id: userId, message, ...(sessionId ? { session_id: sessionId } : {}) }
      const response = await api.chat(payload)
      if (response.session_id && !sessionId) setSessionId(response.session_id)
      setMeta(response)
      if (response.response_type === 'clarification' && response.clarification_question) {
        setClarificationQ(response.clarification_question)
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: response.assistant_response || response.clarification_question },
        ])
      } else {
        setClarificationQ('')
        setResults(response.recommendations || [])
        setMessages(prev => [
          ...prev,
          { role: 'assistant', content: response.assistant_response || `Found ${response.recommendations?.length || 0} top picks for you.` },
        ])
      }
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  const handleNewConversation = async () => {
    if (sessionId) {
      try {
        await api.deleteSession(sessionId)
      } catch {}
    }
    setSessionId(null)
    setMessages([{ role: 'assistant', content: 'Hi! Tell me what you are looking to buy or choose a category below.' }])
    setResults([])
    setMeta({})
    setClarificationQ('')
    setClarificationInput('')
    setError('')
    sessionStorage.removeItem(STORAGE_KEY)
  }

  const handleSave = async (productId) => {
    try {
      const data = await api.saveProduct(productId)
      setSavedProducts(data.items || [])
    } catch {
      setError('Unable to save product right now.')
    }
  }

  const handleCompare = (productId) => {
    const product = results.find(r => r.product_id === productId)
    setSelectedCompare(prev => {
      const already = prev.find(e => (typeof e === 'string' ? e : e.product_id) === productId)
      if (already) return prev
      return [
        ...prev,
        {
          product_id: productId,
          fit_score: product?.fit_score,
          match_summary: product?.match_summary,
          name: product?.name,
          category: product?.category,
          price: product?.price,
          image: product?.image,
        },
      ]
    })
  }

  const handleWhyNot = async (product) => {
    try {
      const lastMsg = [...messages].reverse().find(m => m.role === 'user')?.content || ''
      const data = await api.whyNot(product.product_id, lastMsg, sessionId)
      setWhyModal(data)
    } catch {
      setError('Unable to fetch why-not explanation.')
    }
  }

  const toggleBattleSelect = (product) => {
    setBattleSelection(prev => {
      const exists = prev.find(p => p.product_id === product.product_id)
      if (exists) {
        return prev.filter(p => p.product_id !== product.product_id)
      }
      if (prev.length >= 2) {
        return [prev[1], product]
      }
      const updated = [...prev, product]
      if (updated.length === 2) {
        setActiveBattleProducts(updated)
      }
      return updated
    })
  }

  // Combined You May Also Like items (upgrade pick + companions)
  const youMayLikeItems = useMemo(() => {
    if (meta?.you_may_also_like && meta.you_may_also_like.length > 0) {
      return meta.you_may_also_like
    }
    if (meta?.complementary_product) {
      return [meta.complementary_product]
    }
    return []
  }, [meta])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <ProductModal
        product={modalProduct}
        onClose={() => setModalProduct(null)}
        onAddToCart={addToCart}
        onCompare={handleCompare}
        onSave={handleSave}
      />
      <WhyNotModal data={whyModal} onClose={() => setWhyModal(null)} />

      {/* Top Category Filter Bar */}
      <div className="mb-6 overflow-x-auto pb-2 scrollbar-none">
        <div className="flex gap-2">
          {categoriesList.map(cat => (
            <button
              key={cat.id}
              type="button"
              onClick={() => handlePrompt(cat.prompt)}
              className="flex-shrink-0 rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-bold text-slate-700 shadow-sm hover:border-violet-400 hover:bg-violet-50/50 hover:text-violet-700 transition"
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.6fr_0.8fr]">
        {/* ── Main Panel ── */}
        <section className="rounded-3xl border border-slate-200/80 bg-white p-4 shadow-sm sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-violet-600">AI Guided Discovery</p>
              <h1 className="mt-0.5 text-2xl font-black text-slate-900">Ask ShopSense</h1>
            </div>
            <button
              type="button"
              onClick={handleNewConversation}
              className="rounded-full border border-slate-200 bg-slate-50 px-3.5 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 transition"
            >
              New Search
            </button>
          </div>

          {/* Starter Prompts */}
          <div className="mb-5 flex flex-wrap gap-1.5">
            {starterPrompts.map(p => (
              <button
                key={p.text}
                type="button"
                onClick={() => handlePrompt(p.text)}
                className="rounded-full border border-violet-100 bg-violet-50/70 px-3 py-1.5 text-xs font-medium text-violet-700 transition hover:border-violet-300 hover:bg-violet-100"
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Chat Window */}
          <div className="max-h-64 overflow-y-auto space-y-3 rounded-2xl border border-slate-200 bg-slate-50/60 p-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'bg-white text-slate-700 ring-1 ring-slate-200/80 shadow-sm'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-xs font-medium text-violet-600">
                <MessageSquareText className="h-4 w-4 animate-pulse" />
                ShopSense is ranking top matching candidates...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Clarification Gate */}
          {clarificationQ && (
            <div className="mt-4 rounded-2xl border border-violet-200 bg-violet-50/80 px-4 py-3">
              <p className="text-xs font-bold text-violet-900 mb-2">{clarificationQ}</p>
              <div className="flex gap-2">
                <input
                  value={clarificationInput}
                  onChange={e => setClarificationInput(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && clarificationInput.trim()) {
                      handleSubmit(clarificationInput)
                      setClarificationInput('')
                    }
                  }}
                  placeholder="Your answer..."
                  className="flex-1 rounded-xl border border-violet-200 bg-white px-3 py-1.5 text-xs outline-none focus:border-violet-400"
                />
                <button
                  type="button"
                  onClick={() => {
                    if (clarificationInput.trim()) {
                      handleSubmit(clarificationInput)
                      setClarificationInput('')
                    }
                  }}
                  className="rounded-xl bg-violet-600 px-4 py-1.5 text-xs font-bold text-white hover:bg-violet-700"
                >
                  Answer
                </button>
              </div>
            </div>
          )}

          {error && !clarificationQ && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
              {error}
            </div>
          )}

          {/* Search Input */}
          <div className="mt-4 flex gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm">
            <div className="flex flex-1 items-center gap-2 rounded-xl bg-slate-50 px-3 py-2">
              <Search className="h-4 w-4 flex-shrink-0 text-slate-400" />
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleSubmit()
                  }
                }}
                placeholder="Search products, budget (e.g. laptop under 50k, shoes for bad knees)..."
                className="w-full border-0 bg-transparent text-xs text-slate-700 outline-none placeholder:text-slate-400"
              />
            </div>
            <button
              type="button"
              onClick={() => handleSubmit()}
              className="rounded-xl bg-slate-900 px-5 py-2.5 text-xs font-bold text-white transition hover:bg-slate-700 shadow-sm"
            >
              Search
            </button>
          </div>

          {/* Results Header */}
          {results.length > 0 && (
            <div className="mt-6 flex items-center justify-between pb-2 border-b border-slate-100">
              <p className="text-xs font-bold text-slate-900">
                Top Matches ({results.length} items found)
              </p>
              <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
                <span>Select 2 items for</span>
                <button
                  onClick={() => {
                    if (results.length >= 2) {
                      setActiveBattleProducts([results[0], results[1]])
                    }
                  }}
                  className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2 py-0.5 font-bold text-amber-700 border border-amber-200 hover:bg-amber-100"
                >
                  <Swords className="h-3 w-3" /> AI Battle Showdown
                </button>
              </div>
            </div>
          )}

          {/* Product Cards List */}
          <div className="mt-4 space-y-4">
            {results.length === 0 && !loading && (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-12 text-center text-xs text-slate-400">
                No recommendations yet. Choose a category above or describe what you want to buy.
              </div>
            )}

            {results.map((product, idx) => {
              const hasTradeoffs =
                (product.unmet_constraints && product.unmet_constraints.length > 0) ||
                (typeof product.fit_score === 'number' && product.fit_score < 0.85)

              const isBattleSelected = battleSelection.some(p => p.product_id === product.product_id)

              return (
                <article
                  key={product.product_id}
                  className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm hover:shadow-md transition"
                >
                  <div className="grid md:grid-cols-[180px_1fr]">
                    {/* Image */}
                    <div className="relative">
                      <img
                        src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'}
                        alt={product.name}
                        className="h-44 w-full object-cover md:h-full md:rounded-l-2xl bg-slate-100"
                      />
                      <div className="absolute top-2 left-2 rounded-full bg-slate-900/80 px-2 py-0.5 text-[10px] font-bold text-white">
                        #{idx + 1}
                      </div>
                      <div className="absolute top-2 right-2 rounded-full bg-violet-600 px-2 py-0.5 text-[10px] font-bold text-white shadow-sm">
                        {typeof product.fit_score === 'number' ? `${(product.fit_score * 100).toFixed(0)}% fit` : '—'}
                      </div>
                    </div>

                    {/* Info */}
                    <div className="p-4 flex flex-col justify-between">
                      <div>
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-violet-600">
                              {product.subcategory || product.category}
                            </span>
                            <h3 className="text-sm font-bold text-slate-900 leading-snug">{product.name}</h3>
                            <p className="text-[11px] text-slate-500">{product.brand}</p>
                          </div>
                          <div className="flex-shrink-0 text-right">
                            <p className="text-base font-black text-slate-900">
                              ₹{Number(product.price)?.toLocaleString('en-IN')}
                            </p>
                            <span
                              className={`text-[10px] font-bold ${
                                product.stock_status === 'in_stock' ? 'text-emerald-600' : 'text-amber-600'
                              }`}
                            >
                              {product.stock_status === 'in_stock' ? '✓ In Stock' : '⚡ Limited'}
                            </span>
                          </div>
                        </div>

                        {/* Stars */}
                        <div className="mt-1.5 flex items-center gap-1">
                          {[1, 2, 3, 4, 5].map(s => (
                            <Star
                              key={s}
                              className={`h-3 w-3 ${
                                s <= Math.round(Number(product.rating || 4.4))
                                  ? 'fill-amber-400 text-amber-400'
                                  : 'fill-slate-200 text-slate-200'
                              }`}
                            />
                          ))}
                          <span className="ml-1 text-[11px] font-bold text-slate-600">
                            {product.rating || '4.5'}
                          </span>
                          <span className="text-[10px] text-slate-400">({product.review_count || 120} reviews)</span>
                        </div>

                        <p className="mt-2 text-xs leading-relaxed text-slate-600 line-clamp-2">
                          {product.explanation}
                        </p>

                        {/* Unmet Constraints Badge */}
                        {(product.unmet_constraints || []).length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {product.unmet_constraints.map(c => (
                              <span key={c} className="rounded-full bg-red-50 px-2 py-0.5 text-[10px] font-semibold text-red-600">
                                ⚠ {c}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Action Bar */}
                      <div className="mt-4 flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-100">
                        {/* 1. Add to Smart Cart */}
                        <button
                          type="button"
                          onClick={() => addToCart(product, 1)}
                          className="inline-flex items-center gap-1 rounded-full bg-slate-900 px-3.5 py-1.5 text-xs font-bold text-white hover:bg-slate-800 transition shadow-sm"
                        >
                          <ShoppingBag className="h-3.5 w-3.5" /> Add to Cart
                        </button>

                        {/* 2. View details */}
                        <button
                          type="button"
                          onClick={() => setModalProduct(product)}
                          className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                        >
                          View Details
                        </button>

                        {/* 3. Compare */}
                        <button
                          type="button"
                          onClick={() => handleCompare(product.product_id)}
                          className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1.5 text-xs font-semibold text-violet-700 hover:bg-violet-100 transition"
                        >
                          + Compare
                        </button>

                        {/* 4. Save */}
                        <button
                          type="button"
                          onClick={() => handleSave(product.product_id)}
                          className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 transition"
                        >
                          💾 Save
                        </button>

                        {/* 5. Battle Selection */}
                        <button
                          type="button"
                          onClick={() => toggleBattleSelect(product)}
                          className={`inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-semibold transition ${
                            isBattleSelected
                              ? 'bg-amber-500 text-white shadow-sm'
                              : 'border border-amber-200 bg-amber-50/70 text-amber-800 hover:bg-amber-100'
                          }`}
                        >
                          <Swords className="h-3 w-3" /> {isBattleSelected ? 'Ready' : '⚔️ Battle'}
                        </button>

                        {/* 6. Why NOT Button — ONLY rendered for necessary products */}
                        {hasTradeoffs && (
                          <button
                            type="button"
                            onClick={() => handleWhyNot(product)}
                            className="rounded-full border border-red-200 bg-red-50/70 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-100 transition"
                          >
                            Tradeoffs / Why NOT?
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </article>
              )
            })}

            {/* ── Rich "You May Also Like" Section (Full Interactive Product Cards) ── */}
            {youMayLikeItems.length > 0 && (
              <div className="mt-8 rounded-3xl border border-violet-200 bg-gradient-to-br from-violet-50/60 via-indigo-50/40 to-white p-5 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-violet-600">
                      Smart AI Suggestions
                    </span>
                    <h2 className="text-lg font-black text-slate-900 mt-0.5">You May Also Like</h2>
                    <p className="text-xs text-slate-500">
                      Curated upgrade options and companion accessories tailored to your query.
                    </p>
                  </div>
                  <Sparkles className="h-6 w-6 text-violet-500" />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  {youMayLikeItems.map(item => (
                    <div
                      key={item.product_id}
                      className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm hover:shadow-md transition flex flex-col justify-between"
                    >
                      <div>
                        {item.badge && (
                          <div className="mb-2">
                            <span className="inline-block rounded-full bg-violet-100 px-2.5 py-0.5 text-[10px] font-bold text-violet-800">
                              {item.badge}
                            </span>
                          </div>
                        )}
                        <div className="flex gap-3">
                          <img
                            src={item.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=300&q=80'}
                            alt={item.name}
                            className="h-20 w-20 rounded-xl object-cover flex-shrink-0 bg-slate-100"
                          />
                          <div className="min-w-0 flex-1">
                            <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                              {item.category}
                            </span>
                            <h4 className="text-xs font-bold text-slate-900 leading-snug line-clamp-1">{item.name}</h4>
                            <p className="text-sm font-black text-slate-900 mt-1">
                              ₹{Number(item.price)?.toLocaleString('en-IN')}
                            </p>
                            <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-2">
                              {item.reason || item.description}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Full Actions on You May Also Like */}
                      <div className="mt-3 flex flex-wrap gap-1.5 pt-2 border-t border-slate-100">
                        <button
                          type="button"
                          onClick={() => addToCart(item, 1)}
                          className="flex-1 inline-flex items-center justify-center gap-1 rounded-xl bg-slate-900 py-1.5 text-xs font-bold text-white hover:bg-slate-800 transition"
                        >
                          <ShoppingBag className="h-3 w-3" /> Add to Cart
                        </button>
                        <button
                          type="button"
                          onClick={() => setModalProduct(item)}
                          className="rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          Details
                        </button>
                        <button
                          type="button"
                          onClick={() => handleCompare(item.product_id)}
                          className="rounded-xl border border-violet-200 bg-violet-50 px-2.5 py-1.5 text-xs font-semibold text-violet-700 hover:bg-violet-100"
                        >
                          + Compare
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSave(item.product_id)}
                          className="rounded-xl border border-emerald-200 bg-emerald-50 px-2.5 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                        >
                          💾 Save
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ── Sidebar ── */}
        <aside className="space-y-5">
          {/* Decision snapshot */}
          <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">AI Context</p>
                <h2 className="mt-0.5 text-base font-bold text-slate-900">Decision Snapshot</h2>
              </div>
              <TrendingUp className="h-6 w-6 text-violet-500" />
            </div>
            <div className="space-y-2 text-xs">
              {[
                ['Category', meta.constraints?.category || meta.decision_snapshot?.category || 'All'],
                ['Budget', meta.constraints?.max_budget ? `₹${Number(meta.constraints.max_budget).toLocaleString('en-IN')}` : 'Flexible'],
                ['Subcategory', meta.constraints?.subcategory || 'Automatic'],
                ['Confidence', Number(meta.confidence || 0.85) >= 0.7 ? 'High Precision' : 'Exploratory'],
              ].map(([label, val]) => (
                <div key={label} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2">
                  <span className="text-slate-500">{label}</span>
                  <span className="font-bold text-slate-900">{val}</span>
                </div>
              ))}
              {(meta.constraints?.tags || []).length > 0 && (
                <div className="rounded-xl bg-slate-50 px-3 py-2">
                  <p className="text-[10px] font-bold text-slate-400 mb-1.5 uppercase tracking-wider">Filtered Tags</p>
                  <div className="flex flex-wrap gap-1">
                    {(meta.constraints.tags || []).map(t => (
                      <span key={t} className="rounded-full bg-violet-100 px-2.5 py-0.5 text-[10px] font-bold text-violet-700">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Compare Tray */}
          {selectedCompare.length > 0 && (
            <div className="rounded-3xl border border-violet-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Compare Tray</h2>
                <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-bold text-violet-700">
                  {selectedCompare.length}
                </span>
              </div>
              <div className="space-y-2">
                {selectedCompare.map(e => (
                  <div key={e.product_id} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-xs">
                    <span className="text-slate-800 font-semibold truncate">{e.name || e.product_id}</span>
                    <button
                      type="button"
                      onClick={() => setSelectedCompare(prev => prev.filter(x => (typeof x === 'string' ? x : x.product_id) !== e.product_id))}
                      className="ml-2 text-slate-400 hover:text-red-500 flex-shrink-0"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))}
              </div>
              <a
                href="/compare"
                className="mt-3 flex w-full items-center justify-center gap-1 rounded-2xl bg-violet-600 py-2.5 text-xs font-bold text-white hover:bg-violet-700 transition shadow-sm"
              >
                <Sparkles className="h-3.5 w-3.5" /> View Side-by-Side Comparison →
              </a>
            </div>
          )}

          {/* Saved Shortlist */}
          <div className="rounded-3xl border border-slate-200/80 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Shortlist</p>
                <h2 className="mt-0.5 text-base font-bold text-slate-900">Saved Products</h2>
              </div>
              <Save className="h-5 w-5 text-emerald-600" />
            </div>
            {savedProducts.length === 0 ? (
              <p className="text-xs text-slate-400">No saved products yet. Tap 💾 Save on any item.</p>
            ) : (
              <div className="space-y-2">
                {savedProducts.slice(0, 5).map(pid => (
                  <div key={pid} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-700">
                    <span className="truncate font-semibold">{pid}</span>
                    <ArrowUpRight className="h-3.5 w-3.5 text-slate-400 flex-shrink-0" />
                  </div>
                ))}
                <a href="/saved" className="block text-center text-xs text-violet-600 font-bold hover:underline pt-1">
                  View all {savedProducts.length} saved products →
                </a>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
