import { useEffect, useMemo, useState } from 'react'
import {
  ArrowUpRight,
  MessageSquareText,
  Save,
  Search,
  ShieldCheck,
  Sparkles,
  Star,
  TrendingUp,
  X,
} from 'lucide-react'
import { api } from '../services/api'

const starterPrompts = [
  'Find comfortable walking shoes under ₹3,000.',
  'Gift for my dad who enjoys hiking.',
  'Compare lightweight laptops for college.',
]

// ─── Product Detail Modal ────────────────────────────────────────────────────
function ProductModal({ product, onClose }) {
  if (!product) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="relative max-w-lg w-full rounded-2xl bg-white p-6 shadow-xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-slate-400 hover:text-slate-700"
        >
          <X className="h-5 w-5" />
        </button>
        <img
          src={
            product.image ||
            'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'
          }
          alt={product.name}
          className="h-48 w-full rounded-xl object-cover mb-4"
        />
        <p className="text-xs uppercase tracking-widest text-slate-500">{product.category}</p>
        <h2 className="mt-1 text-xl font-bold text-slate-900">{product.name}</h2>
        <p className="text-sm text-slate-500 mb-3">
          {product.brand} · ₹{product.price}
        </p>
        <p className="text-sm text-slate-700 mb-3 leading-6">{product.explanation}</p>
        {(product.unmet_constraints || []).length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {product.unmet_constraints.map((c) => (
              <span
                key={c}
                className="rounded-full bg-red-50 px-2 py-1 text-xs text-red-700"
              >
                ⚠ {c}
              </span>
            ))}
          </div>
        )}
        {product.match_summary && Object.keys(product.match_summary).length > 0 && (
          <div className="mt-3 space-y-1">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
              Score breakdown
            </p>
            {Object.entries(product.match_summary).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between text-xs text-slate-600">
                <span>{k.replace(/_/g, ' ')}</span>
                <span className="font-semibold text-violet-700">{v}</span>
              </div>
            ))}
          </div>
        )}
        <button
          onClick={onClose}
          className="mt-4 rounded-full bg-slate-900 px-4 py-2 text-sm text-white"
        >
          Close
        </button>
      </div>
    </div>
  )
}

