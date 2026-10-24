import { useEffect, useMemo, useState } from 'react'
import { ArrowUpRight, MessageSquareText, Save, Search, ShieldCheck, Sparkles, Star, TrendingUp } from 'lucide-react'
import { api } from '../services/api'

const starterPrompts = [
  'Find comfortable walking shoes under ₹3,000.',
  'Gift for my dad who enjoys hiking.',
  'Compare lightweight laptops for college.',
]

export default function Discover({ userId, selectedCompare, setSelectedCompare, savedProducts, setSavedProducts }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! Tell me what you are shopping for and I will narrow it down with a recommendation score.',
    },
  ])
  const [input, setInput] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [meta, setMeta] = useState({})

  useEffect(() => {
    const timer = setTimeout(() => {
      setMeta({
        intent: 'self_use',
        category: 'footwear',
        budget: '₹3,000',
        confidence: '0.83',
      })
    }, 150)
    return () => clearTimeout(timer)
  }, [])

  const handlePrompt = async (prompt) => {
    setInput(prompt)
    if (prompt.trim()) {
      await handleSubmit(prompt)
    }
  }

  const handleSubmit = async (messageOverride) => {
    const message = (messageOverride ?? input).trim()
    if (!message || loading) return

    setLoading(true)
    setError('')
    setMessages((prev) => [...prev, { role: 'user', content: message }])

    try {
      const payload = { user_id: userId, message }
      const response = await api.chat(payload)
      setResults(response.recommendations || [])
      setMeta(response)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.assistant_response || 'Here are my top picks.',
        },
      ])
      if (response.clarification_question) {
        setError(response.clarification_question)
      }
    } catch (err) {
      setError(err.message || 'Something went wrong while searching.')
    } finally {
      setLoading(false)
      setInput('')
    }
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
    setSelectedCompare((prev) => {
      const next = prev.includes(productId) ? prev : [...prev, productId].slice(-3)
      return next
    })
  }

  const scoreLabel = useMemo(() => {
    if (!meta?.confidence) return 'High confidence'
    return Number(meta.confidence) >= 0.65 ? 'High confidence' : 'Needs clarification'
  }, [meta])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="grid gap-6 xl:grid-cols-[1.6fr_0.8fr]">
        <section className="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">Discovery workspace</p>
              <h1 className="mt-2 text-2xl font-bold text-slate-900">Ask ShopSense</h1>
            </div>
            <button className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm font-medium text-slate-700">
              New conversation
            </button>
          </div>

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

          <div className="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            {messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
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

          {error && (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700">
              {error}
            </div>
          )}

          <div className="mt-5 flex gap-3 rounded-2xl border border-slate-200 bg-white p-2">
            <div className="flex flex-1 items-center gap-2 rounded-xl bg-slate-50 px-3 py-2">
              <Search className="h-4 w-4 text-slate-400" />
              <textarea
                rows={2}
                value={input}
                onChange={(event) => setInput(event.target.value)}
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

          <div className="mt-6 space-y-5">
            {results.length === 0 && !loading ? (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
                No recommendations yet. Try a sample prompt above.
              </div>
            ) : null}

            {results.map((product) => (
              <article key={product.product_id} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
                <div className="grid gap-5 p-4 md:grid-cols-[180px_1fr]">
                  <img
                    src={product.image || 'https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=900&q=80'}
                    alt={product.name}
                    className="h-40 w-full rounded-2xl object-cover"
                  />
                  <div>
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{product.category}</p>
                        <h3 className="mt-1 text-xl font-bold text-slate-900">{product.name}</h3>
                        <p className="text-sm text-slate-500">{product.brand}</p>
                      </div>
                      <div className="rounded-full bg-violet-50 px-3 py-1 text-sm font-semibold text-violet-700">
                        {product.fit_score || 0} fit score
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
                        {product.match_summary?.rating_signal ?? 4.5}
                      </span>
                    </div>

                    <p className="mt-4 text-sm leading-6 text-slate-600">{product.explanation}</p>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {['View details', 'Compare', 'Save', 'Why this product?'].map((label) => (
                        <button
                          key={label}
                          type="button"
                          onClick={() => {
                            if (label === 'Save') handleSave(product.product_id)
                            if (label === 'Compare') handleCompare(product.product_id)
                          }}
                          className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-700"
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="space-y-6">
          <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Context</p>
                <h2 className="mt-2 text-xl font-bold text-slate-900">Decision snapshot</h2>
              </div>
              <TrendingUp className="h-8 w-8 text-violet-600" />
            </div>
            <div className="mt-5 space-y-4 text-sm text-slate-600">
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Intent</span>
                <span className="font-medium text-slate-900">{meta.intent?.purchase_intent || 'self_use'}</span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Budget</span>
                <span className="font-medium text-slate-900">{meta.constraints?.max_budget ? `₹${meta.constraints.max_budget}` : '₹3,000'}</span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Category</span>
                <span className="font-medium text-slate-900">{meta.constraints?.category || 'footwear'}</span>
              </div>
              <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                <span>Confidence</span>
                <span className="font-medium text-slate-900">{scoreLabel}</span>
              </div>
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Saved</p>
                <h2 className="mt-2 text-xl font-bold text-slate-900">Your shortlist</h2>
              </div>
              <Save className="h-8 w-8 text-violet-600" />
            </div>
            <div className="mt-4 space-y-3">
              {savedProducts.length === 0 ? (
                <p className="text-sm text-slate-500">No saved products yet.</p>
              ) : (
                savedProducts.map((productId) => (
                  <div key={productId} className="flex items-center justify-between rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                    <span>{productId}</span>
                    <ArrowUpRight className="h-4 w-4 text-slate-400" />
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