// ─── Why NOT Modal ───────────────────────────────────────────────────────────
function WhyNotModal({ data, onClose }) {
  if (!data) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="relative max-w-md w-full rounded-2xl bg-white p-6 shadow-xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-1 text-slate-400 hover:text-slate-700"
        >
          <X className="h-5 w-5" />
        </button>
        <h2 className="text-lg font-bold text-slate-900 mb-1">
          Why not {data.name}?
        </h2>
        <p className="text-sm text-slate-500 mb-4">{data.message}</p>

        {data.hard_constraint_failures?.length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-semibold text-red-600 uppercase tracking-wide mb-1">
              Constraint failures
            </p>
            <ul className="list-disc pl-4 space-y-1 text-sm text-slate-700">
              {data.hard_constraint_failures.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </div>
        )}

        {data.feature_gaps?.length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-1">
              Feature gaps
            </p>
            <ul className="list-disc pl-4 space-y-1 text-sm text-slate-700">
              {data.feature_gaps.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-3 flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm">
          <span className="text-slate-600">Fit score</span>
          <span className="font-semibold text-slate-900">{data.matched_score ?? '—'}</span>
        </div>

        <button
          onClick={onClose}
          className="mt-4 rounded-full bg-slate-900 px-4 py-2 text-sm text-white"
        >
          Close
        </button>
      </div>
    </div>
  )
}

// ─── Main Discover Page ──────────────────────────────────────────────────────
export default function Discover({
  userId,
  selectedCompare,
  setSelectedCompare,
  savedProducts,
  setSavedProducts,
}) {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Hi! Tell me what you are shopping for and I will narrow it down with a recommendation score.',
    },
  ])
  const [input, setInput] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [meta, setMeta] = useState({})

  // Clarification state
  const [clarificationQ, setClarificationQ] = useState('')
  const [clarificationInput, setClarificationInput] = useState('')

  // Modal state
  const [modalProduct, setModalProduct] = useState(null)
  const [whyModal, setWhyModal] = useState(null)

  // Seed initial decision snapshot
  useEffect(() => {
    const timer = setTimeout(() => {
      setMeta({
        intent: { purchase_intent: 'self_use' },
        constraints: { category: 'footwear', max_budget: 3000 },
        confidence: 0.83,
      })
    }, 150)
    return () => clearTimeout(timer)
  }, [])

  const handlePrompt = async (prompt) => {
    setInput(prompt)
    if (prompt.trim()) await handleSubmit(prompt)
  }

  const handleSubmit = async (messageOverride) => {
    const message = (messageOverride ?? input).trim()
    if (!message || loading) return

    setLoading(true)
    setError('')
    setMessages((prev) => [...prev, { role: 'user', content: message }])

    try {
      const payload = {
        user_id: userId,
        message,
        ...(sessionId ? { session_id: sessionId } : {}),
      }
      const response = await api.chat(payload)

      // Track session_id across turns
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id)
      }

      setMeta(response)

      if (response.response_type === 'clarification' && response.clarification_question) {
        // Show clarification banner instead of products
        setClarificationQ(response.clarification_question)
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: response.assistant_response || response.clarification_question },
        ])
      } else {
        setClarificationQ('')
        setResults(response.recommendations || [])
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: response.assistant_response || 'Here are my top picks.',
          },
        ])
      }

      if (response.response_type !== 'clarification' && response.clarification_question) {
        setError(response.clarification_question)
      }
    } catch (err) {
      setError(err.message || 'Something went wrong while searching.')
    } finally {
      setLoading(false)
      setInput('')
    }
  }

  const handleNewConversation = async () => {
    if (sessionId) {
      try {
        await api.deleteSession(sessionId)
      } catch {
        // session may already be gone
      }
    }
    setSessionId(null)
    setMessages([
      {
        role: 'assistant',
        content:
          'Hi! Tell me what you are shopping for and I will narrow it down with a recommendation score.',
      },
    ])
    setResults([])
    setMeta({})
    setClarificationQ('')
    setClarificationInput('')
    setError('')
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
    const product = results.find((r) => r.product_id === productId)
    setSelectedCompare((prev) => {
      const already = prev.find((e) => e.product_id === productId)
      if (already) return prev
      return [
        ...prev,
        {
          product_id: productId,
          fit_score: product?.fit_score,
          match_summary: product?.match_summary,
        },
      ].slice(-3)
    })
  }

  const handleWhyNot = async (product) => {
    try {
      const lastMsg =
        [...messages].reverse().find((m) => m.role === 'user')?.content || ''
      const data = await api.whyNot(product.product_id, lastMsg, sessionId)
      setWhyModal(data)
    } catch {
      setError('Unable to fetch why-not explanation right now.')
    }
  }

  const scoreLabel = useMemo(() => {
    if (!meta?.confidence) return 'High confidence'
    return Number(meta.confidence) >= 0.65 ? 'High confidence' : 'Needs clarification'
  }, [meta])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Modals */}
      <ProductModal product={modalProduct} onClose={() => setModalProduct(null)} />
      <WhyNotModal data={whyModal} onClose={() => setWhyModal(null)} />

      <div className="grid gap-6 xl:grid-cols-[1.6fr_0.8fr]">
        {/* ── Chat + Results panel ── */}
        <section className="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
                Discovery workspace
              </p>
              <h1 className="mt-2 text-2xl font-bold text-slate-900">Ask ShopSense</h1>
            </div>
            <button
              type="button"
              onClick={handleNewConversation}
              className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
            >
              New conversation
            </button>
          </div>

          {/* Starter prompts */}
          <div className="mb-5 flex flex-wrap gap-2">
            {starterPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => handlePrompt(prompt)}
                className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1.5 text-xs font-medium text-violet-700 transition hover:border-violet-300 hover:bg-violet-100"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Chat window */}
          <div className="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                    message.role === 'user'
                      ? 'bg-slate-900 text-white'
                      : 'bg-white text-slate-700 ring-1 ring-slate-200'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <MessageSquareText className="h-4 w-4 animate-pulse" />
                ShopSense is comparing products...
              </div>
            )}
          </div>

          {/* Clarification banner */}
          {clarificationQ && (
            <div className="mt-4 rounded-xl border border-violet-200 bg-violet-50 px-4 py-3">
              <p className="text-sm font-medium text-violet-800">{clarificationQ}</p>
              <div className="mt-2 flex gap-2">
                <input
                  value={clarificationInput}
                  onChange={(e) => setClarificationInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && clarificationInput.trim()) {
                      handleSubmit(clarificationInput)
                      setClarificationInput('')
                    }
                  }}
                  placeholder="Your answer..."
                  className="flex-1 rounded-lg border border-violet-200 bg-white px-3 py-1.5 text-sm outline-none focus:border-violet-400"
                />
                <button
                  type="button"
                  onClick={() => {
                    if (clarificationInput.trim()) {
                      handleSubmit(clarificationInput)
                      setClarificationInput('')
                    }
                  }}
                  className="rounded-lg bg-violet-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-violet-700"
                >
                  Answer
                </button>
              </div>
            </div>
          )}

          {/* Error banner */}
          {error && !clarificationQ && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700">
              {error}
            </div>
          )}

          {/* Chat input */}
          <div className="mt-5 flex gap-3 rounded-2xl border border-slate-200 bg-white p-2">
            <div className="flex flex-1 items-center gap-2 rounded-xl bg-slate-50 px-3 py-2">
              <Search className="h-4 w-4 text-slate-400" />
              <textarea
                rows={2}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit()
                  }
                }}
                placeholder="Describe what you want to buy..."
                className="min-h-[56px] w-full resize-none border-0 bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
              />
            </div>
            <button
              type="button"
              onClick={() => handleSubmit()}
              className="rounded-xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-700"
            >
              Send
            </button>
          </div>

          {/* Results */}
          <div className="mt-6 space-y-5">
            {results.length === 0 && !loading && (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
                No recommendations yet. Try a sample prompt above.
              </div>
            )}

            {results.map((product) => (
              <article
                key={product.product_id}
                className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
              >
                <div className="grid gap-5 p-4 md:grid-cols-[180px_1fr]">
                  <img
                    src={
                      product.image ||
                      'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'
                    }
                    alt={product.name}
                    className="h-40 w-full rounded-2xl object-cover"
                  />
                  <div>
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                          {product.category}
                        </p>
                        <h3 className="mt-1 text-xl font-bold text-slate-900">{product.name}</h3>
                        <p className="text-sm text-slate-500">{product.brand}</p>
                      </div>
                      {/* Fit score badge */}
                      <div className="rounded-full bg-violet-50 px-3 py-1 text-sm font-semibold text-violet-700 whitespace-nowrap">
                        {typeof product.fit_score === 'number'
                          ? product.fit_score.toFixed(2)
                          : '—'}{' '}
                        fit
                      </div>
                    </div>

                    <div className="mt-4 flex flex-wrap items-center gap-3 text-sm text-slate-600">
                      <span className="font-semibold text-slate-900">₹{product.price}</span>
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-1 text-emerald-700">
                        <ShieldCheck className="h-3.5 w-3.5" />
                        {product.stock_status || 'in_stock'}
                      </span>
                      <span className="inline-flex items-center gap-1 text-amber-600">
                        <Star className="h-3.5 w-3.5 fill-current" />
                        {typeof product.match_summary?.rating_signal === 'number'
                          ? (product.match_summary.rating_signal / 20).toFixed(1)
                          : '4.5'}
                      </span>
                    </div>

                    <p className="mt-4 text-sm leading-6 text-slate-600">{product.explanation}</p>

                    {/* Unmet constraints */}
                    {(product.unmet_constraints || []).length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {product.unmet_constraints.map((c) => (
                          <span
                            key={c}
                            className="rounded-full bg-red-50 px-2 py-0.5 text-xs text-red-700"
                          >
                            ⚠ {c}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Action buttons */}
                    <div className="mt-4 flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => setModalProduct(product)}
                        className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700"
                      >
                        View details
                      </button>
                      <button
                        type="button"
                        onClick={() => handleCompare(product.product_id)}
                        className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700"
                      >
                        Compare
                      </button>
                      <button
                        type="button"
                        onClick={() => handleSave(product.product_id)}
                        className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700"
                      >
                        Save
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          alert(product.explanation || 'No explanation available.')
                        }
                        className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700"
                      >
                        Why this product?
                      </button>
                      <button
                        type="button"
                        onClick={() => handleWhyNot(product)}
                        className="rounded-full border border-red-100 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 transition hover:bg-red-100"
                      >
                        Why NOT?
                      </button>
                    </div>
                  </div>
                </div>
              </article>
            ))}

            {/* Fallback diff-view */}
            {meta?.fallback_details?.fallback_triggered && (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm">
                <p className="font-semibold text-amber-800">
                  No exact match — here&apos;s what changed:
                </p>
                <div className="mt-2 grid grid-cols-2 gap-3">
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-xs font-semibold text-slate-500 mb-1">Original</p>
                    <pre className="text-xs text-slate-700 whitespace-pre-wrap overflow-auto max-h-32">
                      {JSON.stringify(
                        meta.fallback_details.original_constraints,
                        null,
                        2,
                      )}
                    </pre>
                  </div>
                  <div className="rounded-xl bg-white p-3">
                    <p className="text-xs font-semibold text-amber-600 mb-1">Relaxed ↓</p>
                    <pre className="text-xs text-slate-700 whitespace-pre-wrap overflow-auto max-h-32">
                      {JSON.stringify(
                        meta.fallback_details.relaxed_constraints,
                        null,
                        2,
                      )}
                    </pre>
                  </div>
                </div>
                <p className="mt-2 text-amber-700">
                  {meta.fallback_details.trade_off_explanation}
                </p>
              </div>
            )}

            {/* Complementary product */}
            {meta?.complementary_product && (
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">
                  You might also like
                </p>
                <div className="flex items-center gap-4">
                  {meta.complementary_product.image && (
                    <img
                      src={meta.complementary_product.image}
                      alt={meta.complementary_product.name}
                      className="h-16 w-16 rounded-xl object-cover flex-shrink-0"
                    />
                  )}
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 truncate">
                      {meta.complementary_product.name}
                    </p>
                    <p className="text-sm text-slate-500">
                      ₹{meta.complementary_product.price}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {meta.complementary_product.reason}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ── Sidebar ── */}
        <aside className="space-y-6">
          {/* Decision snapshot */}
          <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Context
                </p>
                <h2 className="mt-2 text-xl font-bold text-slate-900">Decision snapshot</h2>
              </div>
              <TrendingUp className="h-8 w-8 text-violet-600" />
            </div>
            <div className="mt-5 space-y-4 text-sm text-slate-600">
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Intent</span>
                <span className="font-medium text-slate-900">
                  {meta.intent?.purchase_intent || meta.intent?.intent_type || 'self_use'}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Budget</span>
                <span className="font-medium text-slate-900">
                  {meta.constraints?.max_budget
                    ? `₹${meta.constraints.max_budget}`
                    : meta.decision_snapshot?.max_budget
                      ? `₹${meta.decision_snapshot.max_budget}`
                      : '—'}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Category</span>
                <span className="font-medium text-slate-900">
                  {meta.constraints?.category ||
                    meta.decision_snapshot?.category ||
                    'all'}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Confidence</span>
                <span className="font-medium text-slate-900">{scoreLabel}</span>
              </div>
              {meta.decision_snapshot?.turn_number && (
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Turn</span>
                  <span className="font-medium text-slate-900">
                    #{meta.decision_snapshot.turn_number}
                  </span>
                </div>
              )}
              {(meta.constraints?.tags || meta.decision_snapshot?.tags || []).length > 0 && (
                <div className="rounded-xl bg-slate-50 p-3">
                  <p className="text-xs text-slate-500 mb-1">Tags</p>
                  <div className="flex flex-wrap gap-1">
                    {(meta.constraints?.tags || meta.decision_snapshot?.tags || []).map(
                      (tag) => (
                        <span
                          key={tag}
                          className="rounded-full bg-violet-100 px-2 py-0.5 text-xs text-violet-700"
                        >
                          {tag}
                        </span>
                      ),
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Saved shortlist */}
          <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Saved
                </p>
                <h2 className="mt-2 text-xl font-bold text-slate-900">Your shortlist</h2>
              </div>
              <Save className="h-8 w-8 text-violet-600" />
            </div>
            <div className="mt-4 space-y-3">
              {savedProducts.length === 0 ? (
                <p className="text-sm text-slate-500">No saved products yet.</p>
              ) : (
                savedProducts.map((productId) => (
                  <div
                    key={productId}
                    className="flex items-center justify-between rounded-xl bg-slate-50 p-3 text-sm text-slate-700"
                  >
                    <span className="truncate">{productId}</span>
                    <ArrowUpRight className="h-4 w-4 text-slate-400 flex-shrink-0" />
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
